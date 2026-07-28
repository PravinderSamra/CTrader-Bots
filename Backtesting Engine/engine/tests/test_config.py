"""Config loader tests (build-spec §16.1).

The loader's job is to fail loudly, so most of these assert that bad configs are
rejected — including the specific mistakes that 03-Verification-Findings caught in
the original spec.
"""

from __future__ import annotations

import textwrap
from pathlib import Path

import pytest
import yaml

from engine.config import ConfigError, load_search_space, load_study

REPO = Path(__file__).resolve().parents[3]

VALID_STUDY = {
    "study": "test_v1",
    "ctrader_console_tag": "5.9.0.0",
    "bot": {"source": "3 Down Days/ThreeDownDaysBot.cs", "class_name": "ThreeDownDaysBot"},
    "market": {"symbol": "XAUUSD", "period": "D1", "data_glob": "x/*.csv"},
    "account": {"nominal_balance": 10000, "currency": "GBP", "risk_per_trade": 100},
    "execution": {
        "spread_pips": {"realistic": 2.0, "stressed": 4.0},
        "commission_per_million": 0.0,
        "slippage_model": {"dist": "lognormal", "median_pips": 0.5, "p95_pips": 3.0},
    },
    "windows": {
        "data_start": "2021-07-18",
        "holdout_start": "2025-07-01",
        "wfa": {"mode": "rolling", "is_months": 18, "oos_months": 6, "step_months": 6},
    },
    "budgets": {
        "stage1_random": 200, "stage1_tpe": 600,
        "wfa_trials_per_fold": 150, "mc_resamples": 5000,
    },
}


def write(tmp_path: Path, cfg: dict, name="study.yaml") -> Path:
    p = tmp_path / name
    p.write_text(yaml.safe_dump(cfg))
    return p


def mutate(**changes) -> dict:
    import copy
    cfg = copy.deepcopy(VALID_STUDY)
    for dotted, value in changes.items():
        keys = dotted.split(".")
        node = cfg
        for k in keys[:-1]:
            node = node[k]
        if value is None:
            node.pop(keys[-1], None)
        else:
            node[keys[-1]] = value
    return cfg


class TestStudyConfig:
    def test_valid_config_loads(self, tmp_path):
        s = load_study(write(tmp_path, VALID_STUDY))
        assert s.study == "test_v1"
        assert s.bot.dotnet_target == "net6.0"       # defaults to the runtime the image ships
        assert s.gates.min_trades_per_year == 100    # engine default, not the spec's 30
        assert s.execution.spread("stressed") == 4.0

    def test_commission_per_lot_is_rejected_with_a_useful_message(self, tmp_path):
        cfg = mutate(**{"execution.commission_per_million": None})
        cfg["execution"]["commission_per_lot"] = 7.0
        with pytest.raises(ConfigError, match="per million"):
            load_study(write(tmp_path, cfg))

    def test_latest_tag_is_rejected(self, tmp_path):
        with pytest.raises(ConfigError, match="not reproducible"):
            load_study(write(tmp_path, mutate(ctrader_console_tag="latest")))

    def test_missing_tag_is_rejected(self, tmp_path):
        with pytest.raises(ConfigError, match="ctrader_console_tag is required"):
            load_study(write(tmp_path, mutate(ctrader_console_tag=None)))

    def test_lowercase_d1_is_rejected_because_periods_are_case_sensitive(self, tmp_path):
        with pytest.raises(ConfigError, match="case-sensitive"):
            load_study(write(tmp_path, mutate(**{"market.period": "d1"})))

    def test_valid_lowercase_periods_still_work(self, tmp_path):
        assert load_study(write(tmp_path, mutate(**{"market.period": "m5"}))).market.period == "m5"

    def test_zero_spread_is_rejected(self, tmp_path):
        cfg = mutate()
        cfg["execution"]["spread_pips"] = {"realistic": 0.0}
        with pytest.raises(ConfigError, match="zero/negative spread"):
            load_study(write(tmp_path, cfg))

    def test_holdout_before_data_start_is_rejected(self, tmp_path):
        with pytest.raises(ConfigError, match="holdout_start must be after"):
            load_study(write(tmp_path, mutate(**{"windows.holdout_start": "2020-01-01"})))

    def test_gates_can_be_overridden(self, tmp_path):
        cfg = mutate()
        cfg["gates"] = {"min_trades_per_year": 12}
        s = load_study(write(tmp_path, cfg))
        assert s.gates.min_trades_per_year == 12
        assert s.gates.min_pf == 1.15   # unspecified gates keep their defaults

    def test_missing_section_names_the_section(self, tmp_path):
        with pytest.raises(ConfigError, match="missing required key 'account'"):
            load_study(write(tmp_path, mutate(account=None)))


