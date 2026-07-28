"""Stage 1 search tests, including the resumability guarantees.

The interruption tests are the important ones: they simulate a machine dying
mid-study and assert that restarting neither loses completed work nor repeats
backtests. That claim is the whole reason this can run on a laptop.
"""

from __future__ import annotations

import math
from datetime import date
from pathlib import Path

import pandas as pd
import pytest
import yaml

from engine.config import load_search_space, load_study
from engine.metrics import compute
from engine.optimise import (
    REJECTED, Stage1Search, check_constraints, plateau_prescreen, storage_url,
    trial_records, write_stage1_output,
)
from engine.results import BacktestResult, Trade
from engine.runner import ResultCache, Runner
from tests.test_config import VALID_SPACE, VALID_STUDY, write


class ScriptedCli:
    """Returns a result whose profitability depends on a parameter.

    'Take Profit R' near 2.0 is good; far from it is poor. That gives the
    optimiser a real optimum to find and a plateau around it.
    """

    def __init__(self, trades_per_run=60, fail_when=None):
        self.calls = 0
        self.trades_per_run = trades_per_run
        self.fail_when = fail_when
        self.seen_params = []

    def run_backtest(self, request, workdir, nominal_balance):
        self.calls += 1
        params = request.parameters or {}
        self.seen_params.append(params)

        if self.fail_when and self.fail_when(params):
            return BacktestResult(
                trades=[], equity_curve=pd.Series(dtype="float64"), summary={},
                equity_source="none", failed=True, failure_excerpt="bot threw",
            )

        tp = float(params.get("Take Profit R", 2.0))
        edge = max(0.0, 1.0 - abs(tp - 2.0))       # peak at 2.0
        trades, equity, running = [], [], 10000.0
        times, values = [pd.Timestamp("2024-01-01", tz="UTC")], [running]
        for i in range(self.trades_per_run):
            pnl = 120.0 * edge if i % 3 else -80.0
            t = pd.Timestamp("2024-01-01", tz="UTC") + pd.Timedelta(days=i * 3)
            trades.append(Trade(
                position_id=str(i), symbol="XAUUSD", direction="buy",
                open_time=t, close_time=t + pd.Timedelta(hours=6),
                entry_price=2000.0, exit_price=2010.0, volume=1.0,
                gross_pnl=pnl, net_pnl=pnl, pips=10.0,
            ))
            running += pnl
            times.append(t + pd.Timedelta(hours=6))
            values.append(running)
        equity = pd.Series(values, index=pd.DatetimeIndex(times), dtype="float64")
        return BacktestResult(trades=trades, equity_curve=equity, summary={},
                              equity_source="marks")


@pytest.fixture
def setup(tmp_path):
    cfg_path = write(tmp_path, {**VALID_STUDY, "gates": {"min_trades_per_year": 1}})
    space_path = write(tmp_path, VALID_SPACE, "search_space.yaml")
    return load_study(cfg_path), load_search_space(space_path)


def make_search(tmp_path, cfg, space, cli, workers=1) -> Stage1Search:
    runner = Runner(
        cli=cli, cache=ResultCache(tmp_path / "cache"), algo=tmp_path / "b.algo",
        algo_hash="a1", data_hash="d1", symbol="XAUUSD", period="D1",
        balance=10000.0, commission_per_million=0.0,
        workdir_root=tmp_path / "work", workers=workers,
    )
    return Stage1Search(
        study_cfg=cfg, space=space, runner=runner, csv=tmp_path / "insample.csv",
        start=date(2021, 7, 18), end=date(2025, 7, 1), seed=7,
    )


class TestConstraints:
    def _metrics(self, pnl, trades_per_year=50, dd_pct=5.0):
        equity = pd.Series(
            [10000.0, 10500.0, 10200.0],
            index=pd.to_datetime(["2024-01-01", "2024-06-01", "2024-12-01"], utc=True),
        )
        return compute(pd.Series(pnl), equity, 10000, 100)

    def test_zero_trades_is_rejected(self, setup):
        cfg, _ = setup
        m = compute(pd.Series([], dtype="float64"), pd.Series(dtype="float64"), 10000, 100)
        assert "no trades" in check_constraints(m, cfg.gates, 1.0)

    def test_low_profit_factor_is_rejected(self, setup):
        cfg, _ = setup
        m = self._metrics([100.0, -200.0, 50.0])
        assert "profit factor" in check_constraints(m, cfg.gates, 1.0)


