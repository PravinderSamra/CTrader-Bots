"""Two Chart Fanatics intraday index models, coded mechanically on FTMO CFD m5 data (Jul 2023 - 2026). Screening only.

RAJAN D (DND Capital) 'auction' trend continuation, first hour only, 2:1:
  Long day: yesterday's session closed up AND above the daily EMA21 (optional: today's open gapped up).
  First hour after the cash open (NY 09:30 / Frankfurt 09:00): a 5m pullback bar that dips to the 5m EMA21
  (low <= EMA21 + 0.1 ATR) while the EMA is rising and the bar closes above it; buy on a break of that bar's high.
  Stop below the pullback bar's low, target 2R, flat after 2 hours. One trade a day. Shorts mirror.
JADECAP (Kyle) Asian-range sweep (ICT): Asian range = 20:00-00:00 New York.
  09:30-11:30 NY: price trades below the Asian low, then a 15m close back above it -> long at that close,
  stop under the lowest low since the sweep, target the Asian high (need >= 1.5R), exit at 12:00 NY (his time exit).
  Shorts mirror. Bias variants: none / yesterday closed above-below the daily EMA21. One trade a day.
Costs per round trip: NAS100 1.5, US30 2.5, GER40 1.5 points."""
import csv, statistics as st, sys
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

D = "/home/user/CTrader-Bots/US30 London Range Breakout/data"
NY, FR = ZoneInfo("America/New_York"), ZoneInfo("Europe/Berlin")
MK = {"NAS100": ("NAS100/nas100_m5.csv", 1.5, NY, (9, 30), (16, 0)),
      "US30": ("US30/us30_m5.csv", 2.5, NY, (9, 30), (16, 0)),
      "GER40": ("GER40/ger40_m5.csv", 1.5, FR, (9, 0), (17, 30))}


def load(f):
    out = []
    for r in csv.DictReader(open(f"{D}/{f}")):
        out.append((datetime.fromtimestamp(int(r["timestamp_ms"]) / 1000, timezone.utc),
                    float(r["open"]), float(r["high"]), float(r["low"]), float(r["close"])))
    return out


def ema(vals, n):
    a = 2 / (n + 1); e = None; o = []
    for v in vals:
        e = v if e is None else e + a * (v - e); o.append(e)
    return o


def sessions(bars, tz, op, cl):
    """per local date: list of bar indices inside the cash session, session open/close prices"""
    s = defaultdict(list)
    for i, (t, *_ ) in enumerate(bars):
        lt = t.astimezone(tz); hm = (lt.hour, lt.minute)
        if op <= hm < cl and lt.weekday() < 5:
            s[lt.date()].append(i)
    return dict(sorted(s.items()))


def rajan(bars, cost, tz, op, cl, gap):
    S = sessions(bars, tz, op, cl); days = list(S)
    dclose = [bars[S[d][-1]][4] for d in days]; dopen = [bars[S[d][0]][1] for d in days]
    e21 = ema(dclose, 21)
    closes = [b[4] for b in bars]; E = ema(closes, 21)
    atr = [0] * len(bars)
    for i in range(14, len(bars)):
        atr[i] = st.mean(b[2] - b[3] for b in bars[i - 13:i + 1])
    tr = []
    for k in range(22, len(days)):
        idx = S[days[k]]
        up = dclose[k - 1] > dopen[k - 1] and dclose[k - 1] > e21[k - 1]
        dn = dclose[k - 1] < dopen[k - 1] and dclose[k - 1] < e21[k - 1]
        g = bars[idx[0]][1] - dclose[k - 1]
        side = 1 if up and (not gap or g > 0) else -1 if dn and (not gap or g < 0) else 0
        if not side: continue
        done = False
        for n, i in enumerate(idx[1:12], 1):           # first hour of 5m bars
            t, o, h, l, c = bars[i]
            if side == 1:
                ok = l <= E[i] + 0.1 * atr[i] and c > E[i] and E[i] > E[i - 3]
                lvl, stp = h, l - 0.1 * atr[i]
            else:
                ok = h >= E[i] - 0.1 * atr[i] and c < E[i] and E[i] < E[i - 3]
                lvl, stp = l, h + 0.1 * atr[i]
            if not ok: continue
            j = i + 1
            if j >= len(bars) or (side == 1 and bars[j][2] <= lvl) or (side == -1 and bars[j][3] >= lvl):
                continue
            e = lvl if side == 1 else lvl
            e = max(e, bars[j][1]) if side == 1 else min(e, bars[j][1])
            r = abs(e - stp)
            if r <= 0: continue
            tgt = e + side * 2 * r; x = None
            for m in range(j, min(j + 24, len(bars))):  # 2 hours
                if side == 1:
                    if bars[m][3] <= stp: x = stp; break
                    if bars[m][2] >= tgt and m > j or (m == j and bars[m][4] >= tgt): x = tgt; break
                else:
                    if bars[m][2] >= stp: x = stp; break
                    if bars[m][3] <= tgt and m > j or (m == j and bars[m][4] <= tgt): x = tgt; break
            if x is None: x = bars[min(j + 23, len(bars) - 1)][4]
            tr.append((t, side * (x - e) / r - cost / r)); done = True
            break
    return tr


