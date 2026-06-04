#!/usr/bin/env python3
"""
cTrader HTTP Fallback for Trade Picker
Fetches 4H OHLCV from Pepperstone SB account via direct MCP HTTP,
calculates all confluence signals, and outputs ranked results as JSON.

Usage: python3 "Trade Picker/ctrader_fallback.py"
"""
import requests, json, sys
from datetime import datetime, timedelta

BEARER = "eyJwbGFudCI6InBlcHBlcnN0b25ldWsiLCJlbnZpcm9ubWVudCI6ImRlbW8iLCJ0b2tlbiI6IkliMEJzUERzSXBpZUJnTEtUWTluRjRpMEJ6a3R4V0pvSm1ZNVB3a1lIb2c9In0"
MCP_URL = "https://mcp.ctrader.com/trading/mcp"

# (name, symbolId, pip_div, market_type, max_score)
INSTRUMENTS = [
    ("EURUSD",  185, 100000, "forex",     9),
    ("GBPUSD",  199, 100000, "forex",     9),
    ("USDJPY",  226, 100000, "forex",     9),
    ("USDCHF",  222, 100000, "forex",     9),
    ("USDCAD",  221, 100000, "forex",     9),
    ("AUDUSD",  158, 100000, "forex",     9),
    ("NZDUSD",  211, 100000, "forex",     9),
    ("GBPJPY",  192, 100000, "forex",     9),
    ("EURJPY",  177, 100000, "forex",     9),
    ("AUDJPY",  155, 100000, "forex",     9),
    ("EURGBP",  175, 100000, "forex",     9),
    ("GBPAUD",  189, 100000, "forex",     9),
    ("EURCAD",  172, 100000, "forex",     9),
    ("GBPCAD",  190, 100000, "forex",     9),
    ("US500",   220, 100000, "index",    10),
    ("NAS100",  205, 100000, "index",    10),
    ("US30",    219, 100000, "index",    10),
    ("UK100",   217, 100000, "index",    10),
    ("GER40",   200, 100000, "index",    10),
    ("FRA40",   188, 100000, "index",    10),
    ("EUSTX50", 187, 100000, "index",    10),
    ("JPN225",  203, 100000, "index",    10),
    ("AUS200",  159, 100000, "index",    10),
    ("HK50",    201, 100000, "index",    10),
    ("GOLD",    241, 100000, "commodity", 9),
    ("SILVER",  238, 100000, "commodity", 9),
    ("CRUDE",   252, 100000, "commodity", 9),
    ("BRENT",   253, 100000, "commodity", 9),
    ("NATGAS",  254,  10000, "commodity", 9),
]

HEADERS_BASE = {
    "Authorization": f"Bearer {BEARER}",
    "Content-Type":  "application/json",
    "Accept":        "application/json, text/event-stream",
}

def init_session():
    r = requests.post(MCP_URL, headers=HEADERS_BASE, json={
        "jsonrpc": "2.0", "id": 1, "method": "initialize",
        "params": {"protocolVersion": "2024-11-05", "capabilities": {},
                   "clientInfo": {"name": "trade-picker-fallback", "version": "1.0"}}
    }, timeout=15)
    return r.headers.get("mcp-session-id")

def mcp_call(session_id, tool, args):
    h = {**HEADERS_BASE, "mcp-session-id": session_id}
    r = requests.post(MCP_URL, headers=h, json={
        "jsonrpc": "2.0", "id": 1, "method": "tools/call",
        "params": {"name": tool, "arguments": args}
    }, timeout=30)
    for line in r.text.split('\n'):
        if line.startswith('data:'):
            try:
                d = json.loads(line[5:].strip())
            except Exception:
                continue
            if 'result' in d:
                return d['result']
    return None

def extract_text(result):
    if not result:
        return None
    for item in result.get('content', []):
        if item.get('type') == 'text':
            try:
                return json.loads(item['text'])
            except Exception:
                return item.get('text')
    return None