class TestSearch:
    def test_runs_the_full_budget(self, tmp_path, setup):
        cfg, space = setup
        cli = ScriptedCli()
        search = make_search(tmp_path, cfg, space, cli)
        study = search.run(tmp_path / "trials.db", n_random=4, n_tpe=4)
        assert len([t for t in study.trials]) == 8

    def test_finds_the_optimum_region(self, tmp_path, setup):
        cfg, space = setup
        search = make_search(tmp_path, cfg, space, ScriptedCli())
        study = search.run(tmp_path / "trials.db", n_random=10, n_tpe=20)
        best = study.best_trial
        # The scripted edge peaks at Take Profit R = 2.0.
        assert abs(best.params["Take Profit R"] - 2.0) <= 0.75

    def test_every_trial_is_logged_for_dsr(self, tmp_path, setup):
        cfg, space = setup
        search = make_search(tmp_path, cfg, space, ScriptedCli())
        study = search.run(tmp_path / "trials.db", n_random=5, n_tpe=5)
        records = trial_records(study)
        assert len(records) == 10
        assert all(r.metrics for r in records if not r.rejected_reason)

    def test_failed_backtests_are_pruned_not_scored(self, tmp_path, setup):
        cfg, space = setup
        cli = ScriptedCli(fail_when=lambda p: float(p.get("Take Profit R", 0)) > 3.0)
        search = make_search(tmp_path, cfg, space, cli)
        study = search.run(tmp_path / "trials.db", n_random=15, n_tpe=0)
        pruned = [t for t in study.trials if t.user_attrs.get("failed")]
        # A crashed bot must never look like a zero-Sharpe parameter set.
        assert all(t.value is None for t in pruned)


class TestResumability:
    """The claim that a killed machine loses nothing."""

    def test_resume_does_not_repeat_completed_backtests(self, tmp_path, setup):
        cfg, space = setup
        db = tmp_path / "trials.db"

        cli1 = ScriptedCli()
        make_search(tmp_path, cfg, space, cli1).run(db, n_random=6, n_tpe=0)
        first_calls = cli1.calls

        # Simulate a crash and restart: same cache, same storage, new process.
        cli2 = ScriptedCli()
        study = make_search(tmp_path, cfg, space, cli2).run(db, n_random=6, n_tpe=6)

        assert first_calls == 6
        # The 6 completed trials are not re-run; only the outstanding 6 are.
        assert cli2.calls <= 6
        assert len(study.trials) == 12

    def test_rerunning_a_finished_study_is_a_noop(self, tmp_path, setup):
        cfg, space = setup
        db = tmp_path / "trials.db"
        make_search(tmp_path, cfg, space, ScriptedCli()).run(db, n_random=4, n_tpe=0)

        cli = ScriptedCli()
        make_search(tmp_path, cfg, space, cli).run(db, n_random=4, n_tpe=0)
        assert cli.calls == 0

    def test_cache_alone_prevents_repeat_work_across_studies(self, tmp_path, setup):
        cfg, space = setup
        cli1 = ScriptedCli()
        make_search(tmp_path, cfg, space, cli1).run(tmp_path / "a.db", n_random=8, n_tpe=0)

        # A brand new study, same parameters explored: the cache still serves.
        cli2 = ScriptedCli()
        make_search(tmp_path, cfg, space, cli2).run(tmp_path / "b.db", n_random=8, n_tpe=0)
        assert cli2.calls < cli1.calls

    def test_wal_mode_is_enabled(self, tmp_path, setup):
        import sqlite3
        cfg, space = setup
        db = tmp_path / "trials.db"
        make_search(tmp_path, cfg, space, ScriptedCli()).run(db, n_random=2, n_tpe=0)
        con = sqlite3.connect(db)
        mode = con.execute("PRAGMA journal_mode").fetchone()[0]
        con.close()
        assert mode.lower() == "wal"

    def test_storage_url_is_sqlite_with_timeout(self, tmp_path):
        assert storage_url(tmp_path / "x.db").startswith("sqlite:///")
        assert "timeout=60" in storage_url(tmp_path / "x.db")


