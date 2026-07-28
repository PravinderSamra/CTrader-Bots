"""Metric tests against hand-computed fixtures (build-spec §16.1).

Every expected value here is derived by hand in the comment above it. If a test
fails, work out which of the two is wrong before changing either — these
definitions are what every gate in the pipeline is measured against.
"""

from __future__ import annotations

import math

import numpy as np
import pandas as pd
import pytest

from engine import metrics


def eq(values, start="2024-01-01", freq="1D"):
    idx = pd.date_range(start, periods=len(values), freq=freq, tz="UTC")
    return pd.Series([float(v) for v in values], index=idx)


class TestProfitFactor:
    def test_hand_computed(self):
        # wins 100 + 50 = 150; losses |-30 - 20| = 50; PF = 3.0
        pnl = pd.Series([100.0, -30.0, 50.0, -20.0])
        assert metrics.profit_factor(pnl) == pytest.approx(3.0)

    def test_no_losses_is_infinite(self):
        assert metrics.profit_factor(pd.Series([10.0, 5.0])) == math.inf

    def test_no_trades_is_zero_not_nan(self):
        assert metrics.profit_factor(pd.Series([], dtype="float64")) == 0.0

    def test_only_losses(self):
        assert metrics.profit_factor(pd.Series([-10.0, -5.0])) == 0.0


class TestMaxDrawdown:
    def test_hand_computed(self):
        # peak 12000 at index 2, trough 9000 at index 4 -> dd = 3000
        # on a 10000 nominal account that is 30%
        curve = eq([10000, 11000, 12000, 10500, 9000, 9500])
        pct, abs_, peak, trough = metrics.max_drawdown(curve, 10000)
        assert pct == pytest.approx(30.0)
        assert abs_ == pytest.approx(3000.0)
        assert peak == pd.Timestamp("2024-01-03", tz="UTC")
        assert trough == pd.Timestamp("2024-01-05", tz="UTC")

    def test_monotonic_rise_has_no_drawdown(self):
        pct, abs_, peak, trough = metrics.max_drawdown(eq([100, 110, 120]), 100)
        assert (pct, abs_, peak, trough) == (0.0, 0.0, None, None)

    def test_empty(self):
        assert metrics.max_drawdown(pd.Series(dtype="float64"), 1000)[0] == 0.0


class TestSharpe:
    def test_constant_returns_have_zero_variance(self):
        # A perfectly straight equity line has zero std -> must be 0.0, not inf.
        assert metrics.sharpe_ratio(pd.Series([0.01] * 10)) == 0.0

    def test_hand_computed(self):
        # returns [0.01, -0.005, 0.02, 0.0]: mean = 0.00625
        # sample std (ddof=1) = 0.010871...; sharpe = mean/std*sqrt(252)
        r = pd.Series([0.01, -0.005, 0.02, 0.0])
        expected = r.mean() / r.std(ddof=1) * math.sqrt(252)
        assert metrics.sharpe_ratio(r) == pytest.approx(expected)

    def test_too_few_points(self):
        assert metrics.sharpe_ratio(pd.Series([0.01])) == 0.0

    def test_near_constant_returns_do_not_produce_absurd_sharpe(self):
        # Regression: std([0.01]*10) is ~1.7e-18 rather than exactly 0, so an
        # `sd == 0` guard let this through as Sharpe ~= 8.7e16 — a degenerate
        # trial that would top any leaderboard.
        for value in (0.01, -0.01, 1e-9):
            assert metrics.sharpe_ratio(pd.Series([value] * 10)) == 0.0

    def test_genuinely_small_but_real_dispersion_still_scores(self):
        # The degeneracy guard must not swallow a real (if tiny) signal.
        r = pd.Series([0.001, 0.002, 0.0015, 0.0005, 0.0025])
        assert metrics.sharpe_ratio(r) > 0


class TestSortino:
    def test_only_downside_counts(self):
        # downside = [-0.02]; rms = 0.02; mean = 0.01
        r = pd.Series([0.03, 0.01, -0.02, 0.02])
        expected = r.mean() / 0.02 * math.sqrt(252)
        assert metrics.sortino_ratio(r) == pytest.approx(expected)

    def test_no_losing_days(self):
        assert metrics.sortino_ratio(pd.Series([0.01, 0.02])) == 0.0

    def test_constant_losses_score_correctly_not_degenerately(self):
        # Unlike Sharpe, Sortino divides by the downside RMS rather than the
        # standard deviation, so a constant-loss series has a legitimate
        # non-zero denominator: -0.01 / 0.01 * sqrt(252).
        expected = -1.0 * math.sqrt(252)
        assert metrics.sortino_ratio(pd.Series([-0.01] * 10)) == pytest.approx(expected)