def wilder_smooth(vals, period):
    if len(vals) < period:
        return []
    ws = sum(vals[:period])
    out = [ws]
    for v in vals[period:]:
        ws = ws - ws / period + v
        out.append(ws)
    return out

def calc_ema(vals, period):
    if len(vals) < period:
        return None
    k = 2.0 / (period + 1)
    e = sum(vals[:period]) / period
    for v in vals[period:]:
        e = v * k + e * (1 - k)
    return e

def score(name, bars, live_bid, live_ask, div, max_score, mtype):
    if not bars or len(bars) < 30:
        return {"name": name, "skip": f"Only {len(bars) if bars else 0} bars returned"}

    closes = [b['c'] for b in bars]
    highs  = [b['h'] for b in bars]
    lows   = [b['l'] for b in bars]
    n = len(closes)

    live_mid = (live_bid + live_ask) / 2 if (live_bid and live_ask) else closes[-1]
    spread_pct = (live_ask - live_bid) / live_mid * 100 if (live_bid and live_ask) else 0

    if spread_pct > 0.1:
        return {"name": name, "disq": f"Spread {spread_pct:.4f}% > 0.1%"}

    # ── BB20 ──────────────────────────────────────────────
    rc = closes[-20:]
    sma20 = sum(rc) / 20
    std20 = (sum((x - sma20) ** 2 for x in rc) / 20) ** 0.5
    bb_u  = sma20 + 2 * std20
    bb_l  = sma20 - 2 * std20

    # ── RSI14 ─────────────────────────────────────────────
    diffs = [closes[i] - closes[i-1] for i in range(n-14, n)]
    gains = [max(d, 0) for d in diffs]
    losss = [max(-d, 0) for d in diffs]
    ag = sum(gains) / 14;  al = sum(losss) / 14
    rsi = 100 - (100 / (1 + ag / al)) if al > 0 else 100.0

    # ── Stoch %K14 ────────────────────────────────────────
    lo14 = min(lows[-14:]);   hi14 = max(highs[-14:])
    stk  = (closes[-1] - lo14) / (hi14 - lo14) * 100 if (hi14 - lo14) > 0 else 50.0

    # ── EMA200 ────────────────────────────────────────────
    ema200     = calc_ema(closes, 200) if n >= 200 else None
    ema200_pct = abs(live_mid - ema200) / ema200 * 100 if ema200 else None

    # ── MACD 12/26/9 ──────────────────────────────────────
    macd_cross = None
    if n >= 40:
        k12, k26, k9 = 2/13, 2/27, 2/10
        e12 = sum(closes[:12]) / 12
        e26 = sum(closes[:26]) / 26
        macd_line = []
        for i in range(26, n):
            e12 = closes[i] * k12 + e12 * (1 - k12)
            e26 = closes[i] * k26 + e26 * (1 - k26)
            macd_line.append(e12 - e26)
        if len(macd_line) >= 10:
            sig = sum(macd_line[:9]) / 9
            sig_line = [sig]
            for m in macd_line[9:]:
                sig = m * k9 + sig * (1 - k9)
                sig_line.append(sig)
            if len(sig_line) >= 2 and len(macd_line) >= 2:
                pm = macd_line[-2];  cm = macd_line[-1]
                ps = sig_line[-2];   cs = sig_line[-1]
                if pm < ps and cm > cs:
                    macd_cross = "bullish"
                elif pm > ps and cm < cs:
                    macd_cross = "bearish"

    # ── ADX14 (Wilder's smoothing) ────────────────────────
    trs, pds, mds = [], [], []
    for i in range(1, n):
        tr  = max(highs[i]-lows[i], abs(highs[i]-closes[i-1]), abs(lows[i]-closes[i-1]))
        up  = highs[i] - highs[i-1]
        dn  = lows[i-1] - lows[i]
        pds.append(up if up > dn and up > 0 else 0)
        mds.append(dn if dn > up and dn > 0 else 0)
        trs.append(tr)
    adx = 25.0  # fallback neutral
    atr_val = sum(trs[-14:]) / 14 if len(trs) >= 14 else 0
    if len(trs) >= 28:
        sm_tr  = wilder_smooth(trs, 14)
        sm_pd  = wilder_smooth(pds, 14)
        sm_md  = wilder_smooth(mds, 14)
        dxs = []
        for i in range(len(sm_tr)):
            pdi = sm_pd[i] / sm_tr[i] * 100 if sm_tr[i] > 0 else 0
            mdi = sm_md[i] / sm_tr[i] * 100 if sm_tr[i] > 0 else 0
            dx  = abs(pdi - mdi) / (pdi + mdi) * 100 if (pdi + mdi) > 0 else 0
            dxs.append(dx)
        adx_sm = wilder_smooth(dxs, 14)
        if adx_sm:
            adx = adx_sm[-1] / 14  # normalise Wilder sum to average

    if adx > 30:
        return {"name": name, "disq": f"ADX {adx:.1f} > 30 (trending)"}

    # ── Score ─────────────────────────────────────────────
    ls = ss = 0
    sl, sh = [], []

    if live_mid <= bb_l:
        ls += 2; sl.append(f"BB lower breach  (mid {live_mid:.5f} ≤ {bb_l:.5f})")
    if live_mid >= bb_u:
        ss += 2; sh.append(f"BB upper breach  (mid {live_mid:.5f} ≥ {bb_u:.5f})")
    if stk < 15:
        ls += 2; sl.append(f"Stoch %K oversold ({stk:.1f})")
    if stk > 85:
        ss += 2; sh.append(f"Stoch %K overbought ({stk:.1f})")
    if ema200_pct is not None and ema200_pct <= 0.1:
        ls += 2; ss += 2
        sl.append(f"EMA200 confluence ({ema200_pct:.3f}% away, EMA200={ema200:.5f})")
        sh.append(f"EMA200 confluence ({ema200_pct:.3f}% away, EMA200={ema200:.5f})")
    if rsi < 35:
        ls += 1; sl.append(f"RSI oversold ({rsi:.1f})")
    if rsi > 65:
        ss += 1; sh.append(f"RSI overbought ({rsi:.1f})")
    if macd_cross == "bullish":
        ls += 1; sl.append("MACD bullish crossover (confirmed last 4H bar)")
    if macd_cross == "bearish":
        ss += 1; sh.append("MACD bearish crossover (confirmed last 4H bar)")
    if adx < 20:
        ls += 1; ss += 1
        sl.append(f"ADX weak trend ({adx:.1f})")
        sh.append(f"ADX weak trend ({adx:.1f})")

    if ls >= ss:
        raw = ls; direction = "LONG";  signals = sl
    else:
        raw = ss; direction = "SHORT"; signals = sh

    return {
        "name":       name,
        "type":       mtype,
        "direction":  direction,
        "raw":        raw,
        "max":        max_score,
        "norm":       round(raw / max_score * 10, 1),
        "mid":        round(live_mid, 5),
        "bid":        round(live_bid, 5) if live_bid else None,
        "ask":        round(live_ask, 5) if live_ask else None,
        "spread_pct": round(spread_pct, 4),
        "bb_upper":   round(bb_u, 5),
        "bb_lower":   round(bb_l, 5),
        "rsi":        round(rsi, 1),
        "stoch_k":    round(stk, 1),
        "ema200":     round(ema200, 5) if ema200 else None,
        "ema200_pct": round(ema200_pct, 3) if ema200_pct else None,
        "adx":        round(adx, 1),
        "atr":        round(atr_val, 5),
        "macd_cross": macd_cross,
        "signals":    signals,
        "bars":       n,
    }


