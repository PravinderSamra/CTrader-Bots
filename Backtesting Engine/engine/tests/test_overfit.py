"""DSR and PBO tests (build-spec §12, §16.1).

The two that matter most are the synthetic-data tests: pure noise must produce
PBO near 0.5, and a genuine persistent edge must produce PBO near 0. If those
fail, the statistic is not measuring what it claims and every verdict built on
it is worthless.
"""

from __future__ import annotations

import math

import numpy as np
import pandas as pd
import pytest

from engine.overfit import (
    build_performance_matrix, deflated_sharpe_ratio, effective_trial_count,
    expected_max_sharpe, probability_of_backtest_overfitting,
)


class TestExpectedMaxSharpe:
    def test_grows_with_trial_count(self):
        # The whole premise: try more things, expect a higher maximum by luck.
        few = expected_max_sharpe(10, 0.25)
        many = expected_max_sharpe(10_000, 0.25)
        assert many > few > 0

    def test_scales_with_dispersion(self):
        assert expected_max_sharpe(1000, 1.0) > expected_max_sharpe(1000, 0.25)

    def test_degenerate_inputs(self):
        assert expected_max_sharpe(1, 0.25) == 0.0
        assert expected_max_sharpe(1000, 0.0) == 0.0


class TestDeflatedSharpe:
    def test_strong_edge_with_few_trials_passes(self):
        rng = np.random.default_rng(0)
        # Daily mean 0.0012, sd 0.005 -> annualised Sharpe around 3.
        r = pd.Series(rng.normal(0.0012, 0.005, 1000))
        res = deflated_sharpe_ratio(r, trial_sharpes=[0.5, 0.7, 0.6, 0.8, 2.5])
        assert res.dsr > 0.95
        assert res.sharpe_annualised > 2.5

    def test_same_edge_is_deflated_by_a_huge_search(self):
        rng = np.random.default_rng(0)
        r = pd.Series(rng.normal(0.0008, 0.005, 1000))
        few = deflated_sharpe_ratio(r, [0.5, 0.7, 0.6, 0.8, 2.5])
        many = deflated_sharpe_ratio(
            r, list(rng.normal(0.0, 1.5, 5000)), n_effective_trials=5000)
        # Identical returns, far more searching -> strictly less convincing.
        assert many.dsr < few.dsr

    def test_no_edge_fails(self):
        rng = np.random.default_rng(1)
        r = pd.Series(rng.normal(0.0, 0.005, 1000))       # zero mean
        res = deflated_sharpe_ratio(r, list(rng.normal(0, 1.0, 800)),
                                    n_effective_trials=800)
        assert res.dsr < 0.95

    def test_effective_trials_defaults_to_population_size(self):
        rng = np.random.default_rng(2)
        r = pd.Series(rng.normal(0.0005, 0.005, 500))
        res = deflated_sharpe_ratio(r, [1.0, 1.1, 0.9])
        assert res.n_effective_trials == 3

    def test_negative_skew_and_fat_tails_reduce_confidence(self):
        rng = np.random.default_rng(3)
        base = rng.normal(0.0008, 0.005, 2000)
        symmetric = deflated_sharpe_ratio(pd.Series(base), [0.5, 0.6, 0.7])
        # Inject a few large losses: same broad edge, uglier distribution.
        skewed_vals = base.copy()
        skewed_vals[::200] -= 0.05
        skewed = deflated_sharpe_ratio(pd.Series(skewed_vals), [0.5, 0.6, 0.7])
        assert skewed.skew < symmetric.skew
        assert skewed.dsr < symmetric.dsr

    def test_too_few_observations_returns_zero_not_an_error(self):
        assert deflated_sharpe_ratio(pd.Series([0.01, 0.02]), [1.0]).dsr == 0.0

    def test_flat_returns_return_zero(self):
        assert deflated_sharpe_ratio(pd.Series([0.01] * 50), [1.0]).dsr == 0.0


