"""Desi Trades (Chart Fanatics) ICT layered model, coded mechanically on NAS100 m5 (NQ proxy). Screening only.
Bearish (bullish = mirror on inverted prices):
 1. Sweep: price trades above the previous day's high or previous week's high (NY days, 18:00 start).
 2. 4H inversion: within 48 h of the sweep, a 4H candle (NY 18,22,02,06,10,14) closes below the bottom of a bullish
    4H fair value gap formed in the last 12 4H candles -> bearish bias for the rest of that day and the next NY session.
 3. NY 10:00-12:00 only: price retraces up into a bearish 15m FVG formed after the inversion (still unfilled);
    5m bullish FVGs formed during that retrace; entry on the first 5m close below the bottom of one of them.
    Stop = retrace high + 2 pts. Setup dies on a 15m-FVG close-through.
 4. Half off at `tp1` R, stop to break-even, runner to the previous day's low (or 15:55 NY). Max 2 trades a day,
    stop after 2 losses. Cost = spread per trade."""
import csv
import json
import statistics as st
import sys
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

NY = ZoneInfo("America/New_York")
raw = []
for r in csv.DictReader(open("/home/user/CTrader-Bots/US30 London Range Breakout/data/NAS100/nas100_m5.csv")):
    t = datetime.fromtimestamp(int(r["timestamp_ms"]) / 1000, timezone.utc).astimezone(NY)
    raw.append((t, float(r["open"]), float(r["high"]), float(r["low"]), float(r["close"])))


def sday(t):  # NY trading day starting 18:00
    return (t + timedelta(hours=6)).date()


def agg(bars, key):
    out = []
    for t, o, h, l, c in bars:
        k = key(t)
        if out and out[-1][0] == k:
            x = out[-1]; x[2] = max(x[2], h); x[3] = min(x[3], l); x[4] = c; x[5] = t
        else:
            out.append([k, o, h, l, c, t])
    return out


