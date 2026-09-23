"""Tradeable test: fade the FIRST post-open touch of a pre-open OI level.

Entry  : first RTH bar whose range reaches a published gamma level (+/-8pts).
Side   : resistance if price approached from below -> short; support -> long.
Exit   : RTH close (no stop), plus MAE/MFE so a stop can be simulated after.
Control: same trade taken at the SAME BAR but at a price with no level
         (level +/- 50pts, i.e. the empty half of the grid).
"""
import json, glob, sys, statistics as st
from datetime import datetime, timezone, time as dtime
sys.path.insert(0, "/home/user/CTrader-Bots/.claude/skills/nas100-daily-brief/scripts")
import ctrader_http as ct, levels_fuel as LF

OPEN_UTC, CLOSE_UTC = dtime(13, 30), dtime(20, 0)
GK = {"gamma", "gamma-shelf"}
TOUCH = 8.0

def u(b):
    t = b["time"]
    if not isinstance(t, datetime): t = datetime.fromtimestamp(t/1000, timezone.utc)
    return t if t.tzinfo else t.replace(tzinfo=timezone.utc)

bars_all = ct.fetch_ohlcv_paged("NAS100", "M_5", days=45, max_calls=300)
byday = {}
for b in bars_all:
    byday.setdefault(str(LF.trading_day(b["time"])), []).append(b)

per_day = {}
for f in sorted(glob.glob("/home/user/CTrader-Bots/NAS100 Daily Brief agent skill/"
                          "journal/2026-*/[0-9]*.json")):
    d = json.load(open(f))
    if not d.get("is_trading_day") or not d.get("scan_utc"): continue
    t = datetime.fromisoformat(d["scan_utc"].replace("Z","+00:00")).astimezone(timezone.utc)
    if t.time() >= OPEN_UTC: continue
    day = d["trading_day"]
    if day not in per_day or t > per_day[day][0]: per_day[day] = (t, d)

def simulate(rth, lv):
    """Return (entry_bar_idx, level, side) for the first gamma touch."""
    prev = rth[0]["open"]
    for i, b in enumerate(rth):
        hits = [p for p in lv if b["low"] - TOUCH <= p <= b["high"] + TOUCH]
        if hits:
            p = min(hits, key=lambda q: abs(q - prev))
            side = "short" if p >= prev else "long"   # approached from below -> resistance
            return i, p, side
        prev = b["close"]
    return None, None, None

def outcome(rth, i, p, side):
    post = rth[i:]
    cl = post[-1]["close"]
    hi = max(b["high"] for b in post); lo = min(b["low"] for b in post)
    if side == "short":
        return dict(pnl=p - cl, mfe=p - lo, mae=hi - p)
    return dict(pnl=cl - p, mfe=hi - p, mae=p - lo)

real, ctrl = [], []
print(f"{'day':<12}{'t':>7}{'level':>10}{'side':>7}{'pnl':>9}{'MFE':>8}{'MAE':>8}   | control pnl")
for day in sorted(per_day):
    t_scan, d = per_day[day]
    bars = byday.get(day) or []
    rth = [b for b in bars if str(u(b).date()) == day and OPEN_UTC <= u(b).time() < CLOSE_UTC]
    if len(rth) < 20: continue
    lv = sorted({x["price"] for x in (d["prediction"].get("levels") or []) if x.get("kind") in GK})
    if not lv: continue
    i, p, side = simulate(rth, lv)
    if i is None:
        print(f"{day:<12}   no gamma level touched in RTH"); continue
    o = outcome(rth, i, p, side)
    real.append(o); 
    # control: same bar, same side, but the empty mid-grid price 50pts away
    cp = p + 50.0 if side == "short" else p - 50.0
    oc = outcome(rth, i, cp, side)
    ctrl.append(oc)
    print(f"{day:<12}{u(rth[i]).strftime('%H:%M'):>7}{p:>10.1f}{side:>7}"
          f"{o['pnl']:>+9.1f}{o['mfe']:>8.1f}{o['mae']:>8.1f}   | {oc['pnl']:>+8.1f}")

def summarise(name, xs):
    if not xs: return
    pnl = [x["pnl"] for x in xs]
    w = sum(1 for v in pnl if v > 0)
    print(f"\n{name}: n={len(pnl)}  wins {w}/{len(pnl)} ({100*w/len(pnl):.0f}%)  "
          f"mean {st.mean(pnl):+.1f}  median {st.median(pnl):+.1f}  "
          f"total {sum(pnl):+.1f}")
    print(f"   mean MFE {st.mean(x['mfe'] for x in xs):.1f}   "
          f"mean MAE {st.mean(x['mae'] for x in xs):.1f}   "
          f"worst {min(pnl):+.1f}   best {max(pnl):+.1f}")

summarise("FADE the first OI-level tag", real)
summarise("CONTROL (same bar, 50pts off-grid)", ctrl)