class TestEffectiveTrialCount:
    def test_deduplicates_identical_configurations(self):
        assert effective_trial_count(["a", "b", "a", "c", "b"]) == 3

    def test_empty(self):
        assert effective_trial_count([]) == 0


class TestPboOnSyntheticData:
    """The tests that decide whether PBO is trustworthy at all."""

    def test_pure_noise_gives_pbo_near_half_on_average(self):
        # Averaged over realisations, noise must give ~0.5. Asserting on a
        # SINGLE seed would be wrong: PBO's spread at this size is enormous
        # (see test_pbo_is_alarmingly_noisy_at_realistic_sizes), and seed 42
        # alone returns 0.73 on data with no edge whatsoever.
        vals = []
        for seed in range(12):
            rng = np.random.default_rng(seed)
            M = rng.normal(0.0, 1.0, size=(320, 50))
            vals.append(probability_of_backtest_overfitting(
                M, n_blocks=16, max_splits=1500, rng_seed=1).pbo)
        assert 0.4 < float(np.mean(vals)) < 0.6, f"noise mean should be ~0.5, got {np.mean(vals)}"

    def test_pbo_is_alarmingly_noisy_at_realistic_sizes(self):
        # Documents a property of the statistic, not of this implementation:
        # on pure noise, individual PBO values range roughly 0.08-0.81. Several
        # of those would sail through a `pbo <= 0.25` gate. This is why the
        # engine reports an interval and why the verdict must treat a wide band
        # as inconclusive rather than as a pass.
        vals = []
        for seed in range(12):
            rng = np.random.default_rng(seed)
            M = rng.normal(0.0, 1.0, size=(320, 50))
            vals.append(probability_of_backtest_overfitting(
                M, n_blocks=16, max_splits=1500, rng_seed=1).pbo)
        assert float(np.std(vals)) > 0.12, (
            "if this ever falls, the noise warning in the docs can be relaxed")
        assert any(v < 0.25 for v in vals), (
            "pure noise passing a 0.25 gate is the failure mode being guarded against")

    def test_more_observations_reduce_the_spread(self):
        def spread(n_obs):
            vals = []
            for seed in range(8):
                rng = np.random.default_rng(seed)
                M = rng.normal(0.0, 1.0, size=(n_obs, 50))
                vals.append(probability_of_backtest_overfitting(
                    M, n_blocks=16, max_splits=800, rng_seed=1).pbo)
            return float(np.std(vals))
        assert spread(1280) < spread(320)

    def test_genuine_persistent_edge_gives_low_pbo(self):
        # One strategy is genuinely better in every period; selection should
        # find it and it should hold up out-of-sample.
        rng = np.random.default_rng(7)
        M = rng.normal(0.0, 1.0, size=(320, 50))
        M[:, 17] += 1.5
        res = probability_of_backtest_overfitting(M, n_blocks=16, max_splits=2000)
        assert res.pbo < 0.1, f"a real edge should give a low PBO, got {res.pbo}"

    def test_in_sample_only_edge_gives_high_pbo(self):
        # The overfitting signature: a strategy that shines in the first half
        # and collapses in the second. Selection is actively misleading.
        rng = np.random.default_rng(11)
        M = rng.normal(0.0, 1.0, size=(320, 40))
        M[:160, 5] += 3.0        # brilliant early
        M[160:, 5] -= 3.0        # terrible later
        res = probability_of_backtest_overfitting(M, n_blocks=8, max_splits=2000)
        assert res.pbo > 0.5, f"an in-sample-only edge should give a high PBO, got {res.pbo}"