class TestStreaksAndShape:
    def test_longest_losing_streak(self):
        # runs of losses: 1, then 3, then 1 -> longest is 3
        pnl = pd.Series([-1, 5, -1, -2, -3, 4, -1])
        assert metrics.longest_losing_streak(pnl) == 3

    def test_no_losses(self):
        assert metrics.longest_losing_streak(pd.Series([1, 2, 3])) == 0

    def test_sqn_hand_computed(self):
        r = pd.Series([1.0, -1.0, 2.0, -1.0, 1.0])
        expected = math.sqrt(5) * r.mean() / r.std(ddof=1)
        assert metrics.sqn(r) == pytest.approx(expected)

    def test_ulcer_zero_when_never_in_drawdown(self):
        assert metrics.ulcer_index(eq([100, 110, 120])) == pytest.approx(0.0)

    def test_ulcer_positive_in_drawdown(self):
        assert metrics.ulcer_index(eq([100, 90, 95])) > 0

    def test_time_under_water(self):
        # peak at day 1; days 2 and 3 sit below it -> 2 days under water
        assert metrics.time_under_water(eq([100, 90, 95, 105])) == pytest.approx(2.0)


class TestDailyReturns:
    def test_flat_days_are_forward_filled(self):
        idx = pd.to_datetime(
            ["2024-01-01T10:00Z", "2024-01-01T15:00Z", "2024-01-04T10:00Z"], utc=True
        )
        equity = pd.Series([10000.0, 10100.0, 10300.0], index=idx)
        r = metrics.daily_returns(equity, 10000)
        # days: 01 -> 10100, 02 -> 10100 (ffill), 03 -> 10100, 04 -> 10300
        # diffs: 0, 0, 200 -> returns 0.0, 0.0, 0.02
        assert list(r.round(6)) == [0.0, 0.0, 0.02]


class TestCompute:
    def test_end_to_end_hand_computed(self):
        # Four trades on a 10000 account, R = 100.
        # pnl: +200, -100, +300, -100 -> net +300
        # wins 500, losses 200 -> PF 2.5; win rate 50%
        # R multiples: 2, -1, 3, -1 -> expectancy 0.75R
        pnl = pd.Series([200.0, -100.0, 300.0, -100.0])
        curve = eq([10000, 10200, 10100, 10400, 10300])
        m = metrics.compute(pnl, curve, nominal_balance=10000, risk_per_trade=100)

        assert m.trades == 4
        assert m.net_profit == pytest.approx(300.0)
        assert m.profit_factor == pytest.approx(2.5)
        assert m.win_rate == pytest.approx(50.0)
        assert m.expectancy_r == pytest.approx(0.75)
        assert m.longest_loss_streak == 1
        # max dd: peak 10400 -> trough 10300 = 100 = 1% of nominal
        assert m.max_dd_pct == pytest.approx(1.0)
        assert m.max_dd_abs == pytest.approx(100.0)

    def test_no_trades_produces_zeros_not_errors(self):
        m = metrics.compute(
            pd.Series([], dtype="float64"), pd.Series(dtype="float64"), 10000, 100
        )
        assert m.trades == 0
        assert m.sharpe == 0.0
        assert m.max_dd_pct == 0.0
        assert m.as_dict()["max_dd_peak"] is None

    def test_trades_per_year_scales_by_span(self):
        # 2 trades over a 6-month span -> ~4 per year
        idx = pd.to_datetime(["2024-01-01T00:00Z", "2024-07-01T00:00Z"], utc=True)
        curve = pd.Series([10000.0, 10200.0], index=idx)
        m = metrics.compute(pd.Series([100.0, 100.0]), curve, 10000, 100)
        assert m.trades_per_year == pytest.approx(4.0, rel=0.02)


class TestSuspicionFlags:
    def test_flags_high_pf_on_few_trades(self):
        m = metrics.compute(
            pd.Series([500.0] * 8 + [-10.0]),
            eq([10000 + 500 * i for i in range(10)]),
            10000, 100,
        )
        flags = metrics.suspicion_flags(m)
        assert any("profit factor" in f for f in flags)

    def test_clean_result_has_no_flags(self):
        rng = np.random.default_rng(0)
        pnl = pd.Series(rng.normal(5, 100, 300))
        curve = eq([10000 + v for v in pnl.cumsum()])
        assert metrics.suspicion_flags(
            metrics.compute(pnl, curve, 10000, 100)
        ) == []
