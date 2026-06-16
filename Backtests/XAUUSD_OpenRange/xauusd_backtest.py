#!/usr/bin/env python3
"""
XAUUSD 06:30 London Open Range Breakout — 12-Month Backtest
Spec: XAUUSD_OpenRange_Backtest_Brief.pdf

Entry approximation: 5-minute candle closes (spec calls for 1M closes, but the
cTrader MCP caps at 100 bars/request; 5M bars per day are fetched with a targeted
fromTimestamp so every relevant bar fits inside one 100-bar window).

Account : £10,000  |  Risk: £100/trade (fixed, no compounding)
Pip size: $1.00 USD per pip (1 point = $1 move for XAUUSD spread bet)
"""

import http.client
import ssl
import json
import csv
import os
import sys
from datetime import datetime, timedelta, date, timezone
from zoneinfo import ZoneInfo
from collections import defaultdict
from dataclasses import dataclass
from typing import Optional, List, Dict, Tuple

# ── CONFIG ─────────────────────────────────────────────────────────────────────

TOKEN = (
    "eyJwbGFudCI6InBlcHBlcnN0b25ldWsiLCJlbnZpcm9ubWVudCI6ImRlbW8iLCJ0b2"
    "tlbiI6IkliMEJzUERzSXBpZUJnTEtUWTluRjRpMEJ6a3R4V0pvSm1ZNVB3a1lIb2c9In0"
)
MCP_HOST = "mcp.ctrader.com"
MCP_PATH = "/trading/mcp"

UK_TZ  = ZoneInfo("Europe/London")
UTC_TZ = timezone.utc

PIP_SIZE         = 1.0      # $1.00 per pip for XAUUSD (1 dollar = 1 pip)
STARTING_BALANCE = 10_000.0
RISK_PER_TRADE   = 100.0    # £ fixed

# Strategy times (UK local)
RANGE_H, RANGE_M        = 6, 25   # 5M candle whose open is 06:25 UK
ENTRY_H, ENTRY_M        = 6, 30   # start watching for breakouts
BASE_KILL_H, BASE_KILL_M= 7,  0   # default entry kill time
TRADE_KILL_H,TRADE_KILL_M=12,  0  # close open positions

MIN_RANGE_PIP       = 3
MAX_RANGE_THRESHOLDS= [10, 15, 20, 25]
SL_BUFFERS_A        = [2, 3, 5, 8]
ATR_FRACTIONS       = [0.10, 0.15, 0.20]
SPREAD_COSTS        = [2, 3, 5]
KILL_TIMES          = [(6,45),(7,0),(7,15),(7,30)]


# ── DATA CLASSES ───────────────────────────────────────────────────────────────

@dataclass
class Bar:
    ts:     datetime  # UTC open time
    open:   float
    high:   float
    low:    float
    close:  float
    volume: float


@dataclass
class Trade:
    date:           str
    direction:      str
    range_size_pip: float
    entry_price:    float
    stop_loss:      float
    take_profit:    float
    result:         str   # WIN/LOSS/TIMEOUT/EXPIRED/SKIPPED
    r_outcome:      float
    pnl_gbp:        float
    spread_cost:    float
    reentry_flag:   bool
    bst_flag:       bool
    week_balance:   float
    sl_method:      str
    sl_param:       float
    spread_pips:    int
    max_range_pip:  int
    kill_time:      str
    dow:            str
    month:          str


# ── CTRADER MCP CLIENT ─────────────────────────────────────────────────────────

