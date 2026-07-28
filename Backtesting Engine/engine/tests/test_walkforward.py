"""Walk-forward tests (build-spec §16.1: fold generation edge cases).

The fold table is where a leak would do the most damage: one fold reaching past
holdout_start would silently burn the only untouched data in the study.
"""

from __future__ import annotations

from datetime import date

import pandas as pd
import pytest

from engine.config import load_search_space
from engine.walkforward import (
    Fold, FoldResult, add_months, concatenate_oos, fold_concentration,
    generate_folds, parameter_dispersion, walk_forward_efficiency,
)
from engine.metrics import compute
from tests.test_config import VALID_SPACE, write


class TestAddMonths:
    def test_simple(self):
        assert add_months(date(2024, 1, 15), 6) == date(2024, 7, 15)

    def test_crosses_year(self):
        assert add_months(date(2024, 11, 1), 3) == date(2025, 2, 1)

    def test_clamps_to_short_month(self):
        # 31 Jan + 1 month has no 31st; clamp rather than overflow into March.
        assert add_months(date(2024, 1, 31), 1) == date(2024, 2, 29)   # leap year
        assert add_months(date(2023, 1, 31), 1) == date(2023, 2, 28)

    def test_zero_and_negative(self):
        assert add_months(date(2024, 5, 10), 0) == date(2024, 5, 10)
        assert add_months(date(2024, 5, 10), -2) == date(2024, 3, 10)


class TestFoldGeneration:
    def test_uk100_geometry(self):
        # The real study: 2021-08-02 -> holdout 2025-07-01, IS18/OOS6/step6.
        folds = generate_folds(date(2021, 8, 2), date(2025, 7, 1), 18, 6, 6)
        assert len(folds) == 4
        # Default "end" alignment: the OOS runs right up to the holdout.
        assert folds[-1].oos_end == date(2025, 7, 1)

    @pytest.mark.parametrize("align", ["end", "start"])
    def test_no_fold_ever_reaches_the_holdout(self, align):
        folds = generate_folds(date(2021, 8, 2), date(2025, 7, 1), 18, 6, 6, align=align)
        for f in folds:
            assert f.oos_end <= date(2025, 7, 1), f"fold {f.index} leaks into the holdout"

    def test_end_alignment_uses_the_most_recent_data(self):
        # "start" alignment stops five months short of the holdout on this
        # geometry, discarding the most recent — and most relevant — regime.
        start_aligned = generate_folds(date(2021, 8, 2), date(2025, 7, 1), 18, 6, 6,
                                       align="start")
        end_aligned = generate_folds(date(2021, 8, 2), date(2025, 7, 1), 18, 6, 6,
                                     align="end")
        assert start_aligned[-1].oos_end < date(2025, 7, 1)
        assert end_aligned[-1].oos_end == date(2025, 7, 1)
        assert end_aligned[-1].oos_end > start_aligned[-1].oos_end

    def test_end_alignment_never_starts_before_the_data(self):
        folds = generate_folds(date(2021, 8, 2), date(2025, 7, 1), 18, 6, 6, align="end")
        for f in folds:
            assert f.is_start >= date(2021, 8, 2)

    def test_folds_are_indexed_in_chronological_order(self):
        folds = generate_folds(date(2021, 8, 2), date(2025, 7, 1), 18, 6, 6, align="end")
        assert [f.index for f in folds] == list(range(len(folds)))
        for a, b in zip(folds, folds[1:]):
            assert b.oos_start > a.oos_start

    def test_folds_are_contiguous_and_ordered(self):
        folds = generate_folds(date(2021, 1, 1), date(2025, 1, 1), 12, 6, 6)
        for a, b in zip(folds, folds[1:]):
            assert b.is_start > a.is_start
            assert a.oos_start == a.is_end          # OOS begins where IS ends

    def test_anchored_mode_keeps_the_same_start(self):
        folds = generate_folds(date(2021, 1, 1), date(2026, 1, 1), 12, 6, 6,
                               mode="anchored")
        assert len({f.is_start for f in folds}) == 1
        assert all(f.is_start == date(2021, 1, 1) for f in folds)

    def test_rolling_mode_moves_the_start(self):
        folds = generate_folds(date(2021, 1, 1), date(2026, 1, 1), 12, 6, 6)
        assert len({f.is_start for f in folds}) == len(folds)

    def test_insufficient_data_raises_rather_than_returning_nothing(self):
        with pytest.raises(ValueError, match="no walk-forward folds fit"):
            generate_folds(date(2024, 1, 1), date(2024, 6, 1), 18, 6, 6)

    def test_longer_step_produces_fewer_folds(self):
        many = generate_folds(date(2021, 1, 1), date(2026, 1, 1), 12, 6, 3)
        few = generate_folds(date(2021, 1, 1), date(2026, 1, 1), 12, 6, 12)
        assert len(many) > len(few)


