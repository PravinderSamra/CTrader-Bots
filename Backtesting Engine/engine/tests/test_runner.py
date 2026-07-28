"""Runner and cache tests (build-spec §16.1: cache key stability).

These run entirely against a stub backend — no credentials, no network, no
Docker. That is the point of the execution-layer abstraction.
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import pandas as pd
import pytest

from engine.ctcli import CtcliError, InfraError
from engine.results import BacktestResult, Trade
from engine.runner import ResultCache, RunSpec, Runner, throughput_report


def make_result(pnl=(100.0, -50.0)) -> BacktestResult:
    trades = [
        Trade(
            position_id=str(i), symbol="XAUUSD", direction="buy",
            open_time=pd.Timestamp("2024-01-01", tz="UTC") + pd.Timedelta(days=i),
            close_time=pd.Timestamp("2024-01-02", tz="UTC") + pd.Timedelta(days=i),
            entry_price=2000.0, exit_price=2010.0, volume=1.0,
            gross_pnl=p, net_pnl=p, pips=10.0,
        )
        for i, p in enumerate(pnl)
    ]
    equity = pd.Series(
        [10000.0, 10100.0, 10050.0],
        index=pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-03"], utc=True),
    )
    return BacktestResult(trades=trades, equity_curve=equity, summary={"net": 50},
                          equity_source="marks")


class StubCli:
    """Stands in for CtraderCli. Counts calls so cache behaviour is observable."""

    def __init__(self, result=None, raises=None, raise_times=0):
        self.calls = 0
        self.result = result or make_result()
        self.raises = raises
        self.raise_times = raise_times

    def run_backtest(self, request, workdir, nominal_balance):
        self.calls += 1
        if self.raises and self.calls <= self.raise_times:
            raise self.raises
        return self.result


def make_runner(tmp_path, cli, **kw) -> Runner:
    return Runner(
        cli=cli, cache=ResultCache(tmp_path / "cache"), algo=tmp_path / "bot.algo",
        algo_hash="algo123", data_hash="data456", symbol="XAUUSD", period="m5",
        balance=10000.0, commission_per_million=0.0,
        workdir_root=tmp_path / "work", run_log=tmp_path / "runs.jsonl",
        workers=2, **kw,
    )


def spec(**kw) -> RunSpec:
    base = dict(
        parameters={"Take Profit R": 2.0}, csv=Path("/data/insample.csv"),
        start=date(2024, 1, 1), end=date(2024, 6, 1), spread_pips=2.0,
    )
    base.update(kw)
    return RunSpec(**base)


class TestCacheKey:
    def test_identical_specs_share_a_key(self, tmp_path):
        r = make_runner(tmp_path, StubCli())
        assert r.key_for(spec()) == r.key_for(spec())

    def test_trial_id_does_not_affect_the_key(self, tmp_path):
        # Trial id is bookkeeping — it cannot change the backtest's result.
        r = make_runner(tmp_path, StubCli())
        assert r.key_for(spec(trial_id="a")) == r.key_for(spec(trial_id="b"))

    @pytest.mark.parametrize("change", [
        {"parameters": {"Take Profit R": 2.5}},
        {"start": date(2024, 2, 1)},
        {"end": date(2024, 7, 1)},
        {"spread_pips": 4.0},
    ])
    def test_every_result_affecting_field_changes_the_key(self, tmp_path, change):
        r = make_runner(tmp_path, StubCli())
        assert r.key_for(spec()) != r.key_for(spec(**change))

    def test_csv_path_alone_does_not_change_the_key(self, tmp_path):
        # Data identity is carried by data_hash, not the file path: the same
        # bars under a different filename must hit the same cache entry, and
        # different bars must miss it even at the same path.
        r = make_runner(tmp_path, StubCli())
        assert r.key_for(spec()) == r.key_for(spec(csv=Path("/elsewhere/same.csv")))

    def test_data_hash_changes_the_key(self, tmp_path):
        a = make_runner(tmp_path, StubCli())
        b = make_runner(tmp_path, StubCli())
        b.data_hash = "different"
        assert a.key_for(spec()) != b.key_for(spec())

    def test_algo_hash_changes_the_key(self, tmp_path):
        a = make_runner(tmp_path, StubCli())
        b = make_runner(tmp_path, StubCli())
        b.algo_hash = "recompiled"
        assert a.key_for(spec()) != b.key_for(spec())

    def test_int_and_float_spellings_agree(self, tmp_path):
        r = make_runner(tmp_path, StubCli())
        assert r.key_for(spec(parameters={"Max Hold Bars": 5})) == \
               r.key_for(spec(parameters={"Max Hold Bars": 5.0}))

    def test_parameter_order_does_not_matter(self, tmp_path):
        r = make_runner(tmp_path, StubCli())
        assert r.key_for(spec(parameters={"a": 1, "b": 2})) == \
               r.key_for(spec(parameters={"b": 2, "a": 1}))


class TestCaching:
    def test_second_identical_run_is_served_from_cache(self, tmp_path):
        cli = StubCli()
        r = make_runner(tmp_path, cli)
        first = r.run_one(spec())
        second = r.run_one(spec())
        assert cli.calls == 1
        assert not first.cache_hit and second.cache_hit
        assert len(second.result.trades) == 2

    def test_cache_survives_a_new_runner(self, tmp_path):
        cli = StubCli()
        make_runner(tmp_path, cli).run_one(spec())
        cli2 = StubCli()
        assert make_runner(tmp_path, cli2).run_one(spec()).cache_hit
        assert cli2.calls == 0

    def test_failed_runs_are_not_cached(self, tmp_path):
        cli = StubCli(raises=CtcliError("bot threw"), raise_times=99)
        r = make_runner(tmp_path, cli)
        first = r.run_one(spec())
        assert first.result.failed
        second = r.run_one(spec())
        assert not second.cache_hit          # retried, not remembered as a result
        assert cli.calls == 2

    def test_corrupt_cache_entry_is_discarded(self, tmp_path):
        cli = StubCli()
        r = make_runner(tmp_path, cli)
        r.run_one(spec())
        r.cache.path_for(r.key_for(spec())).write_text("{not json")
        assert not r.run_one(spec()).cache_hit


class TestFailureHandling:
    def test_bot_errors_are_recorded_not_scored_zero(self, tmp_path):
        r = make_runner(tmp_path, StubCli(raises=CtcliError("NullReference"), raise_times=99))
        out = r.run_one(spec())
        assert out.result.failed
        assert "NullReference" in out.result.failure_excerpt
        assert out.result.trades == []

    def test_bot_errors_are_not_retried(self, tmp_path):
        cli = StubCli(raises=CtcliError("bot threw"), raise_times=99)
        make_runner(tmp_path, cli, retries=3).run_one(spec())
        assert cli.calls == 1

    def test_infrastructure_errors_are_retried(self, tmp_path):
        # Fails twice with an infra error, succeeds on the third attempt.
        cli = StubCli(raises=InfraError("503 Service Unavailable"), raise_times=2)
        out = make_runner(tmp_path, cli, retries=2).run_one(spec())
        assert cli.calls == 3
        assert out.ok

    def test_infrastructure_errors_give_up_eventually(self, tmp_path):
        cli = StubCli(raises=InfraError("docker api"), raise_times=99)
        out = make_runner(tmp_path, cli, retries=1).run_one(spec())
        assert out.result.failed
        assert "infrastructure failure" in out.result.failure_excerpt

    def test_run_log_records_each_run(self, tmp_path):
        r = make_runner(tmp_path, StubCli())
        r.run_one(spec(trial_id="t1"))
        entries = [json.loads(l) for l in (tmp_path / "runs.jsonl").read_text().splitlines()]
        assert entries[0]["trial_id"] == "t1"
        assert entries[0]["outcome"] == "OK"


class TestParallel:
    def test_run_many_returns_every_outcome(self, tmp_path):
        cli = StubCli()
        r = make_runner(tmp_path, cli)
        specs = [spec(parameters={"Take Profit R": v}, trial_id=str(v))
                 for v in (1.0, 1.5, 2.0, 2.5)]
        outcomes = r.run_many(specs)
        assert len(outcomes) == 4
        assert cli.calls == 4

    def test_callback_fires_per_result(self, tmp_path):
        seen = []
        r = make_runner(tmp_path, StubCli())
        r.run_many([spec(parameters={"x": i}) for i in range(3)], on_result=seen.append)
        assert len(seen) == 3


class TestThroughputReport:
    def test_reports_median_and_rate(self, tmp_path):
        r = make_runner(tmp_path, StubCli())
        outcomes = [r.run_one(spec(parameters={"x": i})) for i in range(3)]
        rep = throughput_report(outcomes)
        assert rep["measured_runs"] == 3
        assert "runs_per_hour_per_worker" in rep

    def test_all_cached_is_reported_honestly(self, tmp_path):
        r = make_runner(tmp_path, StubCli())
        r.run_one(spec())
        rep = throughput_report([r.run_one(spec())])
        assert rep["measured_runs"] == 0
        assert "cache" in rep["note"]