def renew_session():
    """Re-initialise and return a fresh session id; exits on failure."""
    sid = init_session()
    if not sid:
        print("ERROR: could not initialise/renew session", file=sys.stderr)
        sys.exit(1)
    return sid


def safe_mcp_call(sid_ref, tool, args):
    """
    Call mcp_call; if result is None (session expired), renew session once and retry.
    sid_ref is a one-element list so we can mutate it from the caller.
    """
    result = mcp_call(sid_ref[0], tool, args)
    if result is None:
        print(f"\n  [session expired — renewing]", file=sys.stderr, end=" ", flush=True)
        sid_ref[0] = renew_session()
        result = mcp_call(sid_ref[0], tool, args)
    return result


def main():
    print("Initialising cTrader session...", file=sys.stderr)
    sid_ref = [renew_session()]
    print(f"Session: {sid_ref[0]}", file=sys.stderr)

    now       = datetime.utcnow()
    to_ts     = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    # Window 1: most recent 30 days
    from_ts1  = (now - timedelta(hours=719)).strftime("%Y-%m-%dT%H:%M:%SZ")
    # Window 2: 30–60 days ago (for EMA200 — needs ~200 4H bars total)
    to_ts2    = (now - timedelta(hours=719)).strftime("%Y-%m-%dT%H:%M:%SZ")
    from_ts2  = (now - timedelta(hours=1438)).strftime("%Y-%m-%dT%H:%M:%SZ")

    # ── Batch live prices ─────────────────────────────────────────────────────
    all_ids    = [i[1] for i in INSTRUMENTS]
    id_to_div  = {i[1]: i[2] for i in INSTRUMENTS}
    print("Fetching live prices (batch)...", file=sys.stderr)
    pr  = safe_mcp_call(sid_ref, "get_spot_prices", {"symbolId": all_ids})
    pdata = extract_text(pr)
    live_prices = {}
    if pdata and isinstance(pdata, dict):
        for sp in pdata.get('prices', []):
            sid_p = sp.get('symbolId')
            d = id_to_div.get(sid_p, 100000)
            live_prices[sid_p] = (sp.get('bid', 0) / d, sp.get('ask', 0) / d)
    print(f"  Got prices for {len(live_prices)} instruments", file=sys.stderr)

    results = []
    for name, sym_id, div, mtype, max_sc in INSTRUMENTS:
        print(f"  {name}...", file=sys.stderr, end=" ", flush=True)

        def fetch_bars(from_t, to_t):
            raw = safe_mcp_call(sid_ref, "get_trendbars", {
                "symbolId": sym_id, "period": "H_4",
                "fromTimestamp": from_t, "toTimestamp": to_t
            })
            data = extract_text(raw)
            if data and isinstance(data, dict):
                return [{"o": b.get('open',0)/div, "h": b.get('high',0)/div,
                         "l": b.get('low',0)/div,  "c": b.get('close',0)/div}
                        for b in data.get('trendbars', []) if b.get('close')]
            return []

        # Fetch two windows and concatenate (older first) for EMA200 coverage
        bars_old = fetch_bars(from_ts2, to_ts2)
        bars_new = fetch_bars(from_ts1, to_ts)
        bars = bars_old + bars_new

        bid, ask = live_prices.get(sym_id, (None, None))
        r = score(name, bars, bid, ask, div, max_sc, mtype)
        results.append(r)
        status = r.get('norm', 'skip') if not r.get('skip') and not r.get('disq') else r.get('disq', r.get('skip', '?'))
        print(f"{status}  [{len(bars)} bars]", file=sys.stderr)

    valid = sorted(
        [r for r in results if not r.get('disq') and not r.get('skip')],
        key=lambda x: x['norm'], reverse=True
    )
    out = {
        "scanned_at":   to_ts,
        "top3":         valid[:3],
        "all_ranked":   valid,
        "disqualified": [r for r in results if r.get('disq')],
        "skipped":      [r for r in results if r.get('skip')],
    }
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