class CTraderMCP:
    def __init__(self, token: str):
        self.token   = token
        self._conn:   Optional[http.client.HTTPSConnection] = None
        self._sid:    Optional[str] = None
        self._syms:   Dict[str,int] = {}
        self._loaded  = False
        self.pip_digits = 3  # updated on first successful fetch

    def _connection(self) -> http.client.HTTPSConnection:
        if self._conn is None:
            self._conn = http.client.HTTPSConnection(
                MCP_HOST, context=ssl.create_default_context(), timeout=30)
        return self._conn

    def _post(self, payload: dict) -> Optional[dict]:
        body = json.dumps(payload)
        hdrs = {
            "Authorization": f"Bearer {self.token}",
            "Accept":        "application/json, text/event-stream",
            "Content-Type":  "application/json",
        }
        if self._sid:
            hdrs["Mcp-Session-Id"] = self._sid

        for attempt in range(4):
            try:
                c = self._connection()
                c.request("POST", MCP_PATH, body, hdrs)
                resp = c.getresponse()
                sid  = resp.getheader("Mcp-Session-Id") or resp.getheader("mcp-session-id")
                raw  = resp.read().decode()
                if sid:
                    self._sid = sid
                if resp.status == 404:
                    return {"_expired": True}
                for line in raw.split("\n"):
                    if line.startswith("data: "):
                        return json.loads(line[6:])
                return None
            except Exception as e:
                try: self._conn.close()
                except: pass
                self._conn = None
                if attempt == 3:
                    print(f"  [WARN] MCP error: {e}", file=sys.stderr)
        return None

    def _init_session(self) -> bool:
        if self._sid:
            return True
        data = self._post({"jsonrpc":"2.0","method":"initialize","id":0,
            "params":{"protocolVersion":"2024-11-05","capabilities":{},
                      "clientInfo":{"name":"xauusd-backtest","version":"1.0"}}})
        if data and "result" in data:
            self._post({"jsonrpc":"2.0","method":"notifications/initialized","params":{}})
            return True
        return False

    def _call(self, tool: str, args: dict) -> Optional[dict]:
        if not self._init_session():
            return None
        payload = {"jsonrpc":"2.0","method":"tools/call","id":1,
                   "params":{"name":tool,"arguments":args}}
        data = self._post(payload)
        if data and data.get("_expired"):
            self._sid = None
            if not self._init_session():
                return None
            data = self._post(payload)
        if not data or "result" not in data:
            return None
        content = data["result"].get("content",[])
        if content and content[0].get("type") == "text":
            try: return json.loads(content[0]["text"])
            except: pass
        return None

    def _load_symbols(self):
        if self._loaded:
            return
        r = self._call("get_symbols", {})
        if not r:
            return
        for s in r.get("symbols",[]):
            nm  = (s.get("name") or s.get("symbolName") or "").upper()
            sid = s.get("symbolId")
            if nm and sid is not None:
                self._syms[nm] = int(sid)
                for sfx in ("_SBE","_SB","-F_SB","-F"):
                    if nm.endswith(sfx):
                        self._syms.setdefault(nm[:-len(sfx)], int(sid))
        self._loaded = True

    def symbol_id(self, name: str) -> Optional[int]:
        self._load_symbols()
        nm = name.upper()
        if nm in self._syms:
            return self._syms[nm]
        for k,v in self._syms.items():
            if k.startswith(nm) or nm.startswith(k):
                return v
        return None

    def _detect_pip_digits(self, raw: float) -> int:
        for d in range(9):
            v = raw / (10**d)
            if 1400 <= v <= 8000:
                self.pip_digits = d
                return d
        return self.pip_digits

    def fetch_bars(self, sym_id: int, period: str,
                   from_ts: datetime, to_ts: datetime) -> List[Bar]:
        r = self._call("get_trendbars", {
            "symbolId":      sym_id,
            "period":        period,
            "fromTimestamp": from_ts.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "toTimestamp":   to_ts.strftime("%Y-%m-%dT%H:%M:%SZ"),
        })
        if not r:
            return []
        raw_bars = (r.get("trendbars") or r.get("trendBars") or
                    r.get("bars")      or r.get("data") or [])
        if not raw_bars:
            return []

        # Auto-detect pip digits from first bar
        first = raw_bars[0].get("close") or raw_bars[0].get("open") or 0
        if first:
            self._detect_pip_digits(first)
        pdiv = 10 ** self.pip_digits

        bars: List[Bar] = []
        for b in raw_bars:
            try:
                tr = int(b.get("utcTimestamp") or b.get("timestamp") or
                         b.get("utcTimestampInMinutes") or b.get("time") or 0)
                if   tr > 1_000_000_000_000: ts = datetime.fromtimestamp(tr/1000, tz=UTC_TZ)
                elif tr > 1_000_000_000:     ts = datetime.fromtimestamp(float(tr), tz=UTC_TZ)
                elif tr > 0:                 ts = datetime.fromtimestamp(tr*60.0, tz=UTC_TZ)
                else: continue

                o,h,l,c = (b.get(k,0)/pdiv for k in ("open","high","low","close"))
                v = float(b.get("tickVolume") or b.get("volume") or 0)
                if l > 0 and h >= l:
                    bars.append(Bar(ts=ts,open=o,high=h,low=l,close=c,volume=v))
            except Exception:
                continue
        bars.sort(key=lambda x: x.ts)
        return bars


# ── TIME HELPERS ───────────────────────────────────────────────────────────────

def to_uk(dt: datetime) -> datetime:
    return dt.astimezone(UK_TZ)

def uk_offset_hours(d: date) -> int:
    """Return +1 for BST dates, 0 for GMT dates."""
    return int(datetime(d.year,d.month,d.day,12,0,tzinfo=UK_TZ)
               .utcoffset().total_seconds() / 3600)

def is_bst(d: date) -> bool:
    return uk_offset_hours(d) == 1

def uk_to_utc_h(d: date, uk_h: int, uk_m: int = 0) -> datetime:
    """UK local HH:MM on date d → UTC datetime."""
    return datetime(d.year,d.month,d.day,uk_h,uk_m, tzinfo=UK_TZ).astimezone(UTC_TZ)


# ── DATA PIPELINE ──────────────────────────────────────────────────────────────
# The cTrader MCP caps responses at 100 bars per request and returns the FIRST
# 100 bars from fromTimestamp (forward). Each day we therefore set:
#
#   5M fromTimestamp = 04:00 UTC  →  100 × 5min = 8h20m  →  04:00–12:20 UTC
#      BST: 05:00–13:20 UK  ✓  (covers 06:25 range candle AND 12:00 kill)
#      GMT: 04:00–12:20 UK  ✓
#
#   1M fromTimestamp = UK 06:00 in UTC  →  100 × 1min = 1h40m  →  06:00–07:40 UK
#      Covers entry window 06:30–07:30 UK ✓  and 14-bar ATR ✓
#      BST: fromUTC = 05:00 UTC
#      GMT: fromUTC = 06:00 UTC

def fetch_day(client: CTraderMCP, sym_id: int, d: date) -> Tuple[List[Bar], List[Bar]]:
    """Return (bars_5m, bars_1m) for trading day d.

    The cTrader MCP returns the LAST 100 bars before toTimestamp.

    5M: toTimestamp = UK 12:35  →  100 × 5min = 8h20m window ending at UK 12:35
        Starts at UK 04:15 in both BST and GMT — covers 06:25 range candle and 12:00 kill.

    1M: toTimestamp = UK 07:35  →  100 × 1min = 1h40m window ending at UK 07:35
        Starts at UK 05:55 in both BST and GMT — covers entry window 06:30–07:30
        and provides 34 bars of ATR lookback before 06:30.
    """
    # uk_to_utc_h handles BST/GMT automatically
    to_5m   = uk_to_utc_h(d, 12, 35)
    from_5m = to_5m - timedelta(hours=12)   # far enough back; API uses last-N logic

    to_1m   = uk_to_utc_h(d, 7, 35)
    from_1m = to_1m - timedelta(hours=4)

    b5m = client.fetch_bars(sym_id, "M_5", from_5m, to_5m)
    b1m = client.fetch_bars(sym_id, "M_1", from_1m, to_1m)
    return b5m, b1m