def make_fold_result(index, oos_values, start="2024-01-01", profit=None):
    idx = pd.date_range(start, periods=len(oos_values), freq="1D", tz="UTC")
    equity = pd.Series([float(v) for v in oos_values], index=idx)
    trades = pd.DataFrame({"net_pnl": pd.Series(equity.diff().dropna().values)})
    m = compute(trades["net_pnl"], equity, 10000, 100)
    if profit is not None:
        m = compute(pd.Series([profit]), equity, 10000, 100)
    fold = Fold(index, date(2021, 1, 1), date(2022, 1, 1), date(2022, 1, 1), date(2022, 7, 1))
    return FoldResult(fold, {"Take Profit R": 2.0}, None, m, trades, equity)


class TestConcatenation:
    def test_folds_are_chained_by_increment_not_level(self):
        # Each fold's backtest restarts at the nominal balance. Naive
        # concatenation would throw away every fold's gain.
        a = make_fold_result(0, [10000, 10200], start="2024-01-01")
        b = make_fold_result(1, [10000, 10300], start="2024-06-01")
        _, equity = concatenate_oos([a, b], 10000)
        assert float(equity.iloc[-1]) == pytest.approx(10500.0)

    def test_failed_folds_are_skipped(self):
        a = make_fold_result(0, [10000, 10200])
        bad = make_fold_result(1, [10000, 10300])
        bad.failed = True
        _, equity = concatenate_oos([a, bad], 10000)
        assert float(equity.iloc[-1]) == pytest.approx(10200.0)

    def test_empty_input(self):
        pnl, equity = concatenate_oos([], 10000)
        assert pnl.empty and equity.empty


class TestGateMetrics:
    def test_wfe_is_zero_when_in_sample_is_unprofitable(self):
        r = make_fold_result(0, [10000, 10100])
        r.is_metrics = compute(pd.Series([-100.0]),
                               pd.Series([10000.0, 9900.0],
                                         index=pd.to_datetime(["2024-01-01", "2024-02-01"],
                                                              utc=True)),
                               10000, 100)
        assert walk_forward_efficiency([r]) == 0.0

    def test_concentration_flags_a_single_dominant_fold(self):
        a = make_fold_result(0, [10000, 10010], profit=10.0)
        b = make_fold_result(1, [10000, 11000], profit=990.0)
        assert fold_concentration([a, b]) == pytest.approx(0.99, abs=0.01)

    def test_concentration_is_even_when_folds_agree(self):
        a = make_fold_result(0, [10000, 10500], profit=500.0)
        b = make_fold_result(1, [10000, 10500], profit=500.0)
        assert fold_concentration([a, b]) == pytest.approx(0.5)

    def test_all_losing_folds_report_worst_case_concentration(self):
        a = make_fold_result(0, [10000, 9500], profit=-500.0)
        assert fold_concentration([a]) == 1.0


class TestParameterDispersion:
    def test_stable_selection_has_zero_dispersion(self, tmp_path):
        space = load_search_space(write(tmp_path, VALID_SPACE, "search_space.yaml"))
        results = [make_fold_result(i, [10000, 10100]) for i in range(3)]
        for r in results:
            r.selected_params = {"Take Profit R": 2.0, "Max Hold Bars": 5}
        d = parameter_dispersion(results, space)
        assert d["Take Profit R"] == pytest.approx(0.0)

    def test_chaotic_selection_shows_high_dispersion(self, tmp_path):
        space = load_search_space(write(tmp_path, VALID_SPACE, "search_space.yaml"))
        results = [make_fold_result(i, [10000, 10100]) for i in range(3)]
        for r, v in zip(results, (1.0, 2.5, 4.0)):
            r.selected_params = {"Take Profit R": v, "Max Hold Bars": 5}
        d = parameter_dispersion(results, space)
        assert d["Take Profit R"] > 0.3
