"""
Stage 1: does the VIX leg add anything to a plain previous-day-low reclaim?

Daily resolution. Pre-registered in 02-documentation/01-dylan-oneal-rules.md.

EVENT (the source's Setup A, stripped to what daily bars can see):
    ES trades below the previous day's low, and closes back above it.

ARMS, all on the SAME event population (same-day control):
    A   every event                      (the null: reclaim alone)
    B   + VIX failed to reach its PDH    (the source's "relative weakness")
    B'  + VIX DID reach its PDH          (the opposite; the honest control)

TRADE GEOMETRY (daily proxy):
    entry = that day's close   (real entry is intraday at the reclaim, so this
                                is LATER and usually WORSE - results understate)
    stop  = that day's low     (the source: "stop loss under that low")
    risk  = entry - stop
    Walk forward up to MAXDAYS sessions. Within each day the stop is checked
    BEFORE the target - the conservative convention used in 10_exit_rules.py.
    No time stop beyond MAXDAYS (Vanessa, 2026-11-16: test without one first).
"""
import csv, os, statistics as st

D = os.path.join(os.path.dirname(__file__), "..", "03-data")
MAXDAYS = 10
TARGETS = [1.0, 2.0, 3.0]


def load(name):
    out = {}
    with open(os.path.join(D, name)) as f:
        for r in csv.DictReader(f):
            out[int(r["ts"])] = tuple(float(r[k]) / 100000.0
                                      for k in ("open", "high", "low", "close"))
    return out


es, vix = load("us500_d1.csv"), load("vix_d1.csv")
days = sorted(set(es) & set(vix))
print("aligned sessions: %d  (%d ES, %d VIX)" % (len(days), len(es), len(vix)))


def walk(i, entry, stop, target):
    """-> R booked, days held. Stop checked before target within a day."""
    risk = entry - stop
    if risk <= 0:
        return None
    tgt = entry + target * risk
    for n in range(1, MAXDAYS + 1):
        if i + n >= len(days):
            break
        _, hi, lo, cl = es[days[i + n]]
        if lo <= stop:
            return -1.0, n
        if hi >= tgt:
            return target, n
    j = min(i + MAXDAYS, len(days) - 1)
    return (es[days[j]][3] - entry) / risk, j - i


events = []
for i in range(1, len(days)):
    t, p = days[i], days[i - 1]
    _, _, plo, _ = es[p]
    eo, ehi, elo, ecl = es[t]
    if not (elo < plo and ecl > plo):          # breached and reclaimed by close
        continue
    vphi = vix[p][1]
    vhi = vix[t][1]
    risk = ecl - elo
    if risk <= 0:
        continue
    events.append(dict(i=i, ts=t, entry=ecl, stop=elo, risk=risk,
                       riskpct=100.0 * risk / ecl,
                       vix_weak=vhi < vphi,
                       vix_ratio=vhi / vphi,
                       depth=100.0 * (plo - elo) / plo))

print("\nEVENTS: ES breached previous day low and closed back above it")
print("  %d in %d sessions = %.1f%% of days, ~%.0f per year"
      % (len(events), len(days), 100.0 * len(events) / len(days),
         len(events) * 252.0 / len(days)))

arms = [("A  reclaim alone (null)", events),
        ("B  + VIX weak", [e for e in events if e["vix_weak"]]),
        ("B' + VIX confirmed", [e for e in events if not e["vix_weak"]])]

for target in TARGETS:
    print("\n=== target %.0fR, stop below the day's low, max %d days ===" % (target, MAXDAYS))
    print("%-26s %5s %7s %7s %7s %8s" % ("arm", "n", "win%", "avgR", "medHold", "totalR"))
    for name, ev in arms:
        rs, hold, wins = [], [], 0
        for e in ev:
            r = walk(e["i"], e["entry"], e["stop"], target)
            if r is None:
                continue
            rr, n = r
            rs.append(rr); hold.append(n)
            if rr > 0:
                wins += 1
        if not rs:
            print("%-26s %5d  (no data)" % (name, len(ev)));  continue
        print("%-26s %5d %6.1f%% %7.2f %7.0f %8.1f"
              % (name, len(rs), 100.0 * wins / len(rs), sum(rs) / len(rs),
                 st.median(hold), sum(rs)))

print("\n=== stop size produced by this rule (the H25 question) ===")
rp = sorted(e["riskpct"] for e in events)
print("  risk from entry to stop, %% of price: median %.2f%%  p25 %.2f%%  p75 %.2f%%  max %.2f%%"
      % (st.median(rp), rp[len(rp) // 4], rp[3 * len(rp) // 4], rp[-1]))

print("\n=== how often is VIX 'weak' on these days ===")
w = sum(1 for e in events if e["vix_weak"])
print("  VIX weak %d / %d = %.0f%%   (ratio today's high / prev day high:"
      " median %.3f)" % (w, len(events), 100.0 * w / len(events),
                         st.median([e["vix_ratio"] for e in events])))

print("\n=== 1%% rule: ES up >=1%% AND VIX up >=1%% on the same day ===")
hits = []
for i in range(1, len(days)):
    t, p = days[i], days[i - 1]
    esr = 100.0 * (es[t][3] / es[p][3] - 1.0)
    vxr = 100.0 * (vix[t][3] / vix[p][3] - 1.0)
    if esr >= 1.0 and vxr >= 1.0 and i + 1 < len(days):
        hits.append(100.0 * (es[days[i + 1]][3] / es[t][3] - 1.0))
nxt = [100.0 * (es[days[i + 1]][3] / es[days[i]][3] - 1.0) for i in range(len(days) - 1)]
if hits:
    print("  n=%d   next-day ES return: mean %+.2f%%  median %+.2f%%  down %d/%d"
          % (len(hits), sum(hits) / len(hits), st.median(hits),
             sum(1 for h in hits if h < 0), len(hits)))
print("  ALL days baseline next-day: mean %+.2f%%  median %+.2f%%  down %d/%d"
      % (sum(nxt) / len(nxt), st.median(nxt), sum(1 for h in nxt if h < 0), len(nxt)))