def fetch_all_days(client: CTraderMCP, symbol: str,
                   start: date, end: date) -> Dict[date, Tuple[List[Bar], List[Bar]]]:
    sym_id = client.symbol_id(symbol)
    if sym_id is None:
        print(f"  [ERROR] Symbol '{symbol}' not found", file=sys.stderr)
        return {}
    print(f"  symbolId={sym_id}")

    days: List[date] = []
    d = start
    while d <= end:
        if d.weekday() < 5:
            days.append(d)
        d += timedelta(days=1)

    data: Dict[date, Tuple[List[Bar], List[Bar]]] = {}
    n = len(days)
    for i, d in enumerate(days):
        if i % 20 == 0 or i == n-1:
            print(f"    [{i+1}/{n}] {d} …", flush=True)
        b5, b1 = fetch_day(client, sym_id, d)
        if b5:  # only keep days with at least some 5M data
            data[d] = (b5, b1)

    print(f"  Days with data: {len(data)}/{n}")
    return data


# ── INDICATORS ─────────────────────────────────────────────────────────────────

def atr14(bars: List[Bar]) -> float:
    if len(bars) < 2:
        return 0.0
    trs = [max(bars[i].high-bars[i].low,
               abs(bars[i].high-bars[i-1].close),
               abs(bars[i].low -bars[i-1].close))
           for i in range(1, len(bars))]
    sample = trs[-14:] if len(trs)>=14 else trs
    return sum(sample)/len(sample) if sample else 0.0


# ── PRICE / PIP HELPERS ────────────────────────────────────────────────────────

def p2pip(diff: float) -> float: return diff / PIP_SIZE
def pip2p(pips: float) -> float: return pips * PIP_SIZE


# ── STRATEGY SIMULATION ────────────────────────────────────────────────────────

