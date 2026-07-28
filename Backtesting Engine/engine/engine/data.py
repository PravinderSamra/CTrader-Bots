"""Market-data preparation and audit (build-spec §3).

Converts the repo's M1 CSVs into the format the cTrader CLI's ``--data-mode=m1-csv``
expects, splits them at ``holdout_start`` so the holdout is fenced off on disk from
the first moment, and audits the series for the defects that quietly corrupt a
backtest.

Repo input format:  ``datetime,open,high,low,close,volume`` with header,
ISO-8601 ``2021-07-18T22:00:00Z`` timestamps, volume = tick count.
CLI output format:  no header, ``yyyy-MM-dd HH:mm:ss`` (UTC).

The exact datetime format the CLI accepts could not be verified without server
connectivity (03-Verification-Findings §2.1); ``yyyy-MM-dd HH:mm:ss`` follows the
build spec and must be confirmed in Stage 0 on a connected host.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

import pandas as pd

REQUIRED_COLUMNS = ["datetime", "open", "high", "low", "close", "volume"]
CLI_DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

# A bar whose range exceeds this multiple of the rolling median range is flagged
# for eyeball review (build-spec §3.2).
SPIKE_MULTIPLE = 12.0
SPIKE_WINDOW = 1440  # one trading day of M1 bars


class DataError(RuntimeError):
    """Raised when the data is unusable and --allow-dirty was not given."""


@dataclass
class AuditResult:
    rows: int
    first: pd.Timestamp
    last: pd.Timestamp
    failures: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    per_year: dict[int, int] = field(default_factory=dict)
    gaps: pd.DataFrame | None = None
    spikes: pd.DataFrame | None = None

    @property
    def ok(self) -> bool:
        return not self.failures


def load_raw(data_glob: str, repo_root: Path) -> pd.DataFrame:
    """Load and concatenate every CSV matching ``data_glob``, sorted by time."""
    paths = sorted(repo_root.glob(data_glob))
    if not paths:
        raise DataError(f"no data files matched {data_glob!r} under {repo_root}")
    frames = []
    for p in paths:
        df = pd.read_csv(p)
        missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
        if missing:
            raise DataError(f"{p.name}: missing columns {missing}")
        frames.append(df[REQUIRED_COLUMNS])
    out = pd.concat(frames, ignore_index=True)
    out["datetime"] = pd.to_datetime(out["datetime"], utc=True, format="ISO8601")
    return out.sort_values("datetime", kind="mergesort").reset_index(drop=True)


def audit(df: pd.DataFrame) -> AuditResult:
    """Run the pre-flight data checks. Failures block; warnings inform."""
    res = AuditResult(rows=len(df), first=df["datetime"].iloc[0], last=df["datetime"].iloc[-1])

    dupes = df["datetime"].duplicated().sum()
    if dupes:
        res.failures.append(f"{dupes} duplicate timestamps")

    if not df["datetime"].is_monotonic_increasing:
        res.failures.append("timestamps are not strictly increasing after sort")

    hi = df[["open", "close"]].max(axis=1)
    lo = df[["open", "close"]].min(axis=1)
    bad_high = int((df["high"] < hi - 1e-9).sum())
    bad_low = int((df["low"] > lo + 1e-9).sum())
    if bad_high:
        res.failures.append(f"{bad_high} bars violate high >= max(open, close)")
    if bad_low:
        res.failures.append(f"{bad_low} bars violate low <= min(open, close)")
    non_positive = int((df[["open", "high", "low", "close"]] <= 0).any(axis=1).sum())
    if non_positive:
        res.failures.append(f"{non_positive} bars contain non-positive prices")

    res.per_year = df.groupby(df["datetime"].dt.year).size().to_dict()

    # Gaps: any gap over an hour that is not a weekend break is worth seeing.
    delta = df["datetime"].diff()
    gap_mask = delta > pd.Timedelta(hours=1)
    if gap_mask.any():
        gaps = pd.DataFrame({
            "gap_start": df["datetime"].shift(1)[gap_mask],
            "gap_end": df["datetime"][gap_mask],
            "hours": (delta[gap_mask].dt.total_seconds() / 3600).round(2),
        }).reset_index(drop=True)
        # Weekend closes are expected: Friday close -> Sunday open.
        weekend = gaps["gap_start"].dt.dayofweek == 4
        res.gaps = gaps[~weekend].sort_values("hours", ascending=False).reset_index(drop=True)
        if len(res.gaps):
            res.warnings.append(
                f"{len(res.gaps)} non-weekend gaps > 1h "
                f"(largest {res.gaps['hours'].iloc[0]:.1f}h)"
            )

    bar_range = df["high"] - df["low"]
    median_range = bar_range.rolling(SPIKE_WINDOW, min_periods=60).median()
    spike_mask = (bar_range > SPIKE_MULTIPLE * median_range) & median_range.gt(0)
    if spike_mask.any():
        spikes = df.loc[spike_mask, ["datetime", "open", "high", "low", "close"]].copy()
        spikes["range"] = bar_range[spike_mask]
        spikes["x_median"] = (bar_range[spike_mask] / median_range[spike_mask]).round(1)
        res.spikes = spikes.sort_values("x_median", ascending=False).head(20).reset_index(drop=True)
        res.warnings.append(f"{int(spike_mask.sum())} bars with range > {SPIKE_MULTIPLE}x rolling median")

    return res


def write_audit_report(res: AuditResult, path: Path, symbol: str) -> None:
    lines = [
        f"# Data audit — {symbol}",
        "",
        f"- Rows: **{res.rows:,}**",
        f"- Range: **{res.first:%Y-%m-%d %H:%M} → {res.last:%Y-%m-%d %H:%M}** (UTC)",
        f"- Verdict: **{'PASS' if res.ok else 'FAIL'}**",
        "",
        "## Bars per year",
        "",
        "| Year | Bars |",
        "|---|---|",
    ]
    lines += [f"| {y} | {n:,} |" for y, n in sorted(res.per_year.items())]

    lines += ["", "## Failures", ""]
    lines += [f"- {f}" for f in res.failures] or ["_None._"]

    lines += ["", "## Warnings", ""]
    lines += [f"- {w}" for w in res.warnings] or ["_None._"]

    if res.gaps is not None and len(res.gaps):
        lines += ["", "## Largest non-weekend gaps (top 20)", "",
                  "| Gap start (UTC) | Gap end (UTC) | Hours |", "|---|---|---|"]
        for _, r in res.gaps.head(20).iterrows():
            lines.append(f"| {r.gap_start:%Y-%m-%d %H:%M} | {r.gap_end:%Y-%m-%d %H:%M} | {r.hours} |")

    if res.spikes is not None and len(res.spikes):
        lines += ["", f"## Range spikes (> {SPIKE_MULTIPLE}x rolling median, top 20)", "",
                  "| Time (UTC) | High | Low | Range | x median |", "|---|---|---|---|---|"]
        for _, r in res.spikes.iterrows():
            lines.append(
                f"| {r.datetime:%Y-%m-%d %H:%M} | {r.high} | {r.low} | "
                f"{r['range']:.2f} | {r.x_median} |"
            )

    lines += ["", "---", "",
              "Spikes and gaps are informational: gold genuinely gaps at the weekly open "
              "and spikes on news. Review them, don't reflexively clean them."]
    path.write_text("\n".join(lines) + "\n")


def _to_cli_csv(df: pd.DataFrame, path: Path) -> None:
    out = df.copy()
    out["datetime"] = out["datetime"].dt.strftime(CLI_DATETIME_FORMAT)
    out.to_csv(path, index=False, header=False, columns=REQUIRED_COLUMNS)


def prepare(
    data_glob: str,
    repo_root: Path,
    out_root: Path,
    symbol: str,
    data_start: date,
    holdout_start: date,
    allow_dirty: bool = False,
) -> dict:
    """Convert, audit and split the study's data. Returns the manifest.

    Everything at or after ``holdout_start`` goes into ``holdout.csv`` and is not
    touched again until Stage 5.
    """
    df = load_raw(data_glob, repo_root)
    start_ts = pd.Timestamp(data_start, tz="UTC")
    df = df[df["datetime"] >= start_ts].reset_index(drop=True)
    if df.empty:
        raise DataError(f"no bars at or after data_start={data_start}")

    res = audit(df)
    if not res.ok and not allow_dirty:
        raise DataError(
            "data audit failed:\n  - " + "\n  - ".join(res.failures)
            + "\nRe-run with --allow-dirty only if you understand each failure."
        )

    holdout_ts = pd.Timestamp(holdout_start, tz="UTC")
    insample = df[df["datetime"] < holdout_ts].reset_index(drop=True)
    holdout = df[df["datetime"] >= holdout_ts].reset_index(drop=True)
    if insample.empty:
        raise DataError(f"no in-sample bars before holdout_start={holdout_start}")
    if holdout.empty:
        raise DataError(f"no holdout bars at or after holdout_start={holdout_start}")

    digest = hashlib.sha256(
        pd.util.hash_pandas_object(df, index=False).values.tobytes()
    ).hexdigest()[:12]
    out_dir = out_root / symbol / digest
    out_dir.mkdir(parents=True, exist_ok=True)

    _to_cli_csv(insample, out_dir / "insample.csv")
    _to_cli_csv(holdout, out_dir / "holdout.csv")
    _to_cli_csv(df, out_dir / "full.csv")
    write_audit_report(res, out_dir / "audit.md", symbol)

    manifest = {
        "symbol": symbol,
        "data_hash": digest,
        "source_glob": data_glob,
        "source_files": [p.name for p in sorted(repo_root.glob(data_glob))],
        "datetime_format": CLI_DATETIME_FORMAT,
        "rows": {"total": len(df), "insample": len(insample), "holdout": len(holdout)},
        "range": {
            "first": res.first.isoformat(),
            "last": res.last.isoformat(),
            "holdout_start": holdout_start.isoformat(),
        },
        "audit": {
            "passed": res.ok,
            "failures": res.failures,
            "warnings": res.warnings,
            "allow_dirty": allow_dirty,
        },
        "per_year": {str(k): int(v) for k, v in sorted(res.per_year.items())},
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    manifest["out_dir"] = str(out_dir)
    return manifest


def resample(df: pd.DataFrame, rule: str) -> pd.DataFrame:
    """Resample M1 bars for *analysis only* — the backtester always gets M1."""
    out = (
        df.set_index("datetime")
        .resample(rule, label="left", closed="left")
        .agg({"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
        .dropna()
        .reset_index()
    )
    return out