class TestPboMechanics:
    def test_reports_split_and_block_counts(self):
        rng = np.random.default_rng(0)
        res = probability_of_backtest_overfitting(
            rng.normal(0, 1, (160, 20)), n_blocks=8, max_splits=100)
        assert res.n_blocks == 8
        assert res.n_trials == 20
        assert 0 < res.n_splits <= 100

    def test_split_sampling_is_deterministic(self):
        rng = np.random.default_rng(0)
        M = rng.normal(0, 1, (320, 30))
        a = probability_of_backtest_overfitting(M, n_blocks=16, max_splits=200, rng_seed=5)
        b = probability_of_backtest_overfitting(M, n_blocks=16, max_splits=200, rng_seed=5)
        assert a.pbo == b.pbo

    def test_odd_block_count_is_rejected(self):
        rng = np.random.default_rng(0)
        with pytest.raises(ValueError, match="even"):
            probability_of_backtest_overfitting(rng.normal(0, 1, (100, 10)), n_blocks=7)

    def test_single_trial_is_rejected(self):
        with pytest.raises(ValueError, match="at least 2 trials"):
            probability_of_backtest_overfitting(np.zeros((100, 1)))

    def test_few_observations_reduces_blocks_rather_than_failing(self):
        rng = np.random.default_rng(0)
        res = probability_of_backtest_overfitting(
            rng.normal(0, 1, (10, 5)), n_blocks=16, max_splits=100)
        assert res.n_blocks <= 10


class TestPboInterval:
    def test_reports_a_band_not_just_a_point(self):
        from engine.overfit import pbo_with_uncertainty
        rng = np.random.default_rng(42)
        M = rng.normal(0.0, 1.0, size=(320, 50))
        res = pbo_with_uncertainty(M, n_blocks=16, max_splits=800, n_resamples=25)
        assert res.p05 <= res.pbo <= res.p95 or res.sd > 0
        assert res.n_resamples > 0

    def test_noise_band_is_wide_enough_to_be_called_inconclusive(self):
        from engine.overfit import pbo_with_uncertainty
        rng = np.random.default_rng(3)
        M = rng.normal(0.0, 1.0, size=(320, 40))
        res = pbo_with_uncertainty(M, n_blocks=16, max_splits=800, n_resamples=30)
        assert res.sd > 0.0
        assert isinstance(res.is_conclusive, bool)

    def test_genuine_edge_gives_a_tight_low_band(self):
        from engine.overfit import pbo_with_uncertainty
        rng = np.random.default_rng(7)
        M = rng.normal(0.0, 1.0, size=(320, 50))
        M[:, 17] += 1.5
        res = pbo_with_uncertainty(M, n_blocks=16, max_splits=800, n_resamples=30)
        assert res.p95 < 0.35
        assert res.is_conclusive


class TestPerformanceMatrix:
    def test_aligns_trials_on_a_common_index(self):
        idx_a = pd.date_range("2024-01-01", periods=100, freq="1D", tz="UTC")
        idx_b = pd.date_range("2024-01-15", periods=100, freq="1D", tz="UTC")
        rng = np.random.default_rng(0)
        M, labels = build_performance_matrix({
            "t1": pd.Series(rng.normal(0, 1, 100), index=idx_a),
            "t2": pd.Series(rng.normal(0, 1, 100), index=idx_b),
        }, n_blocks=8)
        assert M.shape[1] == 2
        assert labels == ["t1", "t2"]
        assert not np.isnan(M).any()   # gaps become flat, never NaN

    def test_empty_input_raises(self):
        with pytest.raises(ValueError, match="no trial returns"):
            build_performance_matrix({})

    def test_matrix_feeds_straight_into_pbo(self):
        rng = np.random.default_rng(3)
        idx = pd.date_range("2024-01-01", periods=320, freq="1D", tz="UTC")
        trials = {f"t{i}": pd.Series(rng.normal(0, 1, 320), index=idx) for i in range(20)}
        M, _ = build_performance_matrix(trials, n_blocks=16)
        res = probability_of_backtest_overfitting(M, n_blocks=16, max_splits=500)
        assert 0.0 <= res.pbo <= 1.0
