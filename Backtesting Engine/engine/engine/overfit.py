"""Stage 4 overfitting statistics: DSR and PBO (build-spec §12).

These are the two tests that ask the uncomfortable question — *given how many
things you tried, is this result distinguishable from luck?*

**Deflated Sharpe Ratio** (Bailey & López de Prado 2014). The expected maximum
Sharpe of N independent noise strategies grows with N. DSR asks whether the
candidate's Sharpe exceeds that benchmark, correcting for the non-normality of
the return series (skew and excess kurtosis both make a high Sharpe easier to
achieve by chance) and for track length.

**Probability of Backtest Overfitting** (Bailey, Borwein, López de Prado, Zhu
2016), via Combinatorially Symmetric Cross-Validation. Split the trial
performance matrix into S blocks, take every balanced in-sample/out-of-sample
partition, and measure how often the in-sample winner lands below median
out-of-sample. If that happens about half the time, the selection procedure has
no skill — you would have done as well picking at random.

Both are statistics with assumptions, not oracles. They are gates *and* context
in the report, and neither is a substitute for the untouched holdout.

The N that DSR deflates by is the **total number of configurations evaluated in
the study** — Stage 1 plus every walk-forward fold plus plateau probes — not
Stage 1 alone (03-Verification-Findings §4.2). Passing a smaller N silently
inflates the result.
"""

from __future__ import annotations

import itertools
import math
from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy import stats

EULER_MASCHERONI = 0.5772156649015329


@dataclass(frozen=True)
class DsrResult:
    sharpe: float
    sharpe_annualised: float
    expected_max_sharpe: float
    dsr: float
    n_trials: int
    n_effective_trials: int
    n_observations: int
    skew: float
    kurtosis: float

    def as_dict(self) -> dict:
        return {k: getattr(self, k) for k in self.__dataclass_fields__}


def expected_max_sharpe(n_trials: int, sharpe_variance: float) -> float:
    """E[max Sharpe] over N independent trials with the given variance.

    Bailey & López de Prado's approximation:

        E[max] ≈ sqrt(V) * ((1-γ)·Z⁻¹(1 - 1/N) + γ·Z⁻¹(1 - 1/(N·e)))

    where γ is Euler-Mascheroni. This is the bar a genuine edge has to clear:
    with enough trials, an impressive-looking Sharpe is simply what the maximum
    of noise looks like.
    """
    if n_trials < 2 or sharpe_variance <= 0:
        return 0.0
    z1 = stats.norm.ppf(1.0 - 1.0 / n_trials)
    z2 = stats.norm.ppf(1.0 - 1.0 / (n_trials * math.e))
    return math.sqrt(sharpe_variance) * (
        (1 - EULER_MASCHERONI) * z1 + EULER_MASCHERONI * z2
    )


def deflated_sharpe_ratio(
    returns: pd.Series,
    trial_sharpes: list[float] | np.ndarray,
    n_effective_trials: int | None = None,
    periods_per_year: int = 252,
) -> DsrResult:
    """Probability that the candidate's Sharpe beats the expected max of noise.

    ``returns`` are the candidate's per-period (daily) returns.
    ``trial_sharpes`` is every trial's Sharpe — the variance of that population
    is what sets the noise benchmark, which is why the full trial log matters.
    """
    r = pd.Series(returns, dtype="float64").dropna()
    n = len(r)
    if n < 3:
        return DsrResult(0.0, 0.0, 0.0, 0.0, len(trial_sharpes), 0, n, 0.0, 0.0)

    sd = float(r.std(ddof=1))
    if sd <= 0 or not math.isfinite(sd):
        return DsrResult(0.0, 0.0, 0.0, 0.0, len(trial_sharpes), 0, n, 0.0, 0.0)

    sharpe = float(r.mean() / sd)                       # per-period
    skew = float(stats.skew(r, bias=False))
    # Excess kurtosis + 3 gives the raw fourth moment the formula expects.
    kurt = float(stats.kurtosis(r, fisher=True, bias=False)) + 3.0

    sharpes = np.asarray([s for s in trial_sharpes if math.isfinite(s)], dtype="float64")
    n_trials = int(len(sharpes))
    n_eff = int(n_effective_trials if n_effective_trials is not None else n_trials)

    # Trial Sharpes arrive annualised; the benchmark must be on the same
    # per-period scale as the candidate's.
    variance = float(np.var(sharpes / math.sqrt(periods_per_year), ddof=1)) \
        if n_trials > 1 else 0.0
    sr_star = expected_max_sharpe(max(n_eff, 2), variance)

    # Standard error of the Sharpe estimator under non-normality.
    denom = 1.0 - skew * sharpe + (kurt - 1.0) / 4.0 * sharpe**2
    if denom <= 0:
        denom = 1e-12
    se = math.sqrt(denom / (n - 1))

    dsr = float(stats.norm.cdf((sharpe - sr_star) / se)) if se > 0 else 0.0

    return DsrResult(
        sharpe=sharpe,
        sharpe_annualised=sharpe * math.sqrt(periods_per_year),
        expected_max_sharpe=sr_star,
        dsr=dsr,
        n_trials=n_trials,
        n_effective_trials=n_eff,
        n_observations=n,
        skew=skew,
        kurtosis=kurt,
    )