def jade(bars, cost, bias):
    by = defaultdict(list)
    for i, (t, *_ ) in enumerate(bars):
        by[t.astimezone(NY).date()].append(i)
    days = sorted(by)
    # daily close at 16:00 NY for EMA21 bias
    dc = {}
    for d in days:
        c = [i for i in by[d] if bars[i][0].astimezone(NY).hour < 16]
        if c: dc[d] = bars[c[-1]][4]
    dl = [d for d in days if d in dc]; e21 = dict(zip(dl, ema([dc[d] for d in dl], 21)))
    tr = []
    for k in range(25, len(days)):
        d, p = days[k], days[k - 1]
        asia = [i for i in by[p] if bars[i][0].astimezone(NY).hour >= 20]
        if len(asia) < 30 or p not in e21: continue
        ah = max(bars[i][2] for i in asia); al = min(bars[i][3] for i in asia)
        b_up = dc[p] > e21[p]
        sess = [i for i in by[d] if (9, 30) <= (bars[i][0].astimezone(NY).hour, bars[i][0].astimezone(NY).minute) < (11, 30)]
        lo = hi = None; done = False
        for i in sess:
            t, o, h, l, c = bars[i]; lt = t.astimezone(NY)
            if l < al: lo = l if lo is None else min(lo, l)
            if h > ah: hi = h if hi is None else max(hi, h)
            if lo is not None: lo = min(lo, l)
            if hi is not None: hi = max(hi, h)
            if (lt.minute + 5) % 15 != 0: continue        # act on 15m closes
            for side in (1, -1):
                if bias and ((side == 1) != b_up): continue
                if side == 1 and lo is not None and c > al:
                    e, stp, tgt = c, lo - 0.5 * cost, ah
                elif side == -1 and hi is not None and c < ah:
                    e, stp, tgt = c, hi + 0.5 * cost, al
                else: continue
                r = abs(e - stp)
                if r <= 0 or abs(tgt - e) < 1.5 * r: continue
                x = None
                for m in range(i + 1, len(bars)):
                    mt = bars[m][0].astimezone(NY)
                    if mt.date() != d or mt.hour >= 12: x = bars[m - 1][4]; break
                    if side == 1:
                        if bars[m][3] <= stp: x = stp; break
                        if bars[m][2] >= tgt: x = tgt; break
                    else:
                        if bars[m][2] >= stp: x = stp; break
                        if bars[m][3] <= tgt: x = tgt; break
                if x is None: x = bars[-1][4]
                tr.append((t, side * (x - e) / r - cost / r)); done = True
                break
            if done: break
    return tr


def kane(bars, cost, be):
    """TRADER KANE 10am NY hourly power-of-three, with the daily trend (yesterday's close vs daily EMA21):
    short day: the 10:00 hourly candle trades above the 09:00 hourly high, then a 5m close back below the 10:00 open
    -> short at that close, stop above the 10:00 high, target the low since 09:30 (need >= 1R), break-even after
    +1R if be, flat 12:00. Long days mirror."""
    by = defaultdict(list)
    for i, (t, *_ ) in enumerate(bars):
        by[t.astimezone(NY).date()].append(i)
    days = sorted(by); dc = {}
    for d in days:
        c = [i for i in by[d] if bars[i][0].astimezone(NY).hour < 16]
        if c: dc[d] = bars[c[-1]][4]
    dl = [d for d in days if d in dc]; e21 = dict(zip(dl, ema([dc[d] for d in dl], 21)))
    tr = []
    for k in range(25, len(days)):
        d, p = days[k], days[k - 1]
        if p not in e21: continue
        side = -1 if dc[p] < e21[p] else 1
        h9 = [i for i in by[d] if bars[i][0].astimezone(NY).hour == 9]
        h10 = [i for i in by[d] if bars[i][0].astimezone(NY).hour == 10]
        if len(h9) < 10 or len(h10) < 10: continue
        o930 = [i for i in h9 if bars[i][0].astimezone(NY).minute >= 30]
        x9 = max(bars[i][2] for i in h9) if side == -1 else min(bars[i][3] for i in h9)
        op10 = bars[h10[0]][1]; swept = False; ext = None
        for i in h10:
            t, o, h, l, c = bars[i]
            if side == -1:
                if h > x9: swept = True
                ext = h if ext is None else max(ext, h)
                trig = swept and c < op10
            else:
                if l < x9: swept = True
                ext = l if ext is None else min(ext, l)
                trig = swept and c > op10
            if not trig: continue
            e = c; stp = ext + side * -1 * 0.5 * cost if False else (ext + 0.5 * cost if side == -1 else ext - 0.5 * cost)
            seg = o930 + [j for j in h10 if j <= i]
            tgt = min(bars[j][3] for j in seg) if side == -1 else max(bars[j][2] for j in seg)
            r = abs(stp - e)
            if r <= 0 or abs(e - tgt) < r: break
            x = None; s_ = stp
            for m in range(i + 1, len(bars)):
                mt = bars[m][0].astimezone(NY)
                if mt.date() != d or mt.hour >= 12: x = bars[m - 1][4]; break
                hi, lo = bars[m][2], bars[m][3]
                if side == -1:
                    if hi >= s_: x = s_; break
                    if lo <= tgt: x = tgt; break
                    if be and lo <= e - r: s_ = min(s_, e)
                else:
                    if lo <= s_: x = s_; break
                    if hi >= tgt: x = tgt; break
                    if be and hi >= e + r: s_ = max(s_, e)
            if x is None: x = bars[-1][4]
            tr.append((t, side * (x - e) / r - cost / r))
            break
    return tr


