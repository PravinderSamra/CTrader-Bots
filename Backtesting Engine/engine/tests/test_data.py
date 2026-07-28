"""Data preparation and audit tests (build-spec §16.1)."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pandas as pd
import pytest

from engine import data
from engine.data import DataError

REPO = Path(__file__).resolve().parents[3]


def synthetic(n=200, start="2024-01-01T00:00:00Z") -> pd.DataFrame:
    idx = pd.date_range(start, periods=n, freq="1min", tz="UTC")
    base = 2000.0
    return pd.DataFrame({
        "datetime": idx,
        "open": base, "high": base + 1.0, "low": base - 1.0, "close": base + 0.5,
        "volume": 100,
    })


def write_csv(df: pd.DataFrame, path: Path) -> None:
    out = df.copy()
    out["datetime"] = out["datetime"].dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    out.to_csv(path, index=False)


class TestAudit:
    def test_clean_data_passes(self):
        res = data.audit(synthetic())
        assert res.ok
        assert res.failures == []

    def test_duplicate_timestamps_fail(self):
        df = pd.concat([synthetic(10), synthetic(10)]).sort_values("datetime").reset_index(drop=True)
        res = data.audit(df)
        assert not res.ok
        assert any("duplicate" in f for f in res.failures)

    def test_high_below_open_fails(self):
        df = synthetic(10)
        df.loc[5, "high"] = df.loc[5, "open"] - 5.0
        res = data.audit(df)
        assert any("high >= max" in f for f in res.failures)

    def test_low_above_close_fails(self):
        df = synthetic(10)
        df.loc[3, "low"] = df.loc[3, "close"] + 5.0
        assert any("low <= min" in f for f in data.audit(df).failures)

    def test_non_positive_price_fails(self):
        df = synthetic(10)
        df.loc[2, ["open", "high", "low", "close"]] = 0.0
        assert any("non-positive" in f for f in data.audit(df).failures)

    def test_weekend_gap_is_not_warned_about(self):
        # Friday 21:00 close -> Sunday 22:00 open is normal, not a defect.
        fri = synthetic(60, start="2024-01-05T20:00:00Z")
        sun = synthetic(60, start="2024-01-07T22:00:00Z")
        res = data.audit(pd.concat([fri, sun]).reset_index(drop=True))
        assert res.gaps is None or len(res.gaps) == 0

    def test_midweek_gap_is_warned_about(self):
        a = synthetic(60, start="2024-01-09T00:00:00Z")
        b = synthetic(60, start="2024-01-09T12:00:00Z")
        res = data.audit(pd.concat([a, b]).reset_index(drop=True))
        assert res.gaps is not None and len(res.gaps) == 1

    def test_per_year_counts(self):
        res = data.audit(synthetic(100))
        assert res.per_year == {2024: 100}


class TestPrepare:
    def test_splits_at_holdout_and_writes_manifest(self, tmp_path):
        repo = tmp_path / "repo"
        (repo / "d").mkdir(parents=True)
        df = synthetic(n=60 * 24 * 10, start="2024-01-01T00:00:00Z")  # 10 days
        write_csv(df, repo / "d" / "X_2024.csv")

        manifest = data.prepare(
            data_glob="d/*.csv", repo_root=repo, out_root=tmp_path / "out",
            symbol="XAUUSD", data_start=date(2024, 1, 1), holdout_start=date(2024, 1, 8),
        )

        out = Path(manifest["out_dir"])
        assert (out / "insample.csv").is_file()
        assert (out / "holdout.csv").is_file()
        assert (out / "audit.md").is_file()
        assert (out / "manifest.json").is_file()
        assert manifest["rows"]["insample"] + manifest["rows"]["holdout"] == manifest["rows"]["total"]

        # The CLI wants no header and "yyyy-MM-dd HH:mm:ss".
        first = (out / "insample.csv").read_text().splitlines()[0]
        assert first.startswith("2024-01-01 00:00:00,")
        assert "datetime" not in first

        # The holdout must start exactly at holdout_start, never earlier.
        holdout_first = (out / "holdout.csv").read_text().splitlines()[0]
        assert holdout_first.startswith("2024-01-08 00:00:00,")

    def test_dirty_data_blocks_unless_allowed(self, tmp_path):
        repo = tmp_path / "repo"
        (repo / "d").mkdir(parents=True)
        df = synthetic(500)
        df.loc[10, "high"] = 0.0
        write_csv(df, repo / "d" / "X.csv")

        kwargs = dict(
            data_glob="d/*.csv", repo_root=repo, out_root=tmp_path / "out", symbol="X",
            data_start=date(2024, 1, 1), holdout_start=date(2024, 1, 1, ),
        )
        kwargs["holdout_start"] = date(2024, 1, 1)
        with pytest.raises(DataError, match="audit failed"):
            data.prepare(**kwargs)

    def test_missing_files_raise(self, tmp_path):
        with pytest.raises(DataError, match="no data files matched"):
            data.prepare(
                data_glob="nope/*.csv", repo_root=tmp_path, out_root=tmp_path / "o",
                symbol="X", data_start=date(2024, 1, 1), holdout_start=date(2024, 6, 1),
            )

    def test_hash_is_stable_for_identical_data(self, tmp_path):
        repo = tmp_path / "repo"
        (repo / "d").mkdir(parents=True)
        write_csv(synthetic(2000), repo / "d" / "X.csv")
        common = dict(
            data_glob="d/*.csv", repo_root=repo, symbol="X",
            data_start=date(2024, 1, 1), holdout_start=date(2024, 1, 2),
        )
        a = data.prepare(out_root=tmp_path / "a", **common)
        b = data.prepare(out_root=tmp_path / "b", **common)
        assert a["data_hash"] == b["data_hash"]


class TestResample:
    def test_daily_resample_aggregates_correctly(self):
        df = synthetic(60 * 24 * 3)
        d1 = data.resample(df, "1D")
        assert len(d1) == 3
        assert d1["volume"].iloc[0] == 60 * 24 * 100
        assert d1["high"].iloc[0] == pytest.approx(2001.0)


@pytest.mark.skipif(
    not (REPO / "XAUUSD historical Pricing data" / "data" / "XAUUSD_M_1_2021.csv").is_file(),
    reason="repo market data not present",
)
class TestRealRepoData:
    """Guards against the real data drifting from what the study assumes."""

    def test_2021_starts_mid_july_not_january(self):
        df = pd.read_csv(REPO / "XAUUSD historical Pricing data" / "data" / "XAUUSD_M_1_2021.csv",
                         nrows=1)
        assert df["datetime"].iloc[0].startswith("2021-07-18"), (
            "study.yaml's data_start assumes the series begins 2021-07-18"
        )
