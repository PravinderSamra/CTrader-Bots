"""
Measure the sequencing failure rate for arm A at M5 resolution, on a large
sample, using the NAS100 M5 file already in the repo (3 years, 212k bars).

DAILY method  : entry at PDL*(1+cushion); stop = the SESSION low; walk forward
                on daily bars. This is what stages 1-3 did, and it silently
                assumes the session low came BEFORE the reclaim.
INTRADAY method: walk the session bar by bar. Find the first M5 bar whose low
                breaches the PDL; then the first LATER bar whose high reaches
                entry -> that is the fill. stop = lowest low SEEN SO FAR (the
                real breach low). Then continue through the rest of that
                session, and subsequent sessions, checking stop before target.

The gap between the two is the sequencing bias.
"""
import csv, bisect, statistics as st

SRC = "US30 London Range Breakout/data/NAS100/nas100_m5.csv"
CUSHION, TARGET, MAXDAYS = 0.0014, 3.0, 10

bars = []
with open(SRC) as f:
    for r in csv.reader(f):
        if r[0] == "timestamp_ms":
            continue
        bars.append((int(r[0]), float(r[2]), float(r[3]), float(r[4]), float(r[5])))
bars.sort()
print("M5 bars: %d" % len(bars))

# session buckets: broker day rolls at 21:00/22:00 UTC. Start a new session at
# the first bar whose gap from the previous bar is >= 60 min (the daily break).
sess, cur = [], [bars[0]]
for prev, b in zip(bars, bars[1:]):
    if b[0] - prev[0] >= 3600_000:
        sess.append(cur); cur = []
    cur.append(b)
sess.append(cur)
sess = [s for s in sess if len(s) >= 50]          # drop stubs / half days
print("sessions: %d" % len(sess))

def ohlc(s):
    return s[0][1], max(b[2] for b in s), min(b[3] for b in s), s[-1][4]

D = [ohlc(s) for s in sess]

def fwd(i, entry, stop, start_bar=None):
    """Walk to the target or the stop. start_bar: continue INSIDE session i
    from that bar index (intraday method); None = start at session i+1."""
    risk = entry - stop
    if risk <= 0: return None
    tgt = entry + TARGET * risk
    if start_bar is not None:
        for b in sess[i][start_bar:]:
            if b[3] <= stop: return -1.0
            if b[2] >= tgt:  return TARGET
    for n in range(1, MAXDAYS + 1):
        if i + n >= len(D): return None
        _, hi, lo, _ = D[i + n]
        if lo <= stop: return -1.0
        if hi >= tgt:  return TARGET
    return (D[min(i + MAXDAYS, len(D) - 1)][3] - entry) / risk

daily, intra, rows = [], [], []
for i in range(1, len(D)):
    plo = D[i - 1][2]
    _, _, slo, scl = D[i]
    if not (slo < plo and scl > plo):              # arm A event
        continue
    entry = plo * (1 + CUSHION)
    if entry - slo <= 0: continue

    rd = fwd(i, entry, slo)                        # DAILY: stop = session low
    if rd is None: continue

    # INTRADAY: find breach, then fill, then the real stop
    bi = next((k for k, b in enumerate(sess[i]) if b[3] < plo), None)
    if bi is None: continue
    fi = next((k for k in range(bi + 1, len(sess[i])) if sess[i][k][2] >= entry), None)
    if fi is None: continue                        # never actually reclaimed
    stop = min(b[3] for b in sess[i][:fi + 1])
    ri = fwd(i, entry, stop, start_bar=fi + 1)
    if ri is None: continue

    daily.append(rd); intra.append(ri)
    rows.append((rd, ri, 100 * (entry - stop) / entry))

n = len(rows)
dw = sum(1 for r in rows if r[0] > 0); iw = sum(1 for r in rows if r[1] > 0)
flip = [r for r in rows if r[0] > 0 and r[1] <= 0]
print("\nevents with both methods resolvable: %d\n" % n)
print("%-22s %8s %8s %10s" % ("method", "win%", "avgR", "totalR"))
print("%-22s %7.1f%% %+8.3f %10.1f" % ("DAILY (stages 1-3)", 100*dw/n, sum(daily)/n, sum(daily)))
print("%-22s %7.1f%% %+8.3f %10.1f" % ("INTRADAY (true)",    100*iw/n, sum(intra)/n, sum(intra)))
print("\nwinners under daily: %d" % dw)
print("of those, killed by sequencing: %d  = %.1f%% of winners" % (len(flip), 100*len(flip)/dw))
print("avgR degradation: %+.3fR -> %+.3fR  (%.0f%% of the edge)"
      % (sum(daily)/n, sum(intra)/n, 100*(1 - (sum(intra)/n)/(sum(daily)/n))))
if flip:
    w = [r[2] for r in flip]; ok = [r[2] for r in rows if r[0] > 0 and r[1] > 0]
    print("\nstop width of the trades sequencing killed:  median %.3f%%  (n=%d)" % (st.median(w), len(w)))
    print("stop width of the winners that survived:    median %.3f%%  (n=%d)" % (st.median(ok), len(ok)))
