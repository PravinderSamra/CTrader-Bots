#!/usr/bin/env python3
"""Validate every strategy's metadata.json and regenerate library_index.csv.

Run from the library root:
    python3 _index/build_index.py

Exits non-zero if any entry fails schema validation, so it can be wired into a
pre-commit hook. jsonschema is optional; without it, structural validation is
skipped and only the index is rebuilt.
"""

import csv
import glob
import json
import sys

SCHEMA_PATH = "_schema/metadata.schema.json"
INDEX_PATH = "_index/library_index.csv"

COLUMNS = [
    "id", "title", "strategy_type", "asset_classes", "complexity_score",
    "execution_type", "requires_machine_learning", "evidence_grade",
    "holding_period", "directionality", "capacity", "decay_status",
    "primary_source_url", "path",
]


def main() -> int:
    try:
        import jsonschema
    except ImportError:
        jsonschema = None
        print("note: jsonschema not installed - skipping schema validation")

    schema = json.load(open(SCHEMA_PATH))
    files = sorted(glob.glob("strategies/*/*/metadata.json"))
    if not files:
        print("error: no metadata.json found under strategies/")
        return 1

    rows, failures = [], 0
    for f in files:
        try:
            d = json.load(open(f))
        except json.JSONDecodeError as e:
            print(f"INVALID JSON  {f}: {e}")
            failures += 1
            continue

        if jsonschema is not None:
            try:
                jsonschema.validate(d, schema)
            except jsonschema.ValidationError as e:
                print(f"SCHEMA FAIL   {f}: {e.message}")
                failures += 1
                continue

        # The four required files must all be present.
        folder = f.rsplit("/", 1)[0]
        required = [
            "research_paper_or_source.md",
            "backtest_and_data_summary.md",
            "source_or_pseudo_code.txt",
            "metadata.json",
        ]
        missing = [r for r in required if not glob.glob(f"{folder}/{r}")]
        if missing:
            print(f"MISSING FILES {folder}: {', '.join(missing)}")
            failures += 1
            continue

        print(f"VALID         {f}")
        rows.append(d)

    with open(INDEX_PATH, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(COLUMNS)
        for d in rows:
            primary = next(
                (s["url"] for s in d["sources"] if s.get("verified_in_session")),
                d["sources"][0].get("url", ""),
            )
            w.writerow([
                d["id"], d["title"], d["strategy_type"],
                "|".join(d["asset_classes"]), d["complexity_score"],
                d["execution_type"], d["requires_machine_learning"],
                d["evidence_grade"], d.get("holding_period", ""),
                d.get("directionality", ""), d.get("capacity", ""),
                d.get("decay_status", ""), primary,
                f"strategies/{d['strategy_type']}/{d['slug']}/",
            ])

    print(f"\n{len(rows)} entries indexed -> {INDEX_PATH}")
    if failures:
        print(f"{failures} entries FAILED validation")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