def simulate_day(
    d:             date,
    bars_5m:       List[Bar],
    bars_1m:       List[Bar],
    max_range_pip: int,
    sl_method:     str,
    sl_param:      float,
    spread_pips:   int,
    kill_hm:       Tuple[int,int] = (7,0),
    allow_reentry: bool = True,
) -> List[Trade]:

    bst      = is_bst(d)
    dow      = d.strftime("%A")
    mon      = d.strftime("%B")
    kt_label = f"{kill_hm[0]:02d}:{kill_hm[1]:02d}"

    # UK time anchors as UTC for comparisons
    t_range_uk   = uk_to_utc_h(d, RANGE_H, RANGE_M)     # 06:25 UK
    t_entry_uk   = uk_to_utc_h(d, ENTRY_H, ENTRY_M)     # 06:30 UK
    t_kill_uk    = uk_to_utc_h(d, kill_hm[0], kill_hm[1])
    t_trade_kill = uk_to_utc_h(d, TRADE_KILL_H, TRADE_KILL_M)  # 12:00 UK

    def skipped(label: str, rpip: float) -> Trade:
        return Trade(date=str(d), direction="N/A", range_size_pip=rpip,
            entry_price=0, stop_loss=0, take_profit=0, result=label,
            r_outcome=0, pnl_gbp=0, spread_cost=0, reentry_flag=False,
            bst_flag=bst, week_balance=0, sl_method=sl_method, sl_param=sl_param,
            spread_pips=spread_pips, max_range_pip=max_range_pip,
            kill_time=kt_label, dow=dow, month=mon)

    # ── STEP 1: 06:25 5M range candle ─────────────────────────────────────────
    rng_bar = None
    for bar in bars_5m:
        uk = to_uk(bar.ts)
        if uk.hour == RANGE_H and uk.minute == RANGE_M:
            rng_bar = bar
            break

    if rng_bar is None:
        return []   # no data for this day

    rh = rng_bar.high
    rl = rng_bar.low
    rpip = p2pip(rh - rl)

    if rpip < MIN_RANGE_PIP or rpip > max_range_pip:
        return [skipped("SKIPPED", rpip)]

    # ── STEP 2: Entry trigger (1M preferred, 5M fallback) ─────────────────────
    # Use 1M bars where available; fall back to 5M for the entry scan
    entry_bars = bars_1m if bars_1m else bars_5m

    def find_trigger(candidates: List[Bar]
                     ) -> Optional[Tuple[str,float,float,float,float,Bar]]:
        for bar in candidates:
            # Bar's CLOSE time = open + 1min (for 1M) or + 5min (for 5M)
            bar_dur = timedelta(minutes=1) if entry_bars is bars_1m else timedelta(minutes=5)
            close_utc = bar.ts + bar_dur
            if close_utc <= t_entry_uk or close_utc > t_kill_uk:
                continue

            for direction, triggered in [("LONG",  bar.close > rh),
                                          ("SHORT", bar.close < rl)]:
                if not triggered:
                    continue
                entry = bar.close

                # ATR from bars before this candle (5M bars give enough history)
                prior = [b for b in bars_5m if b.ts < bar.ts]

                if sl_method == "A":
                    buf = pip2p(sl_param)
                    sl  = (rl - buf) if direction == "LONG" else (rh + buf)
                    sl_d = abs(entry - sl)
                else:
                    atr  = atr14(prior)
                    if atr == 0:
                        continue
                    sl_d = atr * sl_param
                    sl   = (entry - sl_d) if direction == "LONG" else (entry + sl_d)

                if sl_d <= 0:
                    continue
                tp = (entry + 2*sl_d) if direction == "LONG" else (entry - 2*sl_d)
                return direction, entry, sl, tp, p2pip(sl_d), bar
        return None

    trigger = find_trigger(entry_bars)

    if trigger is None:
        return [skipped("EXPIRED", rpip)]

    direction, entry, sl, tp, sl_pip, trigger_bar = trigger

    # ── STEP 3: Simulate outcome using 5M bars ─────────────────────────────────
    # Returns (Trade, result_bar_close_ts) — the close time of the bar that
    # determined the result (needed to correctly time re-entry searches).
    def run_trade(dir_: str, ent_: float, sl_: float, tp_: float,
                  sl_pip_: float, after_ts: datetime,
                  is_re: bool) -> Tuple[Trade, Optional[datetime]]:
        stake      = RISK_PER_TRADE / sl_pip_ if sl_pip_ > 0 else 0
        spread_gbp = stake * spread_pips

        result_str  = "TIMEOUT"
        r_out       = 0.0
        pnl_gross   = 0.0
        result_bar_close: Optional[datetime] = None

        for bar in bars_5m:
            if bar.ts <= after_ts:
                continue
            bar_close_utc = bar.ts + timedelta(minutes=5)

            if dir_ == "LONG":
                if bar.low  <= sl_:
                    result_str, r_out, pnl_gross = "LOSS", -1.0, -RISK_PER_TRADE
                    result_bar_close = bar_close_utc; break
                if bar.high >= tp_:
                    result_str, r_out, pnl_gross = "WIN",  +2.0, +RISK_PER_TRADE*2
                    result_bar_close = bar_close_utc; break
            else:
                if bar.high >= sl_:
                    result_str, r_out, pnl_gross = "LOSS", -1.0, -RISK_PER_TRADE
                    result_bar_close = bar_close_utc; break
                if bar.low  <= tp_:
                    result_str, r_out, pnl_gross = "WIN",  +2.0, +RISK_PER_TRADE*2
                    result_bar_close = bar_close_utc; break

            if bar_close_utc >= t_trade_kill:
                move      = (bar.close - ent_) if dir_ == "LONG" else (ent_ - bar.close)
                mv_pip    = p2pip(move)
                pnl_gross = stake * mv_pip
                r_out     = mv_pip / sl_pip_ if sl_pip_ > 0 else 0
                result_str = "TIMEOUT"
                result_bar_close = bar_close_utc; break

        trade = Trade(date=str(d), direction=dir_, range_size_pip=rpip,
            entry_price=ent_, stop_loss=sl_, take_profit=tp_,
            result=result_str, r_outcome=r_out,
            pnl_gbp=pnl_gross - spread_gbp, spread_cost=spread_gbp,
            reentry_flag=is_re, bst_flag=bst, week_balance=0,
            sl_method=sl_method, sl_param=sl_param, spread_pips=spread_pips,
            max_range_pip=max_range_pip, kill_time=kt_label, dow=dow, month=mon)
        return trade, result_bar_close

    t1, t1_result_ts = run_trade(direction, entry, sl, tp, sl_pip, trigger_bar.ts, False)
    results = [t1]

    # ── STEP 4: Re-entry ───────────────────────────────────────────────────────
    # Re-entry is only valid AFTER the first trade's SL is hit.
    # We start scanning entry_bars from after t1_result_ts (the 5M bar close
    # on which the SL was hit) so we never count bars while trade 1 is open.
    if allow_reentry and t1.result == "LOSS" and t1_result_ts is not None:
        bar_dur      = timedelta(minutes=1) if entry_bars is bars_1m else timedelta(minutes=5)
        in_range     = False
        re_candidates: List[Bar] = []

        for bar in entry_bars:
            close_utc = bar.ts + bar_dur
            if close_utc <= t1_result_ts:   # wait until first trade is closed
                continue
            if close_utc > t_kill_uk:       # re-entry must be before kill time
                break
            if not in_range and bar.low <= rh and bar.high >= rl:
                in_range = True
            if in_range:
                re_candidates.append(bar)

        re_trigger = find_trigger(re_candidates) if re_candidates else None
        if re_trigger:
            r_dir, r_ent, r_sl, r_tp, r_sl_pip, r_bar = re_trigger
            t2, _ = run_trade(r_dir, r_ent, r_sl, r_tp, r_sl_pip, r_bar.ts, True)
            results.append(t2)

    return results


# ── BACKTEST RUNNER ────────────────────────────────────────────────────────────

def run_backtest(
    day_data:      Dict[date, Tuple[List[Bar], List[Bar]]],
    trading_dates: List[date],
    max_range_pip: int,
    sl_method:     str,
    sl_param:      float,
    spread_pips:   int,
    kill_hm:       Tuple[int,int] = (7,0),
    allow_reentry: bool = True,
) -> List[Trade]:
    all_trades: List[Trade] = []
    balance = STARTING_BALANCE
    week_key = None
    week_bal = STARTING_BALANCE

    for d in sorted(trading_dates):
        if d not in day_data:
            continue
        b5, b1 = day_data[d]
        day_trades = simulate_day(d, b5, b1, max_range_pip, sl_method,
                                  sl_param, spread_pips, kill_hm, allow_reentry)
        for t in day_trades:
            if t.result not in ("SKIPPED","EXPIRED"):
                balance += t.pnl_gbp
        wk = d - timedelta(days=d.weekday())
        if wk != week_key:
            week_key = wk
            week_bal = balance
        for t in day_trades:
            t.week_balance = week_bal
            all_trades.append(t)
    return all_trades


