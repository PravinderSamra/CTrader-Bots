"""
US500 Overnight Phenomenon Backtest
====================================
Strategy: Buy US500 at daily close, sell at next day's open.
Data:      CTrader Remote MCP HTTP API (Pepperstone demo account).
Period:    Last 12 months.
Risk:      $100 per trade (sized as 1% adverse move = $100 loss,
           so notional = $10,000 per trade).
Costs:     Overnight CFD financing + spread (both sides).

Usage:
    python backtest.py
"""

import http.client
import ssl
import json
import sys
from datetime import datetime, timezone, timedelta
from collections import defaultdict

# ── CTrader MCP config ─────────────────────────────────────────────────────────
_MCP_HOST  = "mcp.ctrader.com"
_MCP_PATH  = "/trading/mcp"
_TOKEN     = (
    "eyJwbGFudCI6InBlcHBlcnN0b25ldWsiLCJlbnZpcm9ubWVudCI6ImRlbW8iLCJ0b2"
    "tlbiI6IkliMEJzUERzSXBpZUJnTEtUWTluRjRpMEJ6a3R4V0pvSm1ZNVB3a1lIb2c9In0"
)

# ── Backtest parameters ────────────────────────────────────────────────────────
SYMBOL_NAME       = "US500"          # cTrader symbol name
PIP_DIGITS        = 3                # US500 raw price / 10^3 = display price
RISK_PER_TRADE    = 100.0            # USD
NOTIONAL          = 10_000.0         # Position size: risk / 1% move
BACKTEST_MONTHS   = 12

# Pepperstone US500 overnight financing (long):
# SOFR (~5.3%) + 2.5% markup = ~7.8% p.a. (typical as of 2025-2026)
OVERNIGHT_RATE_PA = 0.078            # 7.8% per annum
SPREAD_POINTS     = 0.5              # ~0.5 pt spread each way (in + out = 1.0 pt)
US500_POINT_VALUE = 1.0              # $1 per point per contract

# ── Session state ──────────────────────────────────────────────────────────────
_conn:       http.client.HTTPSConnection | None = None
_session_id: str | None = None


def _get_conn() -> http.client.HTTPSConnection:
    global _conn
    if _conn is None:
        _conn = http.client.HTTPSConnection(
            _MCP_HOST,
            context=ssl.create_default_context(),
            timeout=30,
        )
    return _conn


def _post(payload: dict, session_id: str | None = None) -> tuple[dict | None, str | None]:
    global _conn, _session_id
    body    = json.dumps(payload)
    headers = {
        "Authorization": f"Bearer {_TOKEN}",
        "Accept":        "application/json, text/event-stream",
        "Content-Type":  "application/json",
    }
    if session_id:
        headers["Mcp-Session-Id"] = session_id

    for attempt in range(3):
        try:
            conn = _get_conn()
            conn.request("POST", _MCP_PATH, body, headers)
            resp    = conn.getresponse()
            new_sid = (resp.getheader("Mcp-Session-Id")
                       or resp.getheader("mcp-session-id")
                       or session_id)
            raw     = resp.read().decode()

            if resp.status == 404:
                return {"_session_expired": True}, None

            for line in raw.split("\n"):
                if line.startswith("data: "):
                    try:
                        return json.loads(line[6:]), new_sid
                    except json.JSONDecodeError:
                        pass
            return None, session_id

        except Exception as exc:
            try:
                if _conn:
                    _conn.close()
            except Exception:
                pass
            _conn = None
            if attempt == 2:
                print(f"  [ERROR] HTTP request failed after 3 attempts: {exc}", file=sys.stderr)
                return None, session_id

    return None, session_id


