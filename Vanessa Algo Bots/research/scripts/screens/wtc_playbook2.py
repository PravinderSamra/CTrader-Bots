"""Wealth Training Company playbook part 2, coded mechanically. Screening only. Market orders at bar closes.

EARLY ADOPTER (Ludo), indices, intraday on 5-min bars (the playbook uses 1-min; 5-min is the finest we have):
  Bias: yesterday's daily close above the daily 10/20/50/100/200 EMAs -> longs only (below all -> shorts).
  Pivots: Tue-Fri from the previous day (NY 18:00 roll), Monday from the previous week. P=(H+L+C)/3,
  R1=2P-L, R2=P+(H-L), R3=H+2(P-L) (mirror S levels for shorts). Trade only above P (longs).
  5-min, 10:00-15:00 NY: 10 & 20 EMA above the 200 EMA; momentum = a new session high in the last 12 bars;
  pullback bar touches the 10 or 20 EMA; trigger = bullish candle closing above the previous (red) bar's open ->
  buy at the close. Stop below all EMAs (10/20/50/100/200) - 0.5 cost. Target R3 (Monday: weekly R1);
  skip unless >= 5R. Management: close above R1 -> stop to entry; close above R2 -> stop to R1. Flat 16:00 NY.
SWING (Darren Winters), FTMO's 45 US stocks, daily (Yahoo, scratchpad/ep), long in uptrends / short in downtrends:
  Trend: close above the 200-day SMA and the 50-day SMA rising (mirror for shorts). The playbook's 6-18 month
  trendline with 3 touches can't be drawn objectively and is replaced by this trend test.
  Signal day: at least 3 of 4: RSI(14) crossed 50 in the last 3 days after being < 45 in the last 10;
  CCI(20) crossed back over -100 in the last 5 days; MACD line crossed its signal in the last 3 days;
  Stochastic %K(14,3) crossed %D in the last 3 days after being < 30 in the last 5.
  Buy next open; stop = 10-day low; target 2R (the playbook gives none); 20-day time stop. Cost 0.15% + swap."""
import glob, statistics as st, sys
from collections import defaultdict
from datetime import timedelta
from zoneinfo import ZoneInfo
from wtc_playbook import ema, rsi, cci, inv, summ

NY = ZoneInfo("America/New_York")
SP = "/tmp/claude-0/-home-user-CTrader-Bots/05dd4dd7-22e7-57bf-8cec-d6a0c9610eea/scratchpad"


def early_adopter(bars, cost, side):
    b = bars if side == 1 else inv(bars)
    c = [x[4] for x in b]; E = {n: ema(c, n) for n in (10, 20, 50, 100, 200)}
    # daily bars on the NY 18:00 roll
    key = lambda t: (t.astimezone(NY) + timedelta(hours=6)).date()
    dk = defaultdict(list)
    for i, x in enumerate(b): dk[key(x[0])].append(i)
    days = sorted(dk)
    D = {d: (b[dk[d][0]][1], max(b[i][2] for i in dk[d]), min(b[i][3] for i in dk[d]), b[dk[d][-1]][4]) for d in days}
    dc = [D[d][3] for d in days]; DE = {n: ema(dc, n) for n in (10, 20, 50, 100, 200)}
    tr = []
    for k in range(205, len(days)):
        d, p = days[k], days[k - 1]
        if not all(dc[k - 1] > DE[n][k - 1] for n in DE): continue
        if d.weekday() == 0:
            wk = [x for x in days[max(0, k - 8):k] if x.isocalendar()[1] == p.isocalendar()[1]]
            H = max(D[x][1] for x in wk); L = min(D[x][2] for x in wk); C = D[wk[-1]][3]
        else:
            _, H, L, C = D[p]
        P = (H + L + C) / 3; R1 = 2 * P - L; R2 = P + (H - L); R3 = H + 2 * (P - L)
        tgt = R1 if d.weekday() == 0 else R3
        idx = [i for i in dk[d] if (9, 30) <= (b[i][0].astimezone(NY).hour, b[i][0].astimezone(NY).minute) < (16, 0)]
        if len(idx) < 60: continue
        for n_, i in enumerate(idx):
            t, o, h, l, cl = b[i]; lt = t.astimezone(NY)
            if not ((10, 0) <= (lt.hour, lt.minute) < (15, 0)) or n_ < 13: continue
            if cl <= P or not (E[10][i] > E[200][i] and E[20][i] > E[200][i]): continue
            sess_hi = max(b[j][2] for j in idx[:n_]); recent_hi = max(b[j][2] for j in idx[n_ - 12:n_])
            if recent_hi < sess_hi: continue
            pb = b[i - 1]
            if not (pb[3] <= E[20][i - 1] or pb[3] <= E[10][i - 1]): continue
            if not (cl > o and pb[4] < pb[1] and cl > pb[1]): continue
            stop = min(E[n][i] for n in E) - 0.5 * cost; e = cl; r = e - stop
            if r <= 0 or tgt - e < 5 * r: continue
            s = stop; x = None
            for j in idx[n_ + 1:]:
                if b[j][3] <= s: x = s; break
                if b[j][2] >= tgt: x = tgt; break
                if b[j][4] > R2 and R1 > e: s = max(s, R1)
                elif b[j][4] > R1: s = max(s, e)
            if x is None: x = b[idx[-1]][4]
            tr.append((t, (x - e - cost) / r)); break
    return tr