# ── METRICS ────────────────────────────────────────────────────────────────────

def metrics(trades: List[Trade]) -> dict:
    active   = [t for t in trades if t.result in ("WIN","LOSS","TIMEOUT")]
    wins     = [t for t in active  if t.result == "WIN"]
    losses   = [t for t in active  if t.result == "LOSS"]
    timeouts = [t for t in active  if t.result == "TIMEOUT"]
    skipped  = [t for t in trades  if t.result == "SKIPPED"]
    expired  = [t for t in trades  if t.result == "EXPIRED"]
    n        = len(active)

    win_rate = len(wins)/n*100 if n else 0
    avg_w_g  = sum(t.pnl_gbp for t in wins)  /len(wins)   if wins   else 0
    avg_l_g  = sum(t.pnl_gbp for t in losses)/len(losses) if losses else 0
    avg_w_r  = sum(t.r_outcome for t in wins) /len(wins)  if wins   else 0
    avg_l_r  = sum(t.r_outcome for t in losses)/len(losses) if losses else 0
    net_pnl  = sum(t.pnl_gbp for t in active)
    gross_w  = sum(t.pnl_gbp for t in wins)
    gross_l  = abs(sum(t.pnl_gbp for t in losses))
    pf       = gross_w/gross_l if gross_l else float("inf")
    exp_g    = net_pnl/n if n else 0
    exp_r    = sum(t.r_outcome for t in active)/n if n else 0
    spread_t = sum(t.spread_cost for t in active)

    max_cl = cl = 0
    for t in active:
        if t.result=="LOSS": cl+=1; max_cl=max(max_cl,cl)
        else: cl=0

    bal=STARTING_BALANCE; peak=bal; max_dd=0.0
    for t in active:
        bal+=t.pnl_gbp
        if bal>peak: peak=bal
        max_dd=max(max_dd,peak-bal)

    return dict(
        n_days=len(set(t.date for t in trades)),
        n_active=n, n_wins=len(wins), n_losses=len(losses),
        n_timeouts=len(timeouts), n_skipped=len(skipped), n_expired=len(expired),
        win_rate=win_rate,
        avg_w_g=avg_w_g, avg_l_g=avg_l_g, avg_w_r=avg_w_r, avg_l_r=avg_l_r,
        exp_g=exp_g, exp_r=exp_r, pf=pf,
        net_pnl=net_pnl, spread_t=spread_t,
        max_cl=max_cl, max_dd=max_dd,
        max_dd_pct=max_dd/STARTING_BALANCE*100,
        ret_pct=net_pnl/STARTING_BALANCE*100,
    )


# ── PRINTING ───────────────────────────────────────────────────────────────────

W = 65
def hdr(title: str):
    print(f"\n{'='*W}\n  {title}\n{'='*W}")

def print_metrics(label: str, m: dict):
    hdr(label)
    print(f"  Days in data   : {m['n_days']}")
    print(f"  Skipped (range): {m['n_skipped']}")
    print(f"  Expired        : {m['n_expired']}")
    print(f"  Trades         : {m['n_active']}  "
          f"({m['n_wins']}W / {m['n_losses']}L / {m['n_timeouts']}T)")
    print(f"  Win rate       : {m['win_rate']:.1f}%")
    print(f"  Avg winner     : £{m['avg_w_g']:+.2f}  ({m['avg_w_r']:+.2f}R)")
    print(f"  Avg loser      : £{m['avg_l_g']:+.2f}  ({m['avg_l_r']:+.2f}R)")
    print(f"  Expectancy     : £{m['exp_g']:+.2f}/trade  ({m['exp_r']:+.4f}R)")
    print(f"  Profit factor  : {m['pf']:.2f}")
    print(f"  Net P&L        : £{m['net_pnl']:+,.2f}")
    print(f"  Spread cost    : £{m['spread_t']:,.2f}")
    print(f"  Max consec loss: {m['max_cl']}")
    print(f"  Max drawdown   : £{m['max_dd']:,.2f}  ({m['max_dd_pct']:.1f}%)")
    print(f"  Return (12mo)  : {m['ret_pct']:+.1f}%")


def print_weekly(trades: List[Trade]):
    by_wk: Dict[str,List[Trade]] = defaultdict(list)
    for t in trades:
        d  = date.fromisoformat(t.date)
        wk = str(d - timedelta(days=d.weekday()))
        by_wk[wk].append(t)

    print(f"\n  {'Week':^12}{'N':>5}{'W/L/E/T':>13}"
          f"{'GrossP&L':>11}{'Spread':>8}{'NetP&L':>10}{'Balance':>10}")
    print(f"  {'─'*69}")
    bal = STARTING_BALANCE
    for wk in sorted(by_wk):
        wt = by_wk[wk]
        ac = [t for t in wt if t.result in ("WIN","LOSS","TIMEOUT")]
        w  = sum(1 for t in ac if t.result=="WIN")
        l  = sum(1 for t in ac if t.result=="LOSS")
        e  = sum(1 for t in wt if t.result=="EXPIRED")
        to = sum(1 for t in ac if t.result=="TIMEOUT")
        gross = sum(t.pnl_gbp+t.spread_cost for t in ac)
        sp    = sum(t.spread_cost for t in ac)
        net   = sum(t.pnl_gbp for t in ac)
        bal  += net
        print(f"  {wk:<12}{len(ac):>5}{f'{w}W/{l}L/{e}E/{to}T':>13}"
              f"  £{gross:>+7.2f}  £{sp:>5.2f}  £{net:>+7.2f}  £{bal:>8,.2f}")
    print(f"  {'─'*69}")