def _ensure_session() -> bool:
    global _session_id
    if _session_id:
        return True

    data, sid = _post({
        "jsonrpc": "2.0",
        "method":  "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities":    {},
            "clientInfo":      {"name": "overnight-backtest", "version": "1.0"},
        },
        "id": 0,
    })

    if data and "result" in data and sid:
        _session_id = sid
        _post({"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}}, sid)
        return True
    return False


def _call_tool(tool: str, arguments: dict) -> dict | None:
    global _session_id

    if not _ensure_session():
        return None

    payload = {
        "jsonrpc": "2.0",
        "method":  "tools/call",
        "params":  {"name": tool, "arguments": arguments},
        "id":      1,
    }

    data, new_sid = _post(payload, _session_id)

    expired = (
        (data and data.get("_session_expired")) or
        (data and "error" in data and "session" in str(data.get("error", "")).lower())
    )
    if expired:
        _session_id = None
        if not _ensure_session():
            return None
        data, new_sid = _post(payload, _session_id)

    if new_sid:
        _session_id = new_sid

    if not data or "result" not in data:
        return None

    content = data["result"].get("content", [])
    if content and content[0].get("type") == "text":
        try:
            return json.loads(content[0]["text"])
        except (json.JSONDecodeError, KeyError):
            pass
    return None


# ── Symbol resolution ──────────────────────────────────────────────────────────

def get_symbol_id(name: str) -> int | None:
    result = _call_tool("get_symbols", {})
    if not result:
        return None
    for sym in result.get("symbols", []):
        raw = sym.get("name") or sym.get("symbolName") or ""
        if raw.upper().startswith(name.upper()):
            sid = sym.get("symbolId")
            if sid is not None:
                return int(sid)
    return None


# ── Trendbar fetching with 720h-window pagination ─────────────────────────────

def fetch_daily_bars(symbol_id: int, from_dt: datetime, to_dt: datetime) -> list[dict]:
    """
    Fetch D_1 trendbars for the given range, chunking into ≤720h windows.
    Returns list of raw bar dicts, sorted ascending by timestamp.
    """
    MAX_WINDOW_H = 700          # stay under the 720h API cap with margin
    all_bars: list[dict] = []
    chunk_delta = timedelta(hours=MAX_WINDOW_H)

    chunk_start = from_dt
    while chunk_start < to_dt:
        chunk_end = min(chunk_start + chunk_delta, to_dt)

        result = _call_tool("get_trendbars", {
            "symbolId":      symbol_id,
            "period":        "D_1",
            "fromTimestamp": chunk_start.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "toTimestamp":   chunk_end.strftime("%Y-%m-%dT%H:%M:%SZ"),
        })

        bars = []
        if result:
            bars = (
                result.get("trendbars")
                or result.get("trendBars")
                or result.get("bars")
                or result.get("data")
                or []
            )
        all_bars.extend(bars)
        chunk_start = chunk_end

    # Deduplicate by timestamp, sort ascending
    seen: set[int] = set()
    unique: list[dict] = []
    for bar in all_bars:
        ts = (bar.get("utcTimestamp")
              or bar.get("timestamp")
              or bar.get("utcTimestampInMinutes")
              or bar.get("time")
              or 0)
        if ts not in seen:
            seen.add(int(ts))
            unique.append(bar)

    unique.sort(key=lambda b: (
        b.get("utcTimestamp")
        or b.get("timestamp")
        or b.get("utcTimestampInMinutes")
        or b.get("time")
        or 0
    ))
    return unique


def parse_bar(bar: dict, pip_div: float) -> tuple[datetime, float, float, float, float]:
    """Returns (datetime_utc, open, high, low, close)."""
    ts_raw = int(
        bar.get("utcTimestamp")
        or bar.get("timestamp")
        or bar.get("utcTimestampInMinutes")
        or bar.get("time")
        or 0
    )
    if ts_raw > 1_000_000_000_000:
        dt = datetime.fromtimestamp(ts_raw / 1000, tz=timezone.utc)
    elif ts_raw > 1_000_000_000:
        dt = datetime.fromtimestamp(ts_raw, tz=timezone.utc)
    else:
        dt = datetime.fromtimestamp(ts_raw * 60.0, tz=timezone.utc)

    o = bar.get("open",  0) / pip_div
    h = bar.get("high",  0) / pip_div
    l = bar.get("low",   0) / pip_div
    c = bar.get("close", 0) / pip_div
    return dt, o, h, l, c


# ── Cost calculations ──────────────────────────────────────────────────────────

def overnight_financing_cost(notional: float) -> float:
    """Overnight CFD financing cost for one night (long US500)."""
    return notional * OVERNIGHT_RATE_PA / 365.0


def spread_cost(entry_price: float, notional: float) -> float:
    """Round-trip spread cost: SPREAD_POINTS points × (notional / price) × $1/pt."""
    contracts = notional / entry_price
    return (SPREAD_POINTS * 2) * contracts * US500_POINT_VALUE


# ── Week number helper ─────────────────────────────────────────────────────────

def week_key(dt: datetime) -> str:
    iso = dt.isocalendar()
    return f"{iso.year}-W{iso.week:02d}"


# ── Main backtest ──────────────────────────────────────────────────────────────

def run_backtest():
    now    = datetime.now(tz=timezone.utc)
    from_dt = now - timedelta(days=365)

    print("=" * 70)
    print("  US500 OVERNIGHT PHENOMENON BACKTEST")
    print(f"  Period : {from_dt.strftime('%d %b %Y')} → {now.strftime('%d %b %Y')}")
    print(f"  Risk   : ${RISK_PER_TRADE:.0f} per trade  |  Notional: ${NOTIONAL:,.0f}")
    print(f"  Costs  : Overnight financing {OVERNIGHT_RATE_PA*100:.1f}% p.a. + {SPREAD_POINTS*2:.1f}pt spread")
    print("=" * 70)

    # ── Connect & resolve symbol ───────────────────────────────────────────────
    print("\n[1/3] Connecting to CTrader MCP (Pepperstone demo)...")
    if not _ensure_session():
        print("  ERROR: Could not establish MCP session. Check token/network.")
        sys.exit(1)
    print("  Session established.")

    print(f"\n[2/3] Resolving symbol '{SYMBOL_NAME}'...")
    symbol_id = get_symbol_id(SYMBOL_NAME)
    if symbol_id is None:
        print(f"  ERROR: Symbol '{SYMBOL_NAME}' not found. Exiting.")
        sys.exit(1)
    print(f"  Symbol ID: {symbol_id}")

    # ── Fetch 12 months of D_1 bars ───────────────────────────────────────────
    print(f"\n[3/3] Fetching 12 months of daily bars (paginated, 700h chunks)...")
    raw_bars = fetch_daily_bars(symbol_id, from_dt, now)
    print(f"  Retrieved {len(raw_bars)} raw bars.")

    if len(raw_bars) < 10:
        print("  ERROR: Insufficient data returned. Exiting.")
        sys.exit(1)

    # Auto-detect pip divisor from first bar
    first_close = raw_bars[0].get("close", 0)
    pip_div = 1.0
    for d in range(0, 9):
        val = first_close / (10 ** d)
        if 3_000 <= val <= 12_000:   # plausible US500 range
            pip_div = 10 ** d
            break
    if pip_div == 1.0:
        pip_div = 10 ** PIP_DIGITS
    print(f"  Price divisor detected: {pip_div:.0f} (raw {first_close} → {first_close/pip_div:.2f})")

    # Parse all bars
    parsed: list[tuple[datetime, float, float, float, float]] = []
    for bar in raw_bars:
        try:
            row = parse_bar(bar, pip_div)
            if row[4] > 100:    # close > 100 sanity check
                parsed.append(row)
        except Exception:
            continue
    parsed.sort(key=lambda r: r[0])
    print(f"  Parsed {len(parsed)} valid daily bars.")

    # ── Simulate overnight trades ─────────────────────────────────────────────
    # Trade: buy at close of day[i], sell at open of day[i+1]
    trades: list[dict] = []

    for i in range(len(parsed) - 1):
        dt_entry,  o_e, h_e, l_e, close_price = parsed[i]
        dt_exit,   open_price, h_x, l_x, c_x   = parsed[i + 1]

        # Skip if it's not a consecutive weekday pair (weekend / holiday gap)
        day_diff = (dt_exit - dt_entry).days
        if day_diff > 4:    # more than 4 days → skip (extended holiday)
            continue

        gap_pct   = (open_price - close_price) / close_price
        contracts = NOTIONAL / close_price      # number of US500 units
        gross_pnl = gap_pct * NOTIONAL

        fin_cost  = overnight_financing_cost(NOTIONAL)
        spr_cost  = spread_cost(close_price, NOTIONAL)
        total_cost = fin_cost + spr_cost
        net_pnl   = gross_pnl - total_cost

        trades.append({
            "entry_date":   dt_entry.date(),
            "exit_date":    dt_exit.date(),
            "close":        close_price,
            "open":         open_price,
            "gap_pct":      gap_pct * 100,
            "contracts":    contracts,
            "gross_pnl":    gross_pnl,
            "fin_cost":     fin_cost,
            "spr_cost":     spr_cost,
            "total_cost":   total_cost,
            "net_pnl":      net_pnl,
            "win":          net_pnl > 0,
            "week":         week_key(dt_entry),
        })

    if not trades:
        print("  ERROR: No trades generated. Check data quality.")
        sys.exit(1)

    # ── Summary stats ─────────────────────────────────────────────────────────
    total_trades = len(trades)
    wins         = [t for t in trades if t["win"]]
    losses       = [t for t in trades if not t["win"]]
    win_rate     = len(wins) / total_trades * 100

    total_gross  = sum(t["gross_pnl"]  for t in trades)
    total_net    = sum(t["net_pnl"]    for t in trades)
    total_fin    = sum(t["fin_cost"]   for t in trades)
    total_spr    = sum(t["spr_cost"]   for t in trades)
    total_costs  = sum(t["total_cost"] for t in trades)

    avg_win      = sum(t["net_pnl"] for t in wins)   / len(wins)   if wins   else 0
    avg_loss     = sum(t["net_pnl"] for t in losses) / len(losses) if losses else 0
    best_trade   = max(trades, key=lambda t: t["gross_pnl"])
    worst_trade  = min(trades, key=lambda t: t["gross_pnl"])

    # Profit factor
    gross_wins   = sum(t["gross_pnl"] for t in wins)
    gross_losses = abs(sum(t["gross_pnl"] for t in losses))
    profit_factor = gross_wins / gross_losses if gross_losses > 0 else float("inf")

    # Max drawdown (equity curve)
    equity = 0.0
    peak   = 0.0
    max_dd = 0.0
    for t in trades:
        equity += t["net_pnl"]
        if equity > peak:
            peak = equity
        dd = peak - equity
        if dd > max_dd:
            max_dd = dd

    # Week-over-week breakdown
    weekly: dict[str, dict] = defaultdict(lambda: {
        "trades": 0, "wins": 0, "losses": 0,
        "gross_pnl": 0.0, "net_pnl": 0.0, "costs": 0.0,
    })
    for t in trades:
        w = t["week"]
        weekly[w]["trades"]    += 1
        weekly[w]["wins"]      += 1 if t["win"] else 0
        weekly[w]["losses"]    += 0 if t["win"] else 1
        weekly[w]["gross_pnl"] += t["gross_pnl"]
        weekly[w]["net_pnl"]   += t["net_pnl"]
        weekly[w]["costs"]     += t["total_cost"]

    # ── Print results ──────────────────────────────────────────────────────────
    print("\n" + "=" * 70)
    print("  BACKTEST RESULTS — US500 OVERNIGHT PHENOMENON")
    print("=" * 70)

    print(f"""
SUMMARY
-------
  Total trades       : {total_trades}
  Wins               : {len(wins)}  ({win_rate:.1f}%)
  Losses             : {len(losses)}  ({100-win_rate:.1f}%)
  Profit factor      : {profit_factor:.2f}
  Max drawdown (net) : ${max_dd:,.2f}

P&L (${RISK_PER_TRADE:.0f} risk / ${NOTIONAL:,.0f} notional per trade)
-------------------------------------
  Gross P&L          : ${total_gross:+,.2f}
  Total costs        : ${total_costs:,.2f}
    Overnight finance: ${total_fin:,.2f}  (${total_fin/total_trades:.2f}/trade avg)
    Spread (in+out)  : ${total_spr:,.2f}  (${total_spr/total_trades:.2f}/trade avg)
  NET P&L            : ${total_net:+,.2f}

AVERAGES PER TRADE
------------------
  Avg win  (net)     : ${avg_win:+,.2f}
  Avg loss (net)     : ${avg_loss:+,.2f}

BEST / WORST
------------
  Best trade  : {best_trade['entry_date']} | gap {best_trade['gap_pct']:+.2f}% | gross ${best_trade['gross_pnl']:+,.2f}
  Worst trade : {worst_trade['entry_date']} | gap {worst_trade['gap_pct']:+.2f}% | gross ${worst_trade['gross_pnl']:+,.2f}
""")

    print("WEEK-BY-WEEK P&L")
    print("-" * 70)
    print(f"  {'Week':<12} {'Trades':>6} {'W/L':>6} {'Gross P&L':>12} {'Costs':>9} {'Net P&L':>12} {'Cumul Net':>12}")
    print("  " + "-" * 66)

    cumul = 0.0
    for wk in sorted(weekly.keys()):
        d = weekly[wk]
        cumul += d["net_pnl"]
        wl_str = f"{d['wins']}/{d['losses']}"
        print(
            f"  {wk:<12} {d['trades']:>6} {wl_str:>6} "
            f"${d['gross_pnl']:>+10,.2f} "
            f"${d['costs']:>7,.2f} "
            f"${d['net_pnl']:>+10,.2f} "
            f"${cumul:>+10,.2f}"
        )

    print("\n" + "=" * 70)
    print("INDIVIDUAL TRADES (last 20 shown)")
    print("-" * 70)
    print(f"  {'Entry':>10} {'Exit':>10} {'Close':>8} {'Open':>8} {'Gap%':>7} {'Gross$':>9} {'Cost$':>7} {'Net$':>9} {'W/L':>4}")
    print("  " + "-" * 68)
    for t in trades[-20:]:
        wl = "WIN" if t["win"] else "LOSS"
        print(
            f"  {str(t['entry_date']):>10} {str(t['exit_date']):>10} "
            f"{t['close']:>8.2f} {t['open']:>8.2f} "
            f"{t['gap_pct']:>+6.2f}% "
            f"${t['gross_pnl']:>+7.2f} "
            f"${t['total_cost']:>5.2f} "
            f"${t['net_pnl']:>+7.2f} "
            f"{wl:>4}"
        )

    print("\n" + "=" * 70)
    print("COST ASSUMPTIONS (Pepperstone demo, long US500 CFD)")
    print("-" * 70)
    print(f"  Overnight financing rate : {OVERNIGHT_RATE_PA*100:.1f}% p.a. (SOFR + 2.5% markup)")
    print(f"  Spread (each way)        : {SPREAD_POINTS:.1f} points  (standard account)")
    print(f"  Round-trip spread cost   : {SPREAD_POINTS*2:.1f} points")
    print(f"  Notional per trade       : ${NOTIONAL:,.0f}")
    print(f"  Contracts at ~5500       : {NOTIONAL/5500:.4f} units")
    print(f"  Cost per night (avg)     : ${total_costs/total_trades:.2f}")
    print(f"  NOTE: Pepperstone Razor account adds $0.02/unit/side commission.")
    print(f"        On {NOTIONAL/5500:.4f} units that is ~${2 * 0.02 * NOTIONAL/5500:.4f} per trade.")
    print("=" * 70)
    print()


if __name__ == "__main__":
    run_backtest()