class TestBranchSampling:
    """The sampler must never suggest a parameter that is not in play."""

    @pytest.fixture
    def branched(self, tmp_path):
        cfg = {**VALID_SPACE, "search": {
            "Enable Multi TP": {"type": "bool"},
            "Take Profit R": {"type": "float", "low": 1, "high": 4,
                              "condition": "Enable Multi TP == false"},
            "TP1 R": {"type": "float", "low": 0.5, "high": 2,
                      "condition": "Enable Multi TP == true"},
            "TP2 R": {"type": "float", "low": 1.5, "high": 5,
                      "condition": "Enable Multi TP == true"},
        }}
        return load_search_space(write(tmp_path, cfg, "search_space.yaml"))

    def test_only_the_live_branch_is_sampled(self, branched):
        import optuna
        from engine.optimise import suggest
        optuna.logging.set_verbosity(optuna.logging.WARNING)
        study = optuna.create_study(sampler=optuna.samplers.RandomSampler(seed=3))

        saw_ladder = saw_single = False
        for _ in range(30):
            params = suggest(study.ask(), branched)
            if params["Enable Multi TP"]:
                saw_ladder = True
                assert "TP1 R" in params and "TP2 R" in params
                assert "Take Profit R" not in params
            else:
                saw_single = True
                assert "Take Profit R" in params
                assert "TP1 R" not in params and "TP2 R" not in params
        assert saw_ladder and saw_single, "both branches should be explored"

    def test_parent_is_sampled_before_its_dependants(self, tmp_path):
        # Declaration order puts the dependant first; the sampler must reorder,
        # or the condition would be evaluated against an unsampled parent.
        from engine.optimise import _condition_order
        cfg = {**VALID_SPACE, "search": {
            "Trend EMA Period": {"type": "int", "low": 5, "high": 50,
                                 "condition": "Enable Trend Filter"},
            "Enable Trend Filter": {"type": "bool"},
        }}
        space = load_search_space(write(tmp_path, cfg, "search_space.yaml"))
        order = _condition_order(space)
        assert order.index("Enable Trend Filter") < order.index("Trend EMA Period")


class TestPlateauPrescreen:
    def test_isolated_spike_is_demoted(self, tmp_path, setup):
        from engine.optimise import TrialRecord
        _, space = setup
        # A cluster of decent neighbours around 2.0, plus one lucky spike far away.
        records = [
            TrialRecord(i, {"Take Profit R": v, "Max Hold Bars": 5}, s, {})
            for i, (v, s) in enumerate([
                (1.9, 1.8), (2.0, 1.9), (2.1, 1.85), (2.05, 1.88), (1.95, 1.82),
                (3.9, 2.6),   # isolated spike: best raw score, no support
            ])
        ]
        top = plateau_prescreen(records, space, k=1)
        assert top[0].params["Take Profit R"] != 3.9

    def test_rejected_trials_are_excluded(self, tmp_path, setup):
        from engine.optimise import TrialRecord
        _, space = setup
        records = [
            TrialRecord(0, {"Take Profit R": 2.0}, REJECTED, {}, "profit factor 0.9 < 1.15"),
            TrialRecord(1, {"Take Profit R": 2.1}, 1.5, {}),
        ]
        assert [r.number for r in plateau_prescreen(records, space, k=5)] == [1]

    def test_empty_input(self, tmp_path, setup):
        _, space = setup
        assert plateau_prescreen([], space) == []


class TestOutput:
    def test_writes_summary_with_rejection_reasons(self, tmp_path, setup):
        import json
        from engine.optimise import TrialRecord
        _, space = setup
        records = [
            TrialRecord(0, {"a": 1}, 1.2, {"sharpe": 1.2}),
            TrialRecord(1, {"a": 2}, REJECTED, {}, "profit factor 0.90 < 1.15"),
        ]
        out = tmp_path / "stage1_top.json"
        write_stage1_output(records, [records[0]], out)
        payload = json.loads(out.read_text())
        assert payload["total_trials"] == 2
        assert payload["rejected"] == 1
        assert payload["rejection_reasons"]