def save_csv(trades: List[Trade], path: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path,"w",newline="") as f:
        w = csv.writer(f)
        w.writerow(["date","direction","range_size_pip","entry_price","stop_loss",
                    "take_profit","result","r_outcome","pnl_gbp","spread_cost",
                    "reentry_flag","bst_flag","week_balance",
                    "sl_method","sl_param","spread_pips","max_range_pip",
                    "kill_time","day_of_week","month"])
        for t in trades:
            w.writerow([t.date,t.direction,f"{t.range_size_pip:.2f}",
                f"{t.entry_price:.3f}",f"{t.stop_loss:.3f}",f"{t.take_profit:.3f}",
                t.result,f"{t.r_outcome:.3f}",f"{t.pnl_gbp:.2f}",f"{t.spread_cost:.2f}",
                t.reentry_flag,t.bst_flag,f"{t.week_balance:.2f}",
                t.sl_method,t.sl_param,t.spread_pips,t.max_range_pip,
                t.kill_time,t.dow,t.month])
    print(f"\n  CSV → {path}")


# ── MAIN ───────────────────────────────────────────────────────────────────────

def main():
    hdr("XAUUSD 06:30 London Open Range Breakout — 12-Month Backtest")

    end_date   = date.today()
    start_date = end_date - timedelta(days=365)
    print(f"\n  Period : {start_date} → {end_date}")
    print(f"  Pip    : ${PIP_SIZE:.2f} per pip  |  Risk: £{RISK_PER_TRADE}/trade")
    print(f"  Note   : Entry uses 1M closes (5M fallback if 1M window unavailable)")

    client = CTraderMCP(TOKEN)

    print("\n── Fetching per-day 5M + 1M bars ───────────────────────────")
    day_data = fetch_all_days(client, "XAUUSD", start_date, end_date)
    if not day_data:
        print("\n  [FATAL] No data. Check CTrader MCP connection.")
        sys.exit(1)

    print(f"  Pip digits detected: {client.pip_digits}")
    trading_dates = sorted(day_data.keys())

    # Diagnostic: show a sample day's bar count + timestamps
    sample_d = trading_dates[len(trading_dates)//2]
    s5, s1 = day_data[sample_d]
    print(f"\n  Sample day {sample_d}: {len(s5)} 5M bars, {len(s1)} 1M bars")
    if s5:
        print(f"    5M: {to_uk(s5[0].ts).strftime('%H:%M')} UK"
              f" → {to_uk(s5[-1].ts).strftime('%H:%M')} UK")
    if s1:
        print(f"    1M: {to_uk(s1[0].ts).strftime('%H:%M')} UK"
              f" → {to_uk(s1[-1].ts).strftime('%H:%M')} UK")

    # ── BASE CASE ──────────────────────────────────────────────────────────────
    print("\n\n── BASE CASE  (range≤20, SL A 3pip, spread 3, kill 07:00) ───")
    base = run_backtest(day_data, trading_dates, 20, "A", 3, 3, (7,0))
    bm   = metrics(base)
    print_metrics("BASE CASE — Max Range 20pip | Method A 3-pip | Spread 3", bm)

    if bm["n_active"] == 0:
        print("\n  [WARN] Zero trades — check bar timestamps in diagnostic above.")
        print("  Dumping first 5 days' 5M bar UK times:")
        for dd in trading_dates[:5]:
            b5,b1 = day_data[dd]
            tms = [to_uk(b.ts).strftime("%H:%M") for b in b5[:5]]
            print(f"    {dd}  5M bars: {tms}")
        return

    # Week-by-week
    print("\n\n── WEEK-BY-WEEK TABLE ────────────────────────────────────────")
    print_weekly(base)

    # ── IMPROVEMENT 1: KILL TIME ───────────────────────────────────────────────
    print("\n\n── IMP 1: KILL TIME OPTIMISATION ────────────────────────────")
    print(f"\n  {'Kill':>6}{'N':>6}{'Win%':>7}{'Exp(R)':>10}{'NetP&L':>11}")
    print(f"  {'─'*44}")
    for kh,km in KILL_TIMES:
        r = run_backtest(day_data, trading_dates, 20, "A", 3, 3, (kh,km))
        m = metrics(r)
        mark = " ← BASE" if (kh,km)==(7,0) else ""
        print(f"  {kh:02d}:{km:02d}{m['n_active']:>6}{m['win_rate']:>6.1f}%"
              f"{m['exp_r']:>+9.4f}R  £{m['net_pnl']:>+8.2f}{mark}")

    # ── IMPROVEMENT 2: RANGE SIZE ──────────────────────────────────────────────
    print("\n\n── IMP 2: RANGE SIZE SWEET SPOT ─────────────────────────────")
    print(f"\n  {'MaxRng':>8}{'N':>6}{'Win%':>7}{'Exp(R)':>10}{'NetP&L':>11}")
    print(f"  {'─'*46}")
    best_rng, best_rng_exp = 20, -999.0
    for mrp in MAX_RANGE_THRESHOLDS:
        r = run_backtest(day_data, trading_dates, mrp, "A", 3, 3, (7,0))
        m = metrics(r)
        mark = " ← BASE" if mrp==20 else ""
        print(f"  {mrp:>7}pip{m['n_active']:>6}{m['win_rate']:>6.1f}%"
              f"{m['exp_r']:>+9.4f}R  £{m['net_pnl']:>+8.2f}{mark}")
        if m["exp_r"] > best_rng_exp: best_rng_exp=m["exp_r"]; best_rng=mrp
    print(f"\n  → Best: {best_rng}pip  ({best_rng_exp:+.4f}R)")

    # ── IMPROVEMENT 3a: SL METHOD A ───────────────────────────────────────────
    print("\n\n── IMP 3a: SL BUFFER — METHOD A (Fixed Pip) ────────────────")
    print(f"\n  {'Buffer':>9}{'N':>6}{'Win%':>7}{'Exp(R)':>10}{'NetP&L':>11}")
    print(f"  {'─'*47}")
    best_sl_a, best_exp_a = 3, -999.0
    for buf in SL_BUFFERS_A:
        r = run_backtest(day_data, trading_dates, 20, "A", buf, 3, (7,0))
        m = metrics(r)
        mark = " ← BASE" if buf==3 else ""
        print(f"  {buf:>8}pip{m['n_active']:>6}{m['win_rate']:>6.1f}%"
              f"{m['exp_r']:>+9.4f}R  £{m['net_pnl']:>+8.2f}{mark}")
        if m["exp_r"] > best_exp_a: best_exp_a=m["exp_r"]; best_sl_a=buf

    # ── IMPROVEMENT 3b: SL METHOD B ───────────────────────────────────────────
    print("\n\n── IMP 3b: SL BUFFER — METHOD B (ATR-Based, 5M ATR) ────────")
    print(f"\n  {'ATR%':>9}{'N':>6}{'Win%':>7}{'Exp(R)':>10}{'NetP&L':>11}")
    print(f"  {'─'*47}")
    best_sl_b, best_exp_b = 0.10, -999.0
    for frac in ATR_FRACTIONS:
        r = run_backtest(day_data, trading_dates, 20, "B", frac, 3, (7,0))
        m = metrics(r)
        print(f"  {frac*100:>8.0f}%ATR{m['n_active']:>6}{m['win_rate']:>6.1f}%"
              f"{m['exp_r']:>+9.4f}R  £{m['net_pnl']:>+8.2f}")
        if m["exp_r"] > best_exp_b: best_exp_b=m["exp_r"]; best_sl_b=frac

    better = "A" if best_exp_a >= best_exp_b else "B"
    if better == "A":
        print(f"\n  → Best SL: Method A {best_sl_a}-pip ({best_exp_a:+.4f}R)")
    else:
        print(f"\n  → Best SL: Method B {best_sl_b*100:.0f}% ATR ({best_exp_b:+.4f}R)")

    # ── IMPROVEMENT 4: SPREAD SENSITIVITY ─────────────────────────────────────
    print("\n\n── IMP 4: SPREAD SENSITIVITY ────────────────────────────────")
    print(f"\n  {'Spread':>9}{'NetP&L':>12}{'vs Base':>10}")
    print(f"  {'─'*34}")
    for sp in SPREAD_COSTS:
        r = run_backtest(day_data, trading_dates, 20, "A", 3, sp, (7,0))
        m = metrics(r)
        mark = " ← BASE" if sp==3 else ""
        diff = m["net_pnl"] - bm["net_pnl"]
        print(f"  {sp:>8}pip  £{m['net_pnl']:>+9,.2f}  ({diff:>+7.2f}){mark}")

    # ── IMPROVEMENT 5: WHIPSAW RATE ───────────────────────────────────────────
    print("\n\n── IMP 5: FALSE BREAKOUT / WHIPSAW ──────────────────────────")
    active_b = [t for t in base if t.result in ("WIN","LOSS","TIMEOUT")]
    losses_b = [t for t in active_b if t.result=="LOSS"]
    wsr = len(losses_b)/len(active_b)*100 if active_b else 0
    print(f"\n  Trades: {len(active_b)} | Losses: {len(losses_b)} ({wsr:.1f}%)")
    print(f"\n  Day-of-week loss rate:")
    for day in ["Monday","Tuesday","Wednesday","Thursday","Friday"]:
        da = [t for t in active_b if t.dow==day]
        dl = [t for t in da       if t.result=="LOSS"]
        pct= len(dl)/len(da)*100 if da else 0
        print(f"    {day:<12}: {len(dl):>3}/{len(da):>3}  ({pct:.0f}%)")

    # ── IMPROVEMENT 6: DIRECTION BIAS ─────────────────────────────────────────
    print("\n\n── IMP 6: LONG vs SHORT ──────────────────────────────────────")
    for dir_ in ["LONG","SHORT"]:
        dr = [t for t in active_b if t.direction==dir_]
        if dr:
            wr  = sum(1 for t in dr if t.result=="WIN")/len(dr)*100
            net = sum(t.pnl_gbp for t in dr)
            print(f"  {dir_:>6}: {len(dr):>3} trades | {wr:.1f}% win | "
                  f"£{net:+,.2f} | £{net/len(dr):+.2f}/trade")

    # ── IMPROVEMENT 7: RE-ENTRY ────────────────────────────────────────────────
    print("\n\n── IMP 7: RE-ENTRY CONTRIBUTION ─────────────────────────────")
    no_re   = run_backtest(day_data, trading_dates, 20, "A", 3, 3, (7,0), allow_reentry=False)
    m_no_re = metrics(no_re)
    re_only = [t for t in active_b if t.reentry_flag]
    delta   = bm["net_pnl"] - m_no_re["net_pnl"]
    print(f"\n  Without re-entry: {m_no_re['n_active']} trades | "
          f"{m_no_re['win_rate']:.1f}% win | £{m_no_re['net_pnl']:+,.2f}")
    print(f"  With re-entry   : {bm['n_active']} trades | "
          f"{bm['win_rate']:.1f}% win | £{bm['net_pnl']:+,.2f}")
    print(f"  Re-entry delta  : £{delta:+,.2f}  "
          f"({'adds edge ✓' if delta>0 else 'detracts ✗'})")
    if re_only:
        rwr = sum(1 for t in re_only if t.result=="WIN")/len(re_only)*100
        rnet= sum(t.pnl_gbp for t in re_only)
        print(f"  Re-entry stats  : {len(re_only)} trades | {rwr:.1f}% win | "
              f"£{rnet:+,.2f} total | £{rnet/len(re_only):+.2f}/trade")

    # ── BREAKDOWNS ────────────────────────────────────────────────────────────
    print("\n\n── BREAKDOWN: DAY OF WEEK ────────────────────────────────────")
    print(f"\n  {'Day':<12}{'N':>5}{'Win%':>7}{'NetP&L':>11}")
    print(f"  {'─'*38}")
    for day in ["Monday","Tuesday","Wednesday","Thursday","Friday"]:
        dr  = [t for t in active_b if t.dow==day]
        if dr:
            wr  = sum(1 for t in dr if t.result=="WIN")/len(dr)*100
            net = sum(t.pnl_gbp for t in dr)
            print(f"  {day:<12}{len(dr):>5}{wr:>6.1f}%  £{net:>+8.2f}")

    print("\n\n── BREAKDOWN: BY MONTH ───────────────────────────────────────")
    print(f"\n  {'YearMonth':<12}{'N':>5}{'Win%':>7}{'NetP&L':>11}{'Period':>7}")
    print(f"  {'─'*45}")
    by_mon: Dict[str,List[Trade]] = defaultdict(list)
    for t in active_b:
        by_mon[date.fromisoformat(t.date).strftime("%Y-%m")].append(t)
    for ym in sorted(by_mon):
        res = by_mon[ym]
        wr  = sum(1 for t in res if t.result=="WIN")/len(res)*100
        net = sum(t.pnl_gbp for t in res)
        per = "BST" if any(t.bst_flag for t in res) else "GMT"
        print(f"  {ym:<12}{len(res):>5}{wr:>6.1f}%  £{net:>+8.2f}  {per:>5}")

    print("\n\n── BREAKDOWN: BST vs GMT ─────────────────────────────────────")
    for label,flag in [("BST (Mar–Oct)",True),("GMT (Oct–Mar)",False)]:
        sr  = [t for t in active_b if t.bst_flag==flag]
        if sr:
            wr  = sum(1 for t in sr if t.result=="WIN")/len(sr)*100
            net = sum(t.pnl_gbp for t in sr)
            print(f"  {label:<16}: {len(sr):>3} trades | {wr:.1f}% win | £{net:+,.2f}")

    # ── ALL 4 RANGE THRESHOLDS ─────────────────────────────────────────────────
    print("\n\n── FULL RESULTS: ALL RANGE THRESHOLDS ────────────────────────")
    for mrp in MAX_RANGE_THRESHOLDS:
        r = run_backtest(day_data, trading_dates, mrp, "A", 3, 3, (7,0))
        print_metrics(f"Max Range {mrp}pip | Method A 3-pip | Spread 3", metrics(r))

    # ── BEST COMBINATION ──────────────────────────────────────────────────────
    print("\n\n── BEST PARAMETER SEARCH ────────────────────────────────────")
    best_exp, best_p, best_r = -999.0, {}, []
    for mrp in MAX_RANGE_THRESHOLDS:
        for buf in SL_BUFFERS_A:
            r = run_backtest(day_data, trading_dates, mrp, "A", buf, 3, (7,0))
            m = metrics(r)
            if m["n_active"] >= 15 and m["exp_r"] > best_exp:
                best_exp = m["exp_r"]
                best_p   = dict(range=mrp, buf=buf)
                best_r   = r
    if best_r:
        print(f"\n  ★ BEST: Range≤{best_p['range']}pip | SL A {best_p['buf']}-pip | Spread 3")
        print_metrics("BEST COMBINATION", metrics(best_r))

    # ── CSV ───────────────────────────────────────────────────────────────────
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs")
    save_csv(base,    os.path.join(out, "base_trades.csv"))
    if best_r:
        save_csv(best_r, os.path.join(out, "best_trades.csv"))

    # ── EXECUTIVE SUMMARY ─────────────────────────────────────────────────────
    hdr("EXECUTIVE SUMMARY")
    bp = best_p if best_r else {}
    print(f"""
  STRATEGY : XAUUSD 06:30 London Open Range Breakout
  PERIOD   : {start_date} → {end_date}
  BASE CASE: Range≤20pip | Method A 3-pip SL | 3-pip spread | Kill 07:00

  RESULT       : Net P&L £{bm['net_pnl']:+,.2f}  ({bm['ret_pct']:+.1f}% on £10,000)
  Win rate     : {bm['win_rate']:.1f}%  |  Profit factor: {bm['pf']:.2f}
  Expectancy   : £{bm['exp_g']:+.2f}/trade  ({bm['exp_r']:+.4f}R)
  Max drawdown : £{bm['max_dd']:,.2f}  ({bm['max_dd_pct']:.1f}%)

  TOP 3 RECOMMENDATIONS:
  1. Optimal range filter : {best_rng}pip max — cleaner breakouts, fewer false signals
  2. Optimal SL buffer    : {f"Method A {best_sl_a}-pip" if best_exp_a>=best_exp_b else f"Method B {best_sl_b*100:.0f}% ATR"}
  3. Re-entry rule        : {'Keep — adds £' + f'{delta:,.2f}' if delta>0 else 'Remove — detracts £' + f'{abs(delta):,.2f}'}
""")
    print("  Done. Outputs saved to ./outputs/")


if __name__ == "__main__":
    main()