VALID_SPACE = {
    "fixed": {"Risk Amount": 100},
    "search": {
        "Take Profit R": {"type": "float", "low": 1.0, "high": 4.0, "step": 0.25},
        "Max Hold Bars": {"type": "int", "low": 2, "high": 10},
    },
    "notes": "Take Profit R — the target.\nMax Hold Bars — the time stop.\n",
}


class TestSearchSpace:
    def test_valid_space_loads(self, tmp_path):
        s = load_search_space(write(tmp_path, VALID_SPACE, "search_space.yaml"))
        assert s.effective_dimensions == 2

    def test_dimension_limit_is_enforced(self, tmp_path):
        cfg = {**VALID_SPACE, "search": {
            f"P{i}": {"type": "int", "low": 1, "high": 10} for i in range(11)
        }}
        with pytest.raises(ConfigError, match="the limit is 10"):
            load_search_space(write(tmp_path, cfg, "search_space.yaml"))

    def test_notes_are_required(self, tmp_path):
        cfg = {**VALID_SPACE, "notes": "   "}
        with pytest.raises(ConfigError, match="notes is REQUIRED"):
            load_search_space(write(tmp_path, cfg, "search_space.yaml"))

    def test_inverted_range_is_rejected(self, tmp_path):
        cfg = {**VALID_SPACE, "search": {"X": {"type": "float", "low": 5, "high": 1}}}
        with pytest.raises(ConfigError, match="low must be < high"):
            load_search_space(write(tmp_path, cfg, "search_space.yaml"))

    def test_empty_choices_rejected(self, tmp_path):
        cfg = {**VALID_SPACE, "search": {"X": {"type": "cat", "choices": []}}}
        with pytest.raises(ConfigError, match="require non-empty choices"):
            load_search_space(write(tmp_path, cfg, "search_space.yaml"))

    def test_mutually_exclusive_branches_do_not_compound(self, tmp_path):
        # Three params under a toggle plus one under its negation: only one
        # branch can be live, so this is 2 active dimensions, not 5.
        cfg = {**VALID_SPACE, "search": {
            "Enable Multi TP": {"type": "bool"},
            "Take Profit R": {"type": "float", "low": 1, "high": 4,
                              "condition": "Enable Multi TP == false"},
            "TP1 R": {"type": "float", "low": 0.5, "high": 2,
                      "condition": "Enable Multi TP == true"},
            "TP2 R": {"type": "float", "low": 1.5, "high": 5,
                      "condition": "Enable Multi TP == true"},
        }}
        space = load_search_space(write(tmp_path, cfg, "search_space.yaml"))
        assert space.declared_dimensions == 4
        assert space.effective_dimensions == 3   # toggle + the 2-param branch

    def test_is_active_respects_equality_conditions(self, tmp_path):
        cfg = {**VALID_SPACE, "search": {
            "Enable Multi TP": {"type": "bool"},
            "Take Profit R": {"type": "float", "low": 1, "high": 4,
                              "condition": "Enable Multi TP == false"},
            "TP1 R": {"type": "float", "low": 0.5, "high": 2,
                      "condition": "Enable Multi TP == true"},
        }}
        space = load_search_space(write(tmp_path, cfg, "search_space.yaml"))
        assert space.is_active("Take Profit R", {"Enable Multi TP": False})
        assert not space.is_active("Take Profit R", {"Enable Multi TP": True})
        assert space.is_active("TP1 R", {"Enable Multi TP": True})
        assert not space.is_active("TP1 R", {"Enable Multi TP": False})

    def test_truthy_condition_still_works(self, tmp_path):
        cfg = {**VALID_SPACE, "search": {
            "Enable Trend Filter": {"type": "bool"},
            "Trend EMA Period": {"type": "int", "low": 5, "high": 50,
                                 "condition": "Enable Trend Filter"},
        }}
        space = load_search_space(write(tmp_path, cfg, "search_space.yaml"))
        assert space.is_active("Trend EMA Period", {"Enable Trend Filter": True})
        assert not space.is_active("Trend EMA Period", {"Enable Trend Filter": False})
        assert space.effective_dimensions == 2

    def test_condition_on_categorical_value(self, tmp_path):
        cfg = {**VALID_SPACE, "search": {
            "Mode": {"type": "cat", "choices": ["A", "B", "C"]},
            "AOnly": {"type": "int", "low": 1, "high": 5, "condition": "Mode == A"},
            "BOnly": {"type": "int", "low": 1, "high": 5, "condition": "Mode == B"},
        }}
        space = load_search_space(write(tmp_path, cfg, "search_space.yaml"))
        assert space.effective_dimensions == 2      # Mode + exactly one branch
        assert space.is_active("AOnly", {"Mode": "A"})
        assert not space.is_active("AOnly", {"Mode": "B"})

    def test_condition_naming_a_missing_choice_is_rejected(self, tmp_path):
        cfg = {**VALID_SPACE, "search": {
            "Mode": {"type": "cat", "choices": ["A", "B"]},
            "X": {"type": "int", "low": 1, "high": 5, "condition": "Mode == Z"},
        }}
        with pytest.raises(ConfigError, match="not one of its choices"):
            load_search_space(write(tmp_path, cfg, "search_space.yaml"))

    def test_limit_applies_to_active_not_declared(self, tmp_path):
        # 14 declared, but every extra one hangs off a mutually-exclusive branch.
        search = {"Mode": {"type": "cat", "choices": ["A", "B"]}}
        for i in range(6):
            search[f"A{i}"] = {"type": "int", "low": 1, "high": 5, "condition": "Mode == A"}
            search[f"B{i}"] = {"type": "int", "low": 1, "high": 5, "condition": "Mode == B"}
        space = load_search_space(
            write(tmp_path, {**VALID_SPACE, "search": search}, "search_space.yaml"))
        assert space.declared_dimensions == 13
        assert space.effective_dimensions == 7      # Mode + one 6-param branch

    def test_dangling_condition_is_rejected(self, tmp_path):
        cfg = {**VALID_SPACE, "search": {
            "X": {"type": "int", "low": 1, "high": 5, "condition": "Nonexistent Toggle"},
        }}
        with pytest.raises(ConfigError, match="neither a searched nor a fixed"):
            load_search_space(write(tmp_path, cfg, "search_space.yaml"))


