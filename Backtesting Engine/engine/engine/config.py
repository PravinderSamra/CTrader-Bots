"""Study and search-space configuration.

Implements build-spec §2.1 (study.yaml) and §5.2 (search_space.yaml), with the
corrections recorded in `03-Verification-Findings.md` §6:

  * ``commission_per_million`` replaces ``commission_per_lot`` — the cTrader CLI's
    ``--commission`` is documented as "commission per million" (§3.3).
  * ``ctrader_console_tag`` is required and must be a pinned tag, never ``latest``
    (§2.3).
  * ``dotnet_target`` defaults to ``net6.0``; the console image ships runtime
    6.0.10 only (§3.2).
  * ``period`` is validated case-sensitively against the CLI's ``periods``
    output — ``D1``/``W1``/``Month1`` are capitalised (§3.6).

The loader validates fully and fails loudly: a study that loads is a study whose
contract has been checked.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any, Literal

import yaml

# `dotnet periods` output from ghcr.io/spotware/ctrader-console:5.9.0.0.
# Case-sensitive on purpose: the CLI's --help text disagrees with reality.
VALID_PERIODS: frozenset[str] = frozenset(
    [f"t{n}" for n in (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 15, 20, 25, 30, 40, 50, 60,
                       80, 90, 100, 150, 200, 250, 300, 500, 750, 1000)]
    + [f"m{n}" for n in (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 15, 20, 30, 45)]
    + [f"h{n}" for n in (1, 2, 3, 4, 6, 8, 12)]
    + ["D1", "D2", "D3", "W1", "Month1"]
)

VALID_DATA_MODES = frozenset({"ticks", "m1", "m1-csv", "open"})

MAX_SEARCH_DIMENSIONS = 10


class ConfigError(ValueError):
    """Raised when a study or search-space file violates its contract."""


def _require(mapping: dict[str, Any], key: str, where: str) -> Any:
    if key not in mapping:
        raise ConfigError(f"{where}: missing required key '{key}'")
    return mapping[key]


def _as_date(value: Any, where: str) -> date:
    if isinstance(value, date):
        return value
    try:
        return date.fromisoformat(str(value))
    except ValueError as exc:
        raise ConfigError(f"{where}: expected an ISO date (yyyy-mm-dd), got {value!r}") from exc


@dataclass(frozen=True)
class BotConfig:
    source: str
    class_name: str
    dotnet_target: str = "net6.0"


@dataclass(frozen=True)
class MarketConfig:
    symbol: str
    period: str
    data_glob: str


@dataclass(frozen=True)
class AccountConfig:
    nominal_balance: float
    currency: str
    risk_per_trade: float


@dataclass(frozen=True)
class SlippageModel:
    dist: str
    median_pips: float
    p95_pips: float


@dataclass(frozen=True)
class ExecutionConfig:
    spread_pips: dict[str, float]
    commission_per_million: float
    slippage_model: SlippageModel

    def spread(self, profile: str) -> float:
        if profile not in self.spread_pips:
            raise ConfigError(
                f"execution.spread_pips: no profile {profile!r} "
                f"(have: {sorted(self.spread_pips)})"
            )
        return self.spread_pips[profile]


@dataclass(frozen=True)
class WfaConfig:
    mode: Literal["rolling", "anchored"]
    is_months: int
    oos_months: int
    step_months: int


@dataclass(frozen=True)
class WindowsConfig:
    data_start: date
    holdout_start: date
    wfa: WfaConfig


@dataclass(frozen=True)
class BudgetsConfig:
    stage1_random: int
    stage1_tpe: int
    wfa_trials_per_fold: int
    mc_resamples: int


@dataclass(frozen=True)
class GatesConfig:
    min_trades_per_year: int
    max_dd_pct: float
    min_pf: float
    wfe_min: float
    dsr_min: float
    pbo_max: float
    plateau_retention: float


@dataclass(frozen=True)
class StudyConfig:
    study: str
    bot: BotConfig
    market: MarketConfig
    account: AccountConfig
    execution: ExecutionConfig
    windows: WindowsConfig
    budgets: BudgetsConfig
    gates: GatesConfig
    ctrader_console_tag: str
    path: Path

    @property
    def study_dir(self) -> Path:
        return self.path.parent

    @property
    def runs_dir(self) -> Path:
        return self.study_dir / "runs"


# Defaults per 01-Research-Findings §4.3 / §5, with the min_trades correction
# from 03-Verification-Findings §4.1 (30/yr is too few to support a Sharpe
# objective; 100/yr is the new floor unless a study overrides it deliberately).
DEFAULT_GATES: dict[str, float] = {
    "min_trades_per_year": 100,
    "max_dd_pct": 20.0,
    "min_pf": 1.15,
    "wfe_min": 0.5,
    "dsr_min": 0.95,
    "pbo_max": 0.25,
    "plateau_retention": 0.7,
}


def load_study(path: str | Path) -> StudyConfig:
    """Load and fully validate a study.yaml. Raises ConfigError on any violation."""
    path = Path(path)
    if not path.is_file():
        raise ConfigError(f"study config not found: {path}")
    raw = yaml.safe_load(path.read_text()) or {}
    if not isinstance(raw, dict):
        raise ConfigError(f"{path}: top level must be a mapping")

    name = _require(raw, "study", str(path))

    bot_raw = _require(raw, "bot", "study.yaml")
    bot = BotConfig(
        source=_require(bot_raw, "source", "bot"),
        class_name=_require(bot_raw, "class_name", "bot"),
        dotnet_target=bot_raw.get("dotnet_target", "net6.0"),
    )
    if bot.dotnet_target != "net6.0":
        # Not fatal — a newer console tag may ship a newer runtime — but the
        # default image ships 6.0.10 only and a net8.0 .algo will not load.
        pass

    market_raw = _require(raw, "market", "study.yaml")
    period = str(_require(market_raw, "period", "market"))
    if period not in VALID_PERIODS:
        raise ConfigError(
            f"market.period: {period!r} is not a cTrader period token. "
            f"Note these are case-sensitive (D1, W1, Month1 are capitalised)."
        )
    market = MarketConfig(
        symbol=_require(market_raw, "symbol", "market"),
        period=period,
        data_glob=_require(market_raw, "data_glob", "market"),
    )

    acct_raw = _require(raw, "account", "study.yaml")
    account = AccountConfig(
        nominal_balance=float(_require(acct_raw, "nominal_balance", "account")),
        currency=_require(acct_raw, "currency", "account"),
        risk_per_trade=float(_require(acct_raw, "risk_per_trade", "account")),
    )
    if account.nominal_balance <= 0 or account.risk_per_trade <= 0:
        raise ConfigError("account: nominal_balance and risk_per_trade must be > 0")

    exec_raw = _require(raw, "execution", "study.yaml")
    if "commission_per_lot" in exec_raw:
        raise ConfigError(
            "execution.commission_per_lot: the cTrader CLI's --commission is "
            "'commission per million'. Rename to commission_per_million and "
            "convert the value (see 03-Verification-Findings §3.3)."
        )
    spread_raw = _require(exec_raw, "spread_pips", "execution")
    if not isinstance(spread_raw, dict) or "realistic" not in spread_raw:
        raise ConfigError("execution.spread_pips must be a mapping containing 'realistic'")
    spreads = {k: float(v) for k, v in spread_raw.items()}
    if any(v <= 0 for v in spreads.values()):
        raise ConfigError(
            "execution.spread_pips: zero/negative spread is never permitted "
            "outside engine-debug mode (01-Research §3.3)"
        )
    slip_raw = _require(exec_raw, "slippage_model", "execution")
    execution = ExecutionConfig(
        spread_pips=spreads,
        commission_per_million=float(_require(exec_raw, "commission_per_million", "execution")),
        slippage_model=SlippageModel(
            dist=_require(slip_raw, "dist", "execution.slippage_model"),
            median_pips=float(_require(slip_raw, "median_pips", "execution.slippage_model")),
            p95_pips=float(_require(slip_raw, "p95_pips", "execution.slippage_model")),
        ),
    )

    win_raw = _require(raw, "windows", "study.yaml")
    wfa_raw = _require(win_raw, "wfa", "windows")
    mode = wfa_raw.get("mode", "rolling")
    if mode not in ("rolling", "anchored"):
        raise ConfigError(f"windows.wfa.mode: expected rolling|anchored, got {mode!r}")
    wfa = WfaConfig(
        mode=mode,
        is_months=int(_require(wfa_raw, "is_months", "windows.wfa")),
        oos_months=int(_require(wfa_raw, "oos_months", "windows.wfa")),
        step_months=int(_require(wfa_raw, "step_months", "windows.wfa")),
    )
    if min(wfa.is_months, wfa.oos_months, wfa.step_months) <= 0:
        raise ConfigError("windows.wfa: is/oos/step months must all be > 0")
    windows = WindowsConfig(
        data_start=_as_date(_require(win_raw, "data_start", "windows"), "windows.data_start"),
        holdout_start=_as_date(_require(win_raw, "holdout_start", "windows"), "windows.holdout_start"),
        wfa=wfa,
    )
    if windows.holdout_start <= windows.data_start:
        raise ConfigError("windows: holdout_start must be after data_start")

    bud_raw = _require(raw, "budgets", "study.yaml")
    budgets = BudgetsConfig(
        stage1_random=int(_require(bud_raw, "stage1_random", "budgets")),
        stage1_tpe=int(_require(bud_raw, "stage1_tpe", "budgets")),
        wfa_trials_per_fold=int(_require(bud_raw, "wfa_trials_per_fold", "budgets")),
        mc_resamples=int(_require(bud_raw, "mc_resamples", "budgets")),
    )

    gates_raw = {**DEFAULT_GATES, **(raw.get("gates") or {})}
    gates = GatesConfig(
        min_trades_per_year=int(gates_raw["min_trades_per_year"]),
        max_dd_pct=float(gates_raw["max_dd_pct"]),
        min_pf=float(gates_raw["min_pf"]),
        wfe_min=float(gates_raw["wfe_min"]),
        dsr_min=float(gates_raw["dsr_min"]),
        pbo_max=float(gates_raw["pbo_max"]),
        plateau_retention=float(gates_raw["plateau_retention"]),
    )

    tag = str(raw.get("ctrader_console_tag", "")).strip()
    if not tag:
        raise ConfigError(
            "ctrader_console_tag is required — pin the image tag for reproducibility "
            "(e.g. '5.9.0.0'; see 03-Verification-Findings §2.3)"
        )
    if tag == "latest":
        raise ConfigError("ctrader_console_tag: 'latest' is not reproducible; pin a version tag")

    return StudyConfig(
        study=name, bot=bot, market=market, account=account, execution=execution,
        windows=windows, budgets=budgets, gates=gates,
        ctrader_console_tag=tag, path=path.resolve(),
    )


# --------------------------------------------------------------------------
# search_space.yaml (build-spec §5.2)
# --------------------------------------------------------------------------

# Parameters whose name starts with this are engine-local: they drive derived
# values and are never passed to the bot, which would reject them as unknown.
LOCAL_PREFIX = "_"


@dataclass(frozen=True)
class SearchParam:
    name: str
    type: Literal["float", "int", "cat", "bool"]
    low: float | None = None
    high: float | None = None
    step: float | None = None
    choices: list[Any] = field(default_factory=list)
    condition: str | None = None

    @property
    def is_local(self) -> bool:
        return self.name.startswith(LOCAL_PREFIX)


@dataclass(frozen=True)
class DerivedParam:
    """A bot parameter computed from searched ones.

    Exists because some bot parameters are only meaningful as a *pair*. The ORB
    range is the motivating case: Range Start and Range End are both absolute
    times, so searching them independently yields incoherent combinations like
    start 14:30 / end 08:15. Searching an anchor plus a duration, and deriving
    the end time, keeps every sampled point valid by construction — far better
    than generating nonsense and rejecting it afterwards.
    """
    name: str
    source: str          # parameter holding a "HH:MM:SS" time
    add_minutes: str     # parameter holding a whole number of minutes

    def resolve(self, values: dict[str, Any]) -> str:
        from datetime import datetime, timedelta
        base = str(values[self.source])
        minutes = int(values[self.add_minutes])
        t = datetime.strptime(base, "%H:%M:%S") + timedelta(minutes=minutes)
        return t.strftime("%H:%M:%S")


def parse_condition(expr: str) -> tuple[str, Any]:
    """Parse a condition into (parent parameter, required value).

    Two forms:
      ``"Enable Trend Filter"``       — active when the parent is truthy
      ``"Exit Mode == MultiTP"``      — active when the parent equals a value

    The equality form is what makes mutually-exclusive branches possible: a
    Multi-TP ladder and a dynamic trailing stop are never both in play, so they
    should not each cost a permanent dimension.
    """
    if "==" in expr:
        parent, value = expr.split("==", 1)
        raw = value.strip().strip('"').strip("'")
        if raw.lower() in ("true", "false"):
            return parent.strip(), raw.lower() == "true"
        return parent.strip(), raw
    return expr.strip(), True


@dataclass(frozen=True)
class SearchSpace:
    fixed: dict[str, Any]
    search: dict[str, SearchParam]
    constraints: list[str]
    notes: str
    path: Path
    derived: dict[str, DerivedParam] = field(default_factory=dict)

    def bot_parameters(self, values: dict[str, Any]) -> dict[str, Any]:
        """The parameters actually sent to the bot: searched + derived, minus locals."""
        out = {k: v for k, v in values.items() if not k.startswith(LOCAL_PREFIX)}
        for name, d in self.derived.items():
            if d.source in values and d.add_minutes in values:
                out[name] = d.resolve(values)
        return out

    def is_active(self, name: str, values: dict[str, Any]) -> bool:
        """Whether a parameter is in play given the parent values chosen so far."""
        p = self.search[name]
        if not p.condition:
            return True
        parent, required = parse_condition(p.condition)
        actual = values.get(parent, self.fixed.get(parent))
        return bool(actual) if required is True else actual == required

    @property
    def declared_dimensions(self) -> int:
        return len(self.search)

    @property
    def effective_dimensions(self) -> int:
        """The most dimensions that can be *simultaneously* active.

        This is the number that matters statistically: a trial only explores the
        parameters actually in play, so mutually-exclusive branches do not
        compound. Counting every declared parameter instead would forbid
        perfectly sound designs (01-Research §4.1 caps the search at ten
        dimensions per study — per trial, not per file).
        """
        controllers: dict[str, list[Any]] = {}
        for p in self.search.values():
            if not p.condition:
                continue
            parent, _ = parse_condition(p.condition)
            if parent in controllers or parent not in self.search:
                continue
            parent_param = self.search[parent]
            if parent_param.type == "bool":
                controllers[parent] = [True, False]
            elif parent_param.type == "cat":
                controllers[parent] = list(parent_param.choices)
            else:
                controllers[parent] = [None]   # numeric parents: treat as always on

        if not controllers:
            return len(self.search)

        import itertools
        names = list(controllers)
        best = 0
        for combo in itertools.product(*(controllers[n] for n in names)):
            values = dict(zip(names, combo))
            active = sum(
                1 for n in self.search
                if not self.search[n].condition or self.is_active(n, values)
            )
            best = max(best, active)
        return best


_CONSTRAINT_RE = re.compile(r"^[\w\s\"'.<>=!+\-*/()%]+$")


def load_search_space(path: str | Path) -> SearchSpace:
    """Load and validate a per-bot search_space.yaml."""
    path = Path(path)
    if not path.is_file():
        raise ConfigError(f"search space not found: {path}")
    raw = yaml.safe_load(path.read_text()) or {}

    fixed = raw.get("fixed") or {}
    if not isinstance(fixed, dict):
        raise ConfigError("search_space.fixed must be a mapping")

    search_raw = raw.get("search") or {}
    if not isinstance(search_raw, dict) or not search_raw:
        raise ConfigError("search_space.search must be a non-empty mapping")

    params: dict[str, SearchParam] = {}
    for pname, spec in search_raw.items():
        if not isinstance(spec, dict):
            raise ConfigError(f"search.{pname}: expected a mapping")
        ptype = spec.get("type")
        if ptype not in ("float", "int", "cat", "bool"):
            raise ConfigError(f"search.{pname}.type must be float|int|cat|bool, got {ptype!r}")
        if ptype in ("float", "int"):
            if "low" not in spec or "high" not in spec:
                raise ConfigError(f"search.{pname}: numeric params require low and high")
            if float(spec["low"]) >= float(spec["high"]):
                raise ConfigError(f"search.{pname}: low must be < high")
        if ptype == "cat" and not spec.get("choices"):
            raise ConfigError(f"search.{pname}: categorical params require non-empty choices")
        params[pname] = SearchParam(
            name=pname,
            type=ptype,
            low=float(spec["low"]) if "low" in spec else None,
            high=float(spec["high"]) if "high" in spec else None,
            step=float(spec["step"]) if spec.get("step") is not None else None,
            choices=list(spec.get("choices") or []),
            condition=spec.get("condition"),
        )

    for pname, p in params.items():
        if not p.condition:
            continue
        parent, required = parse_condition(p.condition)
        if parent not in params and parent not in fixed:
            raise ConfigError(
                f"search.{pname}.condition references {parent!r}, "
                "which is neither a searched nor a fixed parameter"
            )
        if required is not True and parent in params:
            parent_param = params[parent]
            if parent_param.type == "cat" and required not in parent_param.choices:
                raise ConfigError(
                    f"search.{pname}.condition requires {parent}=={required!r}, "
                    f"but that is not one of its choices {parent_param.choices}"
                )

    derived: dict[str, DerivedParam] = {}
    for dname, spec in (raw.get("derived") or {}).items():
        if not isinstance(spec, dict) or "from" not in spec or "add_minutes" not in spec:
            raise ConfigError(
                f"derived.{dname}: expected a mapping with 'from' and 'add_minutes'"
            )
        src, mins = spec["from"], spec["add_minutes"]
        for ref, label in ((src, "from"), (mins, "add_minutes")):
            if ref not in params and ref not in fixed:
                raise ConfigError(
                    f"derived.{dname}.{label} references {ref!r}, which is neither "
                    "searched nor fixed"
                )
        if dname in params or dname in fixed:
            raise ConfigError(
                f"derived.{dname} collides with a searched or fixed parameter — a "
                "derived value must not also be set directly"
            )
        derived[dname] = DerivedParam(name=dname, source=src, add_minutes=mins)

    space = SearchSpace(
        fixed=fixed,
        search=params,
        constraints=list(raw.get("constraints") or []),
        notes=str(raw.get("notes") or ""),
        path=path.resolve(),
        derived=derived,
    )

    if space.effective_dimensions > MAX_SEARCH_DIMENSIONS:
        raise ConfigError(
            f"search space has {space.effective_dimensions} simultaneously-active "
            f"dimensions ({space.declared_dimensions} declared); the limit is "
            f"{MAX_SEARCH_DIMENSIONS} (01-Research §4.1). Either split into staged "
            "studies, or make competing options mutually exclusive with an "
            "'X == value' condition so they do not compound."
        )
    if not space.notes.strip():
        raise ConfigError(
            "search_space.notes is REQUIRED: one line of hypothesis rationale per "
            "searched parameter (build-spec §5.2)"
        )
    for c in space.constraints:
        if not _CONSTRAINT_RE.match(c):
            raise ConfigError(f"constraint {c!r} contains unsupported characters")

    return space