def effective_trial_count(param_hashes: list[str]) -> int:
    """Distinct configurations tried.

    Re-running the identical parameter set does not constitute another
    independent search, so DSR should not be penalised for it — but every
    genuinely different configuration counts, including those from
    walk-forward folds and plateau probes.
    """
    return len(set(param_hashes))


@dataclass(frozen=True)
class PboResult:
    pbo: float
    n_splits: int
    n_blocks: int
    n_trials: int
    median_logit: float
    oos_ranks: list[float]

    def as_dict(self) -> dict:
        d = {k: getattr(self, k) for k in self.__dataclass_fields__}
        d["oos_ranks"] = list(self.oos_ranks)[:200]     # keep the report readable
        return d


def probability_of_backtest_overfitting(
    performance: np.ndarray,
    n_blocks: int = 16,
    max_splits: int = 5000,
    rng_seed: int = 0,
) -> PboResult:
    """PBO via CSCV.

    ``performance`` is a (observations x trials) matrix — typically per-block
    Sharpe or per-period returns for every trial in the study.

    The procedure: cut the observations into S blocks; for every way of
    splitting those blocks into equal in-sample and out-of-sample halves, find
    the trial that wins in-sample and record where it ranks out-of-sample. PBO
    is the fraction of splits where that winner lands in the bottom half.

    PBO near 0.5 means the selection procedure carries no information. Note it
    measures the *procedure*, not any single strategy: a low PBO says "picking
    the in-sample best tends to work here", which is exactly the claim a
    parameter search makes.
    """
    M = np.asarray(performance, dtype="float64")
    if M.ndim != 2 or M.shape[1] < 2:
        raise ValueError("performance must be a 2-D (observations x trials) matrix "
                         "with at least 2 trials")
    if n_blocks % 2 != 0:
        raise ValueError("n_blocks must be even so it can split into equal halves")

    n_obs, n_trials = M.shape
    if n_obs < n_blocks:
        n_blocks = max(2, (n_obs // 2) * 2)

    blocks = np.array_split(np.arange(n_obs), n_blocks)
    half = n_blocks // 2

    combos = list(itertools.combinations(range(n_blocks), half))
    if len(combos) > max_splits:
        rng = np.random.default_rng(rng_seed)
        idx = rng.choice(len(combos), size=max_splits, replace=False)
        combos = [combos[i] for i in idx]

    logits: list[float] = []
    ranks: list[float] = []

    for is_blocks in combos:
        is_set = set(is_blocks)
        is_rows = np.concatenate([blocks[b] for b in is_blocks])
        oos_rows = np.concatenate([blocks[b] for b in range(n_blocks) if b not in is_set])

        is_perf = np.nanmean(M[is_rows, :], axis=0)
        oos_perf = np.nanmean(M[oos_rows, :], axis=0)
        if np.all(np.isnan(is_perf)):
            continue

        best = int(np.nanargmax(is_perf))
        # Relative rank of the in-sample winner among out-of-sample results.
        order = stats.rankdata(oos_perf, method="average")
        rank = float(order[best] / (n_trials + 1))
        ranks.append(rank)

        rank = min(max(rank, 1e-9), 1 - 1e-9)
        logits.append(math.log(rank / (1.0 - rank)))

    if not logits:
        return PboResult(1.0, 0, n_blocks, n_trials, 0.0, [])

    # A non-positive logit means the in-sample winner ranked at or below the
    # out-of-sample median — i.e. the selection did not survive.
    pbo = sum(1 for lg in logits if lg <= 0) / len(logits)

    return PboResult(
        pbo=pbo,
        n_splits=len(logits),
        n_blocks=n_blocks,
        n_trials=n_trials,
        median_logit=float(np.median(logits)),
        oos_ranks=ranks,
    )


@dataclass(frozen=True)
class PboInterval:
    """PBO with an honest uncertainty band."""
    pbo: float
    p05: float
    p95: float
    sd: float
    n_resamples: int
    n_trials: int
    n_observations: int

    @property
    def is_conclusive(self) -> bool:
        """Whether the interval is tight enough to support a pass/fail gate.

        A band wider than 0.3 spans "clearly fine" to "clearly overfit", and a
        point estimate from it means very little.
        """
        return (self.p95 - self.p05) <= 0.30

    def as_dict(self) -> dict:
        d = {k: getattr(self, k) for k in self.__dataclass_fields__}
        d["is_conclusive"] = self.is_conclusive
        return d


def pbo_with_uncertainty(
    performance: np.ndarray,
    n_blocks: int = 16,
    max_splits: int = 2000,
    n_resamples: int = 40,
    rng_seed: int = 0,
) -> PboInterval:
    """PBO as an interval rather than a point estimate.

    Measured on synthetic pure noise, PBO has a standard deviation around 0.21
    with 50 trials over 320 observations — so a single figure can land anywhere
    from 0.08 to 0.81 on data with no edge whatsoever. Reporting one number
    would give false precision to a gate that decides whether real money gets
    traded.

    The band comes from *subsampling the observation window* — each resample
    drops a random quarter of the time blocks and recomputes. That answers the
    question that actually matters: "how much does this verdict depend on the
    particular stretch of history we happened to get?"

    Note it deliberately does NOT bootstrap the trial population. Resampling
    trials with replacement drops the winning configuration entirely about a
    third of the time, which measures "what if we had never tried the good
    parameters" — a different question, and one that makes a genuine edge look
    inconclusive.
    """
    M = np.asarray(performance, dtype="float64")
    rng = np.random.default_rng(rng_seed)
    n_trials = M.shape[1]
    n_obs = M.shape[0]

    point = probability_of_backtest_overfitting(M, n_blocks, max_splits, rng_seed).pbo

    keep = max(n_blocks, int(n_obs * 0.75))
    draws: list[float] = []
    for i in range(n_resamples):
        if keep >= n_obs:
            break
        rows = np.sort(rng.choice(n_obs, size=keep, replace=False))
        try:
            draws.append(probability_of_backtest_overfitting(
                M[rows, :], n_blocks, max(200, max_splits // 4), rng_seed + i + 1).pbo)
        except ValueError:
            continue

    if not draws:
        return PboInterval(point, point, point, 0.0, 0, n_trials, M.shape[0])

    arr = np.asarray(draws)
    return PboInterval(
        pbo=point,
        p05=float(np.percentile(arr, 5)),
        p95=float(np.percentile(arr, 95)),
        sd=float(arr.std(ddof=1)) if len(arr) > 1 else 0.0,
        n_resamples=len(arr),
        n_trials=n_trials,
        n_observations=M.shape[0],
    )


def build_performance_matrix(
    trial_returns: dict[str, pd.Series], n_blocks: int = 16
) -> tuple[np.ndarray, list[str]]:
    """Turn per-trial return series into the (blocks x trials) matrix CSCV wants.

    Trials are aligned on the union of their timestamps so every column covers
    the same period; a trial that produced no return on a given day contributes
    zero for that day, which is what "flat" means.
    """
    if not trial_returns:
        raise ValueError("no trial returns supplied")
    labels = list(trial_returns)
    frame = pd.DataFrame({k: v for k, v in trial_returns.items()}).sort_index()
    frame = frame.fillna(0.0)

    blocks = np.array_split(np.arange(len(frame)), min(n_blocks, max(2, len(frame))))
    rows = [frame.iloc[b].mean(axis=0).to_numpy() for b in blocks if len(b)]
    return np.vstack(rows), labels
