"""cTrader CLI wrapper (build-spec §4).

Three interchangeable backends, all producing the same ``BacktestResult``:

  * ``NativeBackend``  — ``ctrader-cli`` as shipped with cTrader Desktop 4.8+.
    Preferred where available: no Docker, and connectivity already works.
  * ``DockerBackend``  — ``ghcr.io/spotware/ctrader-console:<pinned tag>``.
    For Linux hosts and VPSes.
  * ``FixtureBackend`` — replays recorded runs from disk. This is what lets every
    module above the execution layer be built and tested with no credentials and
    no network, which matters because real backtests cannot run in a sandboxed
    web session at all (03-Verification-Findings §2.1).

Verified against the real image's ``--help`` (5.9.0.0):

    backtest <cbot.algo> [<params.cbotset>] --start=<dd/MM/yyyy> --end=<dd/MM/yyyy>
        --data-mode=<ticks|m1|m1-csv|open> [--data-file=<path>] [--balance=<n>]
        [--commission=<n>] [--spread=<pips>] [--report=<path>] [--report-json=<path>]
        --ctid=<cTID> --pwd-file=<path> --account=<n> --symbol=<n> --period=<p>

Two details that bite:
  * dates are ``dd/MM/yyyy``, not ISO;
  * batch mode requires ``--pwd-file``. Passing ``--password`` inline routes the
    process into the *interactive shell*, which will hang an agent forever.

The Events.json/Report.json field names are NOT yet verified — they need a
connected host. Every access goes through ``_pick()`` so the mapping is in one
place and a schema surprise produces a clear error rather than a silent zero.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Sequence

import pandas as pd

from engine.results import BacktestResult, Trade, TradeSlice, reconstruct_equity

CLI_DATE_FORMAT = "%d/%m/%Y"
DEFAULT_TIMEOUT_S = 30 * 60


class CtcliError(RuntimeError):
    """A backtest could not be run, or its output could not be parsed."""


class InfraError(CtcliError):
    """Docker/network class failure — worth retrying. Bot errors are not."""


@dataclass(frozen=True)
class Credentials:
    ctid: str
    account_id: str
    password: str
    broker: str | None = None

    @classmethod
    def from_env(cls) -> "Credentials":
        """Read credentials from the environment variables this repo already uses.

        The password is never passed on a command line — it is written to a 0600
        file for ``--pwd-file`` (see ``pwd_file()``).
        """
        missing = [v for v in ("CTRADER_CID", "CTRADER_ACCOUNT_ID", "CTRADER_PASSWORD")
                   if not os.environ.get(v)]
        if missing:
            raise CtcliError(
                f"missing credential environment variables: {', '.join(missing)}. "
                "Set CTRADER_CID (cTID or email), CTRADER_ACCOUNT_ID and "
                "CTRADER_PASSWORD before running any backtest."
            )
        return cls(
            ctid=os.environ["CTRADER_CID"],
            account_id=os.environ["CTRADER_ACCOUNT_ID"],
            password=os.environ["CTRADER_PASSWORD"],
            broker=os.environ.get("CTRADER_BROKER") or None,
        )


@dataclass(frozen=True)
class BacktestRequest:
    algo: Path
    csv: Path
    start: date
    end: date
    symbol: str
    period: str
    spread_pips: float
    balance: float
    commission_per_million: float = 0.0
    parameters: dict[str, Any] | None = None
    cbotset: Path | None = None

    def cli_args(self, report_json: Path, report_html: Path) -> list[str]:
        args = ["backtest", str(self.algo)]
        if self.cbotset:
            args.append(str(self.cbotset))
        args += [
            f"--start={self.start.strftime(CLI_DATE_FORMAT)}",
            f"--end={self.end.strftime(CLI_DATE_FORMAT)}",
            "--data-mode=m1-csv",
            f"--data-file={self.csv}",
            f"--symbol={self.symbol}",
            f"--period={self.period}",
            f"--spread={self.spread_pips}",
            f"--balance={self.balance}",
            f"--commission={self.commission_per_million}",
            f"--report-json={report_json}",
            f"--report={report_html}",
        ]
        # Parameter injection without a .cbotset file. The image's options
        # reference lists `--CustomParameter1=<value>  set any cBot parameter by
        # name`, which reads as a placeholder for the parameter's own name.
        # UNVERIFIED — confirm on a connected host before trusting a search
        # (DECISIONS.md "Still unverified" #2).
        for key, value in (self.parameters or {}).items():
            args.append(f"--{key}={_format_param(value)}")
        return args


def _format_param(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


class Backend(ABC):
    """Runs an argv against some cTrader CLI and returns (rc, stdout, workdir)."""

    @abstractmethod
    def invoke(self, args: Sequence[str], workdir: Path, timeout: int) -> tuple[int, str]:
        ...


class NativeBackend(Backend):
    """``ctrader-cli`` installed locally (cTrader Desktop 4.8+)."""

    def __init__(self, executable: str | None = None):
        exe = executable or shutil.which("ctrader-cli")
        if not exe:
            raise CtcliError(
                "ctrader-cli not found on PATH. It ships with cTrader Desktop 4.8+; "
                "pass --cli-path, or use the Docker backend."
            )
        self.executable = exe

    def invoke(self, args, workdir, timeout):
        try:
            proc = subprocess.run(
                [self.executable, *args], cwd=workdir, capture_output=True,
                text=True, timeout=timeout,
            )
        except subprocess.TimeoutExpired as exc:
            raise InfraError(f"ctrader-cli timed out after {timeout}s") from exc
        except OSError as exc:
            raise InfraError(f"could not launch ctrader-cli: {exc}") from exc
        return proc.returncode, proc.stdout + proc.stderr


class DockerBackend(Backend):
    """The official console image, one container per run."""

    def __init__(self, tag: str, sudo: bool = False):
        self.image = f"ghcr.io/spotware/ctrader-console:{tag}"
        self.sudo = sudo

    def invoke(self, args, workdir, timeout):
        docker = (["sudo", "-n"] if self.sudo else []) + ["docker"]
        cmd = [
            *docker, "run", "--rm",
            "-v", f"{workdir}:/work",
            "-w", "/work",
            self.image, *args,
        ]
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        except subprocess.TimeoutExpired as exc:
            raise InfraError(f"docker backtest timed out after {timeout}s") from exc
        except OSError as exc:
            raise InfraError(f"could not launch docker: {exc}") from exc
        out = proc.stdout + proc.stderr
        if proc.returncode != 0 and _is_infra_failure(out):
            raise InfraError(out.strip()[:500])
        return proc.returncode, out


def _is_infra_failure(output: str) -> bool:
    """Distinguish "retry this" from "the bot threw".

    Retrying a bot exception just burns time and produces the same answer.
    """
    lowered = output.lower()
    return any(s in lowered for s in (
        "connection can't be established", "docker api", "503 service unavailable",
        "temporary failure in name resolution", "connection reset", "i/o timeout",
        "daemon is not running",
    ))


class FixtureBackend(Backend):
    """Replays recorded CLI output — no credentials, no network.

    Fixtures live under ``<root>/<key>/`` and contain the same files a real run
    leaves behind. Record them once on a connected host, then every module above
    this line is developable and testable anywhere.
    """

    def __init__(self, root: Path, key_fn=None):
        self.root = Path(root)
        self.key_fn = key_fn

    def invoke(self, args, workdir, timeout):
        key = self.key_fn(args) if self.key_fn else "default"
        src = self.root / key
        if not src.is_dir():
            raise CtcliError(
                f"no fixture at {src}. Record one on a connected host, or point "
                "--fixtures at a directory that has it."
            )
        for f in src.iterdir():
            shutil.copy2(f, workdir / f.name)
        return 0, (src / "stdout.txt").read_text() if (src / "stdout.txt").is_file() else ""


def pwd_file(password: str, directory: Path) -> Path:
    """Write the password to a 0600 file for ``--pwd-file``.

    Inline ``--password`` is not an option: it routes the CLI into interactive
    mode, which blocks forever under an agent.
    """
    path = directory / "pwd.txt"
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w") as fh:
        fh.write(password)
    return path


def _pick(node: dict, *names: str, default=None, required=False, where="") -> Any:
    """Read the first present key from a set of candidate spellings.

    The CLI's JSON schema is unverified, so every field access is funnelled
    through here: when a name turns out to be wrong we get one clear error
    naming the alternatives tried, not a silent zero that quietly corrupts a
    metric.
    """
    for n in names:
        if n in node:
            return node[n]
        for k in node:
            if k.lower().replace("_", "") == n.lower().replace("_", ""):
                return node[k]
    if required:
        raise CtcliError(
            f"{where}: none of {names} present in CLI output. Keys were "
            f"{sorted(node)[:20]}. Update the mapping in ctcli._parse_* and record "
            "the real schema in DECISIONS.md."
        )
    return default


def _ts(value: Any) -> pd.Timestamp:
    return pd.Timestamp(value, tz="UTC") if pd.Timestamp(value).tzinfo is None \
        else pd.Timestamp(value)


def parse_result(
    report_json: Path,
    events_json: Path | None,
    nominal_balance: float,
    symbol: str,
    log_path: Path | None = None,
) -> BacktestResult:
    """Parse CLI output into the canonical result."""
    report = json.loads(Path(report_json).read_text())
    events: list[dict] = []
    if events_json and Path(events_json).is_file():
        raw = json.loads(Path(events_json).read_text())
        events = raw if isinstance(raw, list) else _pick(raw, "events", "Events", default=[])

    slices_by_position: dict[str, list[TradeSlice]] = {}
    opens: dict[str, dict] = {}

    for ev in events:
        kind = str(_pick(ev, "type", "eventType", "Event", default="")).lower()
        pid = str(_pick(ev, "positionId", "PositionId", "id", default=""))
        if not pid:
            continue
        if "open" in kind:
            opens[pid] = ev
        elif "close" in kind:
            slices_by_position.setdefault(pid, []).append(TradeSlice(
                position_id=pid,
                close_time=_ts(_pick(ev, "time", "closeTime", "timestamp", required=True,
                                     where="close event")),
                close_price=float(_pick(ev, "price", "closePrice", default=0.0)),
                volume=float(_pick(ev, "volume", "closedVolume", default=0.0)),
                net_pnl=float(_pick(ev, "netProfit", "pnl", "profit", default=0.0)),
            ))

    trades: list[Trade] = []
    for pid, sl in slices_by_position.items():
        sl.sort(key=lambda s: s.close_time)
        op = opens.get(pid, {})
        total_vol = sum(s.volume for s in sl) or 1.0
        vwap_exit = sum(s.close_price * s.volume for s in sl) / total_vol
        trades.append(Trade(
            position_id=pid,
            symbol=str(_pick(op, "symbol", "symbolName", default=symbol)),
            direction=str(_pick(op, "direction", "tradeSide", "side", default="")).lower(),
            open_time=_ts(_pick(op, "time", "openTime", "timestamp",
                                default=sl[0].close_time)),
            close_time=sl[-1].close_time,
            entry_price=float(_pick(op, "price", "entryPrice", default=0.0)),
            exit_price=vwap_exit,
            volume=sum(s.volume for s in sl),
            gross_pnl=float(sum(s.net_pnl for s in sl)),
            net_pnl=float(sum(s.net_pnl for s in sl)),
            pips=float(_pick(op, "pips", default=0.0)),
            label=str(_pick(op, "label", "comment", default="")),
            slices=sl,
        ))
    trades.sort(key=lambda t: t.open_time)

    equity, source = _equity_from(events, trades, nominal_balance)

    return BacktestResult(
        trades=trades,
        equity_curve=equity,
        summary=report if isinstance(report, dict) else {"raw": report},
        equity_source=source,
        log_path=str(log_path) if log_path else None,
    )


def _equity_from(
    events: list[dict], trades: list[Trade], nominal_balance: float
) -> tuple[pd.Series, str]:
    """Prefer real equity marks; fall back to replaying closed trades.

    Which one was used is recorded on the result and must reach the report's
    LIMITATIONS section — reconstructed equity hides open drawdown and therefore
    flatters Sharpe (01-Research §7.3).
    """
    marks = [
        (_ts(_pick(ev, "time", "timestamp", required=True, where="equity mark")),
         float(_pick(ev, "equity", "Equity", required=True, where="equity mark")))
        for ev in events
        if _pick(ev, "equity", "Equity") is not None
    ]
    if len(marks) >= 2:
        marks.sort(key=lambda m: m[0])
        return pd.Series(
            [v for _, v in marks], index=pd.DatetimeIndex([t for t, _ in marks]),
            dtype="float64",
        ), "marks"
    return reconstruct_equity(trades, nominal_balance), "reconstructed"


class CtraderCli:
    """Runs one backtest and returns a canonical result."""

    def __init__(
        self,
        backend: Backend,
        credentials: Credentials | None = None,
        timeout_s: int = DEFAULT_TIMEOUT_S,
        keep_raw: bool = True,
    ):
        self.backend = backend
        self.credentials = credentials
        self.timeout_s = timeout_s
        self.keep_raw = keep_raw

    def run_backtest(
        self, request: BacktestRequest, workdir: Path, nominal_balance: float
    ) -> BacktestResult:
        workdir = Path(workdir)
        workdir.mkdir(parents=True, exist_ok=True)
        report_json = workdir / "Report.json"
        report_html = workdir / "Report.html"

        args = list(request.cli_args(report_json, report_html))
        if self.credentials:
            pwd = pwd_file(self.credentials.password, workdir)
            args += [
                f"--ctid={self.credentials.ctid}",
                f"--pwd-file={pwd}",
                f"--account={self.credentials.account_id}",
            ]
            if self.credentials.broker:
                args.append(f"--broker={self.credentials.broker}")

        rc, output = self.backend.invoke(args, workdir, self.timeout_s)
        (workdir / "stdout.txt").write_text(output)

        if rc != 0 or not report_json.is_file():
            return BacktestResult(
                trades=[], equity_curve=pd.Series(dtype="float64"),
                summary={}, equity_source="none", failed=True,
                failure_excerpt=output.strip()[-2000:] or f"exit code {rc}, no report written",
                log_path=str(workdir / "stdout.txt"),
            )

        events = workdir / "Events.json"
        result = parse_result(
            report_json, events if events.is_file() else None,
            nominal_balance, request.symbol, workdir / "stdout.txt",
        )
        if not self.keep_raw:
            for f in (report_json, report_html, events):
                f.unlink(missing_ok=True)
        return result


def make_backend(
    tag: str, prefer_native: bool = True, fixtures: Path | None = None, sudo: bool = False
) -> Backend:
    """Pick a backend: fixtures if given, else native if present, else Docker."""
    if fixtures:
        return FixtureBackend(fixtures)
    if prefer_native and shutil.which("ctrader-cli"):
        return NativeBackend()
    return DockerBackend(tag, sudo=sudo)