def kane_tz(bars, cost, flat_h=12):
    """TRADER KANE, TradeZella playbook rules on top of kane(): same 10am sweep of the 09:00 hourly extreme and 5m
    close back through the 10:00 open, but target = 50% of the H1 dealing range (09:00 hour + 10:00 so far; need
    >= 0.5R), break-even once an 11:00-hour 5m close is past the 11:00 open in the trade's favour (his '11:00 candle
    flips'), flat at flat_h NY. No NQ/ES SMT filter (no ES intraday data)."""
    by = defaultdict(list)
    for i, (t, *_ ) in enumerate(bars):
        by[t.astimezone(NY).date()].append(i)
    days = sorted(by); dc = {}
    for d in days:
        c = [i for i in by[d] if bars[i][0].astimezone(NY).hour < 16]
        if c: dc[d] = bars[c[-1]][4]
    dl = [d for d in days if d in dc]; e21 = dict(zip(dl, ema([dc[d] for d in dl], 21)))
    tr = []
    for k in range(25, len(days)):
        d, p = days[k], days[k - 1]
        if p not in e21: continue
        side = -1 if dc[p] < e21[p] else 1
        h9 = [i for i in by[d] if bars[i][0].astimezone(NY).hour == 9]
        h10 = [i for i in by[d] if bars[i][0].astimezone(NY).hour == 10]
        if len(h9) < 10 or len(h10) < 10: continue
        x9 = max(bars[i][2] for i in h9) if side == -1 else min(bars[i][3] for i in h9)
        op10 = bars[h10[0]][1]; swept = False; ext = None
        for i in h10:
            t, o, h, l, c = bars[i]
            if side == -1:
                swept |= h > x9; ext = h if ext is None else max(ext, h); trig = swept and c < op10
            else:
                swept |= l < x9; ext = l if ext is None else min(ext, l); trig = swept and c > op10
            if not trig: continue
            seg = h9 + [j for j in h10 if j <= i]
            tgt = (max(bars[j][2] for j in seg) + min(bars[j][3] for j in seg)) / 2
            e = c; stp = ext + 0.5 * cost if side == -1 else ext - 0.5 * cost; r = abs(stp - e)
            if r <= 0 or side * (tgt - e) < 0.5 * r: break
            x = None; s_ = stp; op11 = None
            for m in range(i + 1, len(bars)):
                mt = bars[m][0].astimezone(NY)
                if mt.date() != d or mt.hour >= flat_h: x = bars[m - 1][4]; break
                H, L, C = bars[m][2], bars[m][3], bars[m][4]
                if side == -1:
                    if H >= s_: x = s_; break
                    if L <= tgt: x = tgt; break
                else:
                    if L <= s_: x = s_; break
                    if H >= tgt: x = tgt; break
                if mt.hour == 11:
                    if op11 is None: op11 = bars[m][1]
                    if side * (C - op11) > 0: s_ = min(s_, e) if side == -1 else max(s_, e)
            if x is None: x = bars[-1][4]
            tr.append((t, side * (x - e) / r - cost / r))
            break
    return tr


def summ(name, tr):
    if not tr: print(f"  {name:34s} no trades"); return
    rs = [r for _, r in tr]; yr = defaultdict(float)
    for t, r in tr: yr[t.year] += r
    print(f"  {name:34s} n={len(rs):4d} win={sum(r > 0 for r in rs)/len(rs):4.0%} avg={st.mean(rs):+.2f}R tot={sum(rs):+6.1f}R  "
          + " ".join(f"{y%100:02d}:{v:+.0f}" for y, v in sorted(yr.items())))


if __name__ == "__main__":
    for m, (f, cost, tz, op, cl) in MK.items():
        b = load(f)
        print(f"== {m} {b[0][0]:%Y-%m} .. {b[-1][0]:%Y-%m}")
        summ("Rajan, trend day, no gap rule", rajan(b, cost, tz, op, cl, False))
        summ("Rajan, trend day + gap same way", rajan(b, cost, tz, op, cl, True))
        if tz is NY:
            summ("Jade Asian sweep, no bias", jade(b, cost, False))
            summ("Jade Asian sweep, EMA21 bias", jade(b, cost, True))
            summ("Kane 10am PO3 with trend", kane(b, cost, False))
            summ("Kane 10am PO3 with trend, BE at 1R", kane(b, cost, True))
            summ("Kane TZ: 50% H1 range, 11h-flip BE", kane_tz(b, cost))
