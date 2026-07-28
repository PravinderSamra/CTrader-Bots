"""Canonical backtest result structures.

Everything downstream of the cTrader CLI speaks this vocabulary, so the parser in
``ctcli.py`` is the only module that needs to know cTrader's JSON schema. Swapping
the execution backend (or using the recorded-fixture fake) changes nothing above
this line.

Partial closes matter here: multi-TP bots close a position in slices. The parser
aggregates slices into one *logical trade* while keeping the raw slices, because
the two answer different questions — logical trades drive R-multiples and win
rate, slices drive fill-level cost analysis.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path

import pandas as pd


@dataclass
class TradeSlice:
    """One fill: a partial or full close of a position."""
    position_id: str
    close_time: pd.Timestamp
    close_price: float
    volume: float
    net_pnl: float


@dataclass
class Trade:
    """A logical trade — one position from open to fully closed."""
    position_id: str
    symbol: str
    direction: str                  # "buy" | "sell"
    open_time: pd.Timestamp
    close_time: pd.Timestamp
    entry_price: float
    exit_price: float               # volume-weighted across slices
    volume: float
    gross_pnl: float
    net_pnl: float
    pips: float
    label: str = ""
    comment: str = ""
    slices: list[TradeSlice] = field(default_factory=list)

    @property
    def is_win(self) -> bool:
        return self.net_pnl > 0


@dataclass
class BacktestResult:
    """The canonical outcome of one backtest run."""
    trades: list[Trade]
    equity_curve: pd.Series          # timestamp-indexed account equity
    summary: dict                    # as reported by the CLI, unmodified
    equity_source: str               # "marks" | "reconstructed" — never guess later
    log_path: str | None = None
    failed: bool = False
    failure_excerpt: str = ""

    @property
    def trade_pnl(self) -> pd.Series:
        return pd.Series([t.net_pnl for t in self.trades], dtype="float64")

    def trades_frame(self) -> pd.DataFrame:
        """Trades as a DataFrame — the input to slicing, MC and regime analysis."""
        if not self.trades:
            return pd.DataFrame(columns=[
                "position_id", "direction", "open_time", "close_time",
                "entry_price", "exit_price", "volume", "net_pnl", "pips", "label",
            ])
        return pd.DataFrame([{
            "position_id": t.position_id,
            "direction": t.direction,
            "open_time": t.open_time,
            "close_time": t.close_time,
            "entry_price": t.entry_price,
            "exit_price": t.exit_price,
            "volume": t.volume,
            "net_pnl": t.net_pnl,
            "pips": t.pips,
            "label": t.label,
        } for t in self.trades])

    def to_json(self, path: Path) -> None:
        payload = {
            "summary": self.summary,
            "equity_source": self.equity_source,
            "failed": self.failed,
            "failure_excerpt": self.failure_excerpt,
            "equity_curve": {
                "index": [ts.isoformat() for ts in self.equity_curve.index],
                "values": [float(v) for v in self.equity_curve.values],
            },
            "trades": [
                {**asdict(t),
                 "open_time": t.open_time.isoformat(),
                 "close_time": t.close_time.isoformat(),
                 "slices": [
                     {**asdict(s), "close_time": s.close_time.isoformat()}
                     for s in t.slices
                 ]}
                for t in self.trades
            ],
        }
        path.write_text(json.dumps(payload, indent=2, default=str) + "\n")

    @classmethod
    def from_json(cls, path: Path) -> "BacktestResult":
        raw = json.loads(Path(path).read_text())
        eq = raw["equity_curve"]
        equity = pd.Series(
            eq["values"],
            index=pd.to_datetime(eq["index"], utc=True),
            dtype="float64",
        )
        trades = []
        for t in raw["trades"]:
            slices = [
                TradeSlice(
                    position_id=s["position_id"],
                    close_time=pd.Timestamp(s["close_time"]),
                    close_price=s["close_price"],
                    volume=s["volume"],
                    net_pnl=s["net_pnl"],
                )
                for s in t.get("slices", [])
            ]
            trades.append(Trade(
                position_id=t["position_id"], symbol=t["symbol"], direction=t["direction"],
                open_time=pd.Timestamp(t["open_time"]), close_time=pd.Timestamp(t["close_time"]),
                entry_price=t["entry_price"], exit_price=t["exit_price"], volume=t["volume"],
                gross_pnl=t["gross_pnl"], net_pnl=t["net_pnl"], pips=t["pips"],
                label=t.get("label", ""), comment=t.get("comment", ""), slices=slices,
            ))
        return cls(
            trades=trades, equity_curve=equity, summary=raw["summary"],
            equity_source=raw["equity_source"], failed=raw.get("failed", False),
            failure_excerpt=raw.get("failure_excerpt", ""),
        )


def reconstruct_equity(
    trades: list[Trade], nominal_balance: float
) -> pd.Series:
    """Build an equity curve by replaying closed trades on the nominal balance.

    Used when the CLI's Events.json carries no intra-trade equity marks. This
    flatters Sharpe slightly during long holds (open drawdown is invisible), so
    the caller MUST record ``equity_source="reconstructed"`` in the report's
    LIMITATIONS section — see 01-Research §7.3.
    """
    if not trades:
        return pd.Series(dtype="float64")
    ordered = sorted(trades, key=lambda t: t.close_time)
    times = [ordered[0].open_time]
    values = [nominal_balance]
    running = nominal_balance
    for t in ordered:
        running += t.net_pnl
        times.append(t.close_time)
        values.append(running)
    return pd.Series(values, index=pd.DatetimeIndex(times), dtype="float64")