def swing(b, cost):
    c = [x[4] for x in b]; n = len(b)
    R = rsi(c); C = cci(b); fast, slow = ema(c, 12), ema(c, 26); mac = [a - z for a, z in zip(fast, slow)]; sig = ema(mac, 9)
    K = [None] * n
    for i in range(13, n):
        hh = max(x[2] for x in b[i - 13:i + 1]); ll = min(x[3] for x in b[i - 13:i + 1])
        K[i] = 50 if hh == ll else 100 * (c[i] - ll) / (hh - ll)
    Ks = [None] * n; Ds = [None] * n
    for i in range(16, n): Ks[i] = sum(K[i - 2:i + 1]) / 3
    for i in range(18, n): Ds[i] = sum(Ks[i - 2:i + 1]) / 3
    sma = lambda i, k: sum(c[i - k + 1:i + 1]) / k
    tr = []; i = 210
    while i < n - 2:
        if not (c[i] > sma(i, 200) and sma(i, 50) > sma(i - 5, 50)): i += 1; continue
        s1 = any(R[k - 1] < 50 <= R[k] for k in range(i - 2, i + 1)) and min(R[i - 10:i]) < 45
        s2 = any(C[k - 1] < -100 <= C[k] for k in range(i - 4, i + 1))
        s3 = any(mac[k - 1] <= sig[k - 1] and mac[k] > sig[k] for k in range(i - 2, i + 1))
        s4 = any(Ks[k - 1] <= Ds[k - 1] and Ks[k] > Ds[k] for k in range(i - 2, i + 1)) and min(Ks[i - 4:i + 1]) < 30
        if s1 + s2 + s3 + s4 < 3: i += 1; continue
        e = b[i + 1][1]; stop = min(x[3] for x in b[i - 9:i + 1]); r = e - stop
        if r <= 0: i += 1; continue
        tgt = e + 2 * r; x = None; j = i + 1
        while j < min(i + 21, n):
            if b[j][1] <= stop and j > i + 1: x = b[j][1]; break
            if b[j][3] <= stop: x = stop; break
            if b[j][2] >= tgt: x = tgt; break
            j += 1
        if x is None: j = min(j, n - 1); x = b[j][4]
        nights = (b[j][0] - b[i + 1][0]).days
        tr.append((b[i + 1][0], (x - e - cost * e - e * 0.0003 * nights) / r)); i = j + 1
    return tr


if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "all"
    if what in ("all", "ea"):
        import rajan_jade as rj
        print("== EARLY ADOPTER (5-min, pivots)")
        for m, f, cost in (("NAS100 2020-23", "NAS100_2020_2023/nas100_m5_2020_2023.csv", 1.5), ("NAS100 2023-26", "NAS100/nas100_m5.csv", 1.5),
                           ("US500 2023-26", "US500/us500_m5.csv", 0.6), ("US30 2023-26", "US30/us30_m5.csv", 2.5)):
            b = rj.load(f)
            summ(f"{m} longs", early_adopter(b, cost, 1)); summ(f"{m} shorts", early_adopter(b, cost, -1))
    if what in ("all", "sw"):
        import first_red_day as frd
        print("== SWING (Darren Winters), 45 US stocks daily")
        L = []; S = []
        for f in sorted(glob.glob(f"{SP}/ep/*.json")):
            d = frd.load(f); L += swing(d, 0.0015); S += swing(inv(d), 0.0015)
        summ("longs", L); summ("shorts", S); summ("both", L + S)
