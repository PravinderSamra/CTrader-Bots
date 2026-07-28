"""``engine`` command-line entrypoint (build-spec §15).

Every subcommand takes ``--config studies/<name>/study.yaml``, is idempotent and
resumable, and exits non-zero on failure. No prompts anywhere except the explicit
``--confirm`` guard on ``holdout`` — the engine is designed to be agent-operated.

Implemented so far (milestone M1, no credentials or network required):
  data-prepare, validate-config, status

Stubbed with a clear message (need a host with cTrader connectivity — see
03-Verification-Findings §2.1):
  compile, smoke, optimise, wfa, validate, holdout, report
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from engine import __version__
from engine.config import ConfigError, load_search_space, load_study
from engine.data import DataError, prepare

REPO_ROOT_MARKER = "Backtesting Engine"

_NEEDS_HOST = (
    "'{cmd}' needs a host with direct TCP access to the cTrader servers "
    "(ports 5035/5036). It cannot run in a sandboxed web session — see "
    "Backtesting Engine/03-Verification-Findings.md §2.1. Not yet implemented."
)


def _repo_root(config_path: Path) -> Path:
    """Walk up from the study config to the repository root."""
    for parent in config_path.resolve().parents:
        if (parent / REPO_ROOT_MARKER).is_dir():
            return parent
    raise ConfigError(
        f"could not locate the repo root above {config_path} "
        f"(expected a '{REPO_ROOT_MARKER}' directory)"
    )


def cmd_validate_config(args: argparse.Namespace) -> int:
    study = load_study(args.config)
    print(f"study            : {study.study}")
    print(f"bot              : {study.bot.source} ({study.bot.class_name}, {study.bot.dotnet_target})")
    print(f"market           : {study.market.symbol} @ {study.market.period}")
    print(f"console image    : ghcr.io/spotware/ctrader-console:{study.ctrader_console_tag}")
    print(f"data window      : {study.windows.data_start} → holdout from {study.windows.holdout_start}")
    print(f"wfa              : {study.windows.wfa.mode} IS={study.windows.wfa.is_months}m "
          f"OOS={study.windows.wfa.oos_months}m step={study.windows.wfa.step_months}m")
    print(f"gates            : min_trades/yr={study.gates.min_trades_per_year} "
          f"maxDD={study.gates.max_dd_pct}% PF>={study.gates.min_pf} "
          f"WFE>={study.gates.wfe_min} DSR>={study.gates.dsr_min} PBO<={study.gates.pbo_max}")

    space_path = study.study_dir / "search_space.yaml"
    if space_path.is_file():
        space = load_search_space(space_path)
        print(f"search space     : {space.effective_dimensions} dimensions, "
              f"{len(space.fixed)} fixed, {len(space.constraints)} constraints")
        for name, p in space.search.items():
            rng = (f"[{p.low:g}, {p.high:g}]" + (f" step {p.step:g}" if p.step else "")
                   if p.type in ("float", "int") else
                   (str(p.choices) if p.type == "cat" else "{true, false}"))
            cond = f"  (only when {p.condition})" if p.condition else ""
            print(f"  - {name}: {p.type} {rng}{cond}")
    else:
        print(f"search space     : not present at {space_path}")

    print("\nconfig OK")
    return 0


def cmd_data_prepare(args: argparse.Namespace) -> int:
    study = load_study(args.config)
    repo_root = _repo_root(Path(args.config))
    out_root = repo_root / REPO_ROOT_MARKER / "data" / "prepared"

    manifest = prepare(
        data_glob=study.market.data_glob,
        repo_root=repo_root,
        out_root=out_root,
        symbol=study.market.symbol,
        data_start=study.windows.data_start,
        holdout_start=study.windows.holdout_start,
        allow_dirty=args.allow_dirty,
    )

    rows = manifest["rows"]
    print(f"prepared {rows['total']:,} bars for {manifest['symbol']} "
          f"(hash {manifest['data_hash']})")
    print(f"  in-sample : {rows['insample']:,} bars  → insample.csv")
    print(f"  holdout   : {rows['holdout']:,} bars  → holdout.csv  "
          f"(fenced off until Stage 5)")
    print(f"  audit     : {'PASS' if manifest['audit']['passed'] else 'FAIL'}, "
          f"{len(manifest['audit']['warnings'])} warning(s)")
    for w in manifest["audit"]["warnings"]:
        print(f"    ! {w}")
    print(f"  output    : {manifest['out_dir']}")
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    """Machine-readable stage completion — agents poll this."""
    study = load_study(args.config)
    runs = study.runs_dir
    repo_root = _repo_root(Path(args.config))
    prepared_root = repo_root / REPO_ROOT_MARKER / "data" / "prepared" / study.market.symbol

    prepared = sorted(p.name for p in prepared_root.glob("*/manifest.json") for p in [p.parent]) \
        if prepared_root.is_dir() else []
    ledger = study.study_dir / "HOLDOUT_LEDGER.md"

    state = {
        "study": study.study,
        "engine_version": __version__,
        "stages": {
            "data_prepare": bool(prepared),
            "compile": (runs / "bot.algo").exists(),
            "smoke": (runs / "smoke.json").exists(),
            "optimise": (runs / "stage1_top.json").exists(),
            "wfa": (runs / "wfa.json").exists(),
            "validate": (runs / "verdict.json").exists(),
            "holdout": (runs / "holdout.json").exists(),
            "report": (runs / "report.md").exists(),
        },
        "prepared_data_hashes": prepared,
        "holdout_ledger_present": ledger.exists(),
    }
    print(json.dumps(state, indent=2))
    return 0


def cmd_not_implemented(args: argparse.Namespace) -> int:
    print(_NEEDS_HOST.format(cmd=args.command), file=sys.stderr)
    return 2


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="engine",
        description="Backtesting & optimisation engine for cTrader cBots.",
    )
    p.add_argument("--version", action="version", version=f"engine {__version__}")
    sub = p.add_subparsers(dest="command", required=True)

    def add(name: str, help_: str, fn) -> argparse.ArgumentParser:
        sp = sub.add_parser(name, help=help_)
        sp.add_argument("--config", required=True, help="path to studies/<name>/study.yaml")
        sp.set_defaults(func=fn)
        return sp

    add("validate-config", "Load and fully validate study.yaml + search_space.yaml",
        cmd_validate_config)

    dp = add("data-prepare", "Convert, audit and split market data for the study",
             cmd_data_prepare)
    dp.add_argument("--allow-dirty", action="store_true",
                    help="proceed despite audit failures (understand each one first)")

    add("status", "Machine-readable stage completion (JSON)", cmd_status)

    for name, help_ in [
        ("compile", "Compile the bot .cs to a .algo artefact"),
        ("smoke", "Stage 0 parity and smoke test"),
        ("optimise", "Stage 1 coarse search"),
        ("wfa", "Stage 2 walk-forward analysis"),
        ("validate", "Stages 3-4 plateau, Monte Carlo, overfit statistics, gates"),
        ("report", "Generate the study dossier"),
    ]:
        add(name, help_, cmd_not_implemented)

    ho = add("holdout", "Stage 5 one-shot holdout test (guarded)", cmd_not_implemented)
    ho.add_argument("--confirm", action="store_true", help="required; the holdout is single-use")

    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except (ConfigError, DataError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
