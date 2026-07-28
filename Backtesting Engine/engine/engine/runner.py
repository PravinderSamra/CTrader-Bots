"""Parallel backtest execution with a content-addressed cache (build-spec §6).

The cache is what makes the whole pipeline affordable. Plateau analysis re-runs
points the search already visited, walk-forward re-evaluates stage-1 candidates,
and a resumed study repeats everything it did before a crash — all of which
become free. The key covers every input that can change a result, so a hit is
genuinely the same run rather than approximately the same one.

Failed backtests are recorded as failures. They are never scored as zero: a bot
that throws on 30% of trials would otherwise look like a bot with mediocre
parameters, and the search would happily optimise around the exception.
"""

from __future__ import annotations

import hashlib
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Callable, Iterable

from engine.ctcli import BacktestRequest, CtcliError, CtraderCli, InfraError
from engine.results import BacktestResult


@dataclass(frozen=True)
class RunSpec:
    """One backtest to perform, identified by everything that affects its result."""
    parameters: dict[str, Any]
    csv: Path
    start: date
    end: date
    spread_pips: float
    trial_id: str = ""

    def cache_key(self, algo_hash: str, data_hash: str, balance: float,
                  commission: float) -> str:
        payload = json.dumps({
            "algo": algo_hash,
            "data": data_hash,
            "params": {k: _canonical(v) for k, v in sorted(self.parameters.items())},
            "start": self.start.isoformat(),
            "end": self.end.isoformat(),
            "spread": round(float(self.spread_pips), 6),
            "balance": round(float(balance), 6),
            "commission": round(float(commission), 6),
        }, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(payload.encode()).hexdigest()


def _canonical(value: Any) -> Any:
    """Make parameter values hash-stable across int/float and bool spellings."""
    if isinstance(value, bool):
        return bool(value)
    if isinstance(value, float) and value.is_integer():
        return int(value)
    if isinstance(value, float):
        return round(value, 10)
    return value


@dataclass
class RunOutcome:
    spec: RunSpec
    result: BacktestResult
    cache_hit: bool
    wall_seconds: float
    key: str

    @property
    def ok(self) -> bool:
        return not self.result.failed


class ResultCache:
    """Content-addressed store of canonical results."""

    def __init__(self, root: Path):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def path_for(self, key: str) -> Path:
        return self.root / key[:2] / f"{key}.json"

    def get(self, key: str) -> BacktestResult | None:
        p = self.path_for(key)
        if not p.is_file():
            return None
        try:
            return BacktestResult.from_json(p)
        except (json.JSONDecodeError, KeyError):
            # A truncated cache entry is worth re-running, not crashing over.
            p.unlink(missing_ok=True)
            return None

    def put(self, key: str, result: BacktestResult) -> None:
        p = self.path_for(key)
        p.parent.mkdir(parents=True, exist_ok=True)
        tmp = p.with_suffix(".tmp")
        result.to_json(tmp)
        tmp.replace(p)   # atomic: a killed worker never leaves a partial entry


class Runner:
    """Executes RunSpecs across N workers, consulting the cache first."""

    def __init__(
        self,
        cli: CtraderCli,
        cache: ResultCache,
        algo: Path,
        algo_hash: str,
        data_hash: str,
        symbol: str,
        period: str,
        balance: float,
        commission_per_million: float,
        workdir_root: Path,
        run_log: Path | None = None,
        workers: int = 4,
        retries: int = 2,
    ):
        self.cli = cli
        self.cache = cache
        self.algo = Path(algo)
        self.algo_hash = algo_hash
        self.data_hash = data_hash
        self.symbol = symbol
        self.period = period
        self.balance = balance
        self.commission = commission_per_million
        self.workdir_root = Path(workdir_root)
        self.run_log = run_log
        self.workers = max(1, workers)
        self.retries = retries

    def key_for(self, spec: RunSpec) -> str:
        return spec.cache_key(self.algo_hash, self.data_hash, self.balance, self.commission)

    def run_one(self, spec: RunSpec) -> RunOutcome:
        key = self.key_for(spec)
        cached = self.cache.get(key)
        if cached is not None:
            return RunOutcome(spec, cached, True, 0.0, key)

        request = BacktestRequest(
            algo=self.algo, csv=spec.csv, start=spec.start, end=spec.end,
            symbol=self.symbol, period=self.period, spread_pips=spec.spread_pips,
            balance=self.balance, commission_per_million=self.commission,
            parameters=spec.parameters,
        )

        started = time.monotonic()
        workdir = self.workdir_root / key[:12]
        last_infra_error: Exception | None = None
        result: BacktestResult | None = None

        for attempt in range(self.retries + 1):
            try:
                result = self.cli.run_backtest(request, workdir, self.balance)
                break
            except InfraError as exc:
                # Infrastructure only. A bot exception is a real answer and is
                # never retried — it would just cost time to learn the same thing.
                last_infra_error = exc
                if attempt < self.retries:
                    time.sleep(2 ** (attempt + 1))
            except CtcliError as exc:
                result = _failed(str(exc))
                break

        if result is None:
            result = _failed(f"infrastructure failure after {self.retries} retries: "
                             f"{last_infra_error}")

        elapsed = time.monotonic() - started
        if not result.failed:
            self.cache.put(key, result)

        outcome = RunOutcome(spec, result, False, elapsed, key)
        self._log(outcome)
        return outcome

    def run_many(
        self, specs: Iterable[RunSpec], on_result: Callable[[RunOutcome], None] | None = None
    ) -> list[RunOutcome]:
        specs = list(specs)
        outcomes: list[RunOutcome] = []
        with ThreadPoolExecutor(max_workers=self.workers) as pool:
            futures = {pool.submit(self.run_one, s): s for s in specs}
            for fut in as_completed(futures):
                outcome = fut.result()
                outcomes.append(outcome)
                if on_result:
                    on_result(outcome)
        return outcomes

    def _log(self, outcome: RunOutcome) -> None:
        if not self.run_log:
            return
        self.run_log.parent.mkdir(parents=True, exist_ok=True)
        with self.run_log.open("a") as fh:
            fh.write(json.dumps({
                "trial_id": outcome.spec.trial_id,
                "key": outcome.key,
                "cache_hit": outcome.cache_hit,
                "wall_seconds": round(outcome.wall_seconds, 2),
                "outcome": "FAILED" if outcome.result.failed else "OK",
                "trades": len(outcome.result.trades),
                "excerpt": outcome.result.failure_excerpt[:300],
            }) + "\n")


def _failed(message: str) -> BacktestResult:
    import pandas as pd
    return BacktestResult(
        trades=[], equity_curve=pd.Series(dtype="float64"), summary={},
        equity_source="none", failed=True, failure_excerpt=message,
    )


def throughput_report(outcomes: list[RunOutcome]) -> dict:
    """Measured runs/hour — the M3 gate before any budget is trusted.

    Every budget in study.yaml is provisional until this number exists
    (03-Verification-Findings §4.4).
    """
    real = [o for o in outcomes if not o.cache_hit]
    if not real:
        return {"measured_runs": 0, "note": "all results served from cache"}
    times = sorted(o.wall_seconds for o in real)
    total = sum(times)
    median = times[len(times) // 2]
    return {
        "measured_runs": len(real),
        "cache_hits": len(outcomes) - len(real),
        "median_seconds": round(median, 1),
        "mean_seconds": round(total / len(real), 1),
        "slowest_seconds": round(times[-1], 1),
        "runs_per_hour_per_worker": round(3600 / median, 1) if median else None,
        "failures": sum(1 for o in real if o.result.failed),
    }