def run(bars, cost, tp1=1.5, runner=True):
    day = agg(bars, sday)
    dhi = {d[0]: d[2] for d in day}; dlo = {d[0]: d[3] for d in day}
    days = [d[0] for d in day]
    prev = {days[i]: days[i - 1] for i in range(1, len(days))}
    wk = defaultdict(lambda: [-1e18, 1e18])
    for d in days:
        k = d.isocalendar()[:2]; wk[k][0] = max(wk[k][0], dhi[d]); wk[k][1] = min(wk[k][1], dlo[d])
    pwh = {}
    for d in days:
        y, w = d.isocalendar()[:2]
        pk = (d - timedelta(days=7)).isocalendar()[:2]
        pwh[d] = wk[pk][0] if pk in wk else 1e18
    trades = []
    h4, m15, f4, f15 = [], [], [], []
    sweep_t, bias_until, bias_t = None, None, None
    st_ = {}
    pos = None
    for i, (t, o, h, l, c) in enumerate(bars):
        d = sday(t); pd = prev.get(d)
        if pd is None:
            continue
        if h > dhi[pd] or h > pwh[d]:
            sweep_t = t
        # 4H candles
        k4 = (d, ((t.hour - 18) % 24) // 4)
        if h4 and h4[-1][0] == k4:
            x = h4[-1]; x[2] = max(x[2], h); x[3] = min(x[3], l); x[4] = c
        else:
            if h4:
                done = h4[-1]
                if len(h4) >= 3:
                    a, b_, cc = h4[-3], h4[-2], h4[-1]
                    if cc[3] > a[2]: f4.append((len(h4), a[2], cc[3]))
                f4 = [g for g in f4 if len(h4) - g[0] <= 12]
                if sweep_t and t - sweep_t <= timedelta(hours=48) and any(done[4] < g[1] for g in f4):
                    bias_t = t
                    bias_until = (t + timedelta(days=1)).replace(hour=16, minute=0)
                    f4 = [g for g in f4 if done[4] >= g[1]]
            h4.append([k4, o, h, l, c])
        # 15m candles and bearish FVGs after the bias
        k15 = t.replace(minute=t.minute - t.minute % 15)
        if m15 and m15[-1][0] == k15:
            x = m15[-1]; x[2] = max(x[2], h); x[3] = min(x[3], l); x[4] = c
        else:
            if len(m15) >= 3 and bias_t and m15[-3][0] >= bias_t - timedelta(minutes=15):
                a, cc = m15[-3], m15[-1]
                if cc[2] < a[3]: f15.append([cc[2], a[3]])
            m15.append([k15, o, h, l, c])
        if not bias_t or t > bias_until:
            f15 = []
        # manage position
        if pos:
            e, stop, risk, half, tgt = pos["e"], pos["stop"], pos["risk"], pos["half"], pos["tgt"]
            ex = None; mins = t.hour * 60 + t.minute
            if h >= stop: ex = stop
            elif not half and l <= e - tp1 * risk:
                pos["half"] = True; pos["stop"] = e
                if not runner: ex = e - tp1 * risk
            elif half and runner and l <= tgt: ex = tgt
            if ex is None and mins >= 955: ex = c
            if ex is not None:
                if pos["half"] and runner:
                    r = (tp1 * risk + (e - ex)) / 2
                elif pos["half"]:
                    r = tp1 * risk
                else:
                    r = e - ex
                trades.append((t.date(), (r - cost) / risk))
                ds = st_.setdefault(t.date(), [0, 0]); ds[0] += 1; ds[1] += (r - cost) < 0
                pos = None
            continue
        mins = t.hour * 60 + t.minute
        ds = st_.setdefault(t.date(), [0, 0])
        if not (600 <= mins < 720) or not bias_t or t > bias_until or ds[0] >= 2 or ds[1] >= 2:
            st_["touch"] = None
            continue
        tch = st_.get("touch")
        if tch is None:
            for g in f15:
                if h >= g[0] and c <= g[1]:
                    st_["touch"] = {"g": g, "hi": h, "f5": [], "start": i}
                    break
            continue
        if c > tch["g"][1]:
            f15.remove(tch["g"]) if tch["g"] in f15 else None
            st_["touch"] = None; continue
        tch["hi"] = max(tch["hi"], h)
        j = i
        if j - 2 >= tch["start"] - 6:
            a, cc = bars[j - 2], bars[j]
            if cc[3] > a[2]: tch["f5"].append(a[2])
        if tch["f5"] and c < min(tch["f5"]):
            stop = tch["hi"] + 2; risk = stop - c
            if 3 <= risk <= 120:
                tgt = min(dlo[pd], c - tp1 * risk)
                pos = {"e": c, "stop": stop, "risk": risk, "half": False, "tgt": tgt}
            st_["touch"] = None
    return trades


bot = dict(zip(*json.load(open(sys.argv[1])).values()))
inv = [(t, -o, -l, -h, -c) for t, o, h, l, c in raw]
# daily volatility (prior 14-day average range %) for a regime split
dr = agg(raw, sday)
rng = {x[0]: (x[2] - x[3]) / x[4] for x in dr}
dd_ = [x[0] for x in dr]
vol = {}
for k in range(14, len(dd_)):
    vol[dd_[k]] = st.mean(rng[x] for x in dd_[k - 14:k])
cut = sorted(vol.values())[len(vol) * 2 // 3]


def report(name, t):
    if not t:
        print(name, "none"); return
    rs = [x[1] for x in t]
    yr = defaultdict(float)
    for x in t: yr[x[0].year] += x[1]
    eq = pk = mdd = 0.0
    for r in rs: eq += r; pk = max(pk, eq); mdd = max(mdd, pk - eq)
    dv = defaultdict(float)
    for x in t: dv[x[0].strftime("%Y%m%d")] += x[1]
    com = [k for k in dv if k in bot]
    corr = st.correlation([bot[k] for k in com], [dv[k] for k in com]) if len(com) > 5 else float("nan")
    hv = [x[1] for x in t if vol.get(x[0], 0) >= cut]; lv = [x[1] for x in t if 0 < vol.get(x[0], 0) < cut]
    print(f"{name:26s} n={len(rs):3d} win={sum(r > 0 for r in rs) / len(rs):4.0%} avg={st.mean(rs):+.3f}R "
          f"tot={sum(rs):+6.1f}R dd={mdd:4.1f}R corr={corr:+.2f} | high-vol {len(hv)}: "
          f"{(st.mean(hv) if hv else 0):+.2f}R, rest {len(lv)}: {(st.mean(lv) if lv else 0):+.2f}R | "
          + " ".join(f"{y}:{v:+.0f}" for y, v in sorted(yr.items())))


for cost in (0.0, 1.2, 1.8):
    for tp1, runner in ((1.5, True), (2.0, False), (1.5, False)):
        t = sorted(run(raw, cost, tp1, runner) + run(inv, cost, tp1, runner))
        report(f"cost {cost} tp1 {tp1} runner {runner}", t)