class TestShippedStudy:
    """The study committed to the repo must actually be valid."""

    def test_threedowndays_study_loads(self):
        path = REPO / "Backtesting Engine" / "studies" / "threedowndays_xauusd" / "study.yaml"
        s = load_study(path)
        assert s.market.period == "D1"
        assert s.bot.dotnet_target == "net6.0"
        assert s.windows.data_start.isoformat() == "2021-07-18"

    def test_threedowndays_search_space_loads(self):
        path = REPO / "Backtesting Engine" / "studies" / "threedowndays_xauusd" / "search_space.yaml"
        space = load_search_space(path)
        assert space.effective_dimensions <= 10
        assert "Skip Mondays" in space.fixed   # day filters must never be searched
        assert "Skip Fridays" in space.fixed

    @pytest.mark.parametrize("study", ["orb_uk100", "orb_uk100_exits"])
    def test_orb_studies_load_and_respect_the_dimension_limit(self, study):
        base = REPO / "Backtesting Engine" / "studies" / study
        load_study(base / "study.yaml")
        space = load_search_space(base / "search_space.yaml")
        assert space.effective_dimensions <= 10
        # Declared > active is the whole point of the branch design.
        assert space.declared_dimensions >= space.effective_dimensions

    def test_orb_session_timezone_is_london_not_utc(self):
        # UK100-BUILD-PLAN.md: session times are Europe/London wall-clock and
        # must never be hardcoded to UTC. The bot's default would silently shift
        # the opening range by an hour for the months BST is in effect.
        for study in ("orb_uk100", "orb_uk100_exits"):
            space = load_search_space(
                REPO / "Backtesting Engine" / "studies" / study / "search_space.yaml")
            assert space.fixed["Use Fixed UTC Times"] is False
            assert space.fixed["Session Time Zone"] == "EuropeLondon"

    def test_orb_day_filters_are_never_searched(self):
        for study in ("orb_uk100", "orb_uk100_exits"):
            space = load_search_space(
                REPO / "Backtesting Engine" / "studies" / study / "search_space.yaml")
            for day in ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday"):
                assert f"Trade {day}" in space.fixed
                assert f"Trade {day}" not in space.search
