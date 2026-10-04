"""What target is realistic, given how wide the stop is?

The question behind this: "if my stop is 30pts, 1R may be a fair target; if it
is 70pts, maybe only half an R is realistic." That is a claim about whether R
is the right unit at all. If price travels roughly the same DISTANCE regardless
of how wide your stop happened to be, then a wide stop mechanically reaches a
smaller R multiple, and taking 1R on every trade is not one rule but two
different bets.

Reads /tmp/sw_conf.json (the sweep -> lower-high/higher-low setups from
05_sweep_reversal.py). Each row carries:
    risk  the stop distance in points, entry to stop
    R     the best R reached ON A CLOSE before the stop was touched
    stopped  whether the stop was hit at any point afterwards

So R * risk is the furthest price closed in favour, in points. Max favourable
excursion, not an achievable exit: there are no spreads, no slippage and no
partials anywhere in this.

OUTCOME MODEL, for a hard target T and a hard stop:
    R >= T              -> target hit before the stop        +T
    R < T and stopped   -> stopped out                       -1
    R < T, not stopped  -> ran to the end of the day, neither
                           target nor stop; scored 0, and the
                           share of these is reported, because
                           in reality they close somewhere.
Expectancy is in R per trade. Scoring the third case at 0 makes every
expectancy here slightly OPTIMISTIC for wide targets, which attract more of
them, so read the "open" column before trusting a wide-target cell.
"""
import json, statistics as st, collections, sys

BUCKETS = [(0, 25, "<=25pts"), (25, 40, "26-40"), (40, 55, "41-55"),
           (55, 75, "56-75"), (75, 100, "76-100"), (100, 1e9, ">100")]
TARGETS = [0.5, 0.75, 1.0, 1.5, 2.0, 3.0]


def load(path):
    return json.load(open(path))


def bucket_of(risk):
    for lo, hi, name in BUCKETS:
        if lo < risk <= hi:
            return name
    return None


def outcome(r, T):
    """-> ('target'|'stop'|'open', R booked)"""
    if r["R"] >= T:
        return "target", T
    if r["stopped"]:
        return "stop", -1.0
    return "open", 0.0


def table(rows, title):
    by = collections.defaultdict(list)
    for r in rows:
        b = bucket_of(r["risk"])
        if b:
            by[b].append(r)

    print(f"\n{title}")
    print(f"{'stop size':<11}{'n':>5}{'pairs':>6}" +
          "".join(f"{('P ' + (f'{t:g}') + 'R'):>8}" for t in TARGETS) +
          f"{'medR':>7}{'med pts':>9}")
    for _, _, name in BUCKETS:
        v = by.get(name)
        if not v:
            continue
        n = len(v)
        pairs = len({(r["day"], r["level"]) for r in v})
        cells = "".join(f"{sum(1 for r in v if r['R'] >= t) / n:>8.0%}" for t in TARGETS)
        print(f"{name:<11}{n:>5}{pairs:>6}{cells}"
              f"{st.median(r['R'] for r in v):>7.2f}"
              f"{st.median(r['R'] * r['risk'] for r in v):>8.0f}p")
    return by


def expectancy(by, title):
    print(f"\n{title}  (R per trade; 'open' = neither target nor stop by day end)")
    print(f"{'stop size':<11}" +
          "".join(f"{('E ' + f'{t:g}' + 'R'):>9}" for t in TARGETS) +
          f"{'best':>8}")
    for _, _, name in BUCKETS:
        v = by.get(name)
        if not v:
            continue
        es = {}
        for t in TARGETS:
            tot = sum(outcome(r, t)[1] for r in v)
            es[t] = tot / len(v)
        best = max(es, key=es.get)
        print(f"{name:<11}" + "".join(f"{es[t]:>+9.2f}" for t in TARGETS) +
              f"{f'{best:g}R':>8}")
    print(f"\n{'stop size':<11}" + "".join(f"{('open ' + f'{t:g}' + 'R'):>9}" for t in TARGETS))
    for _, _, name in BUCKETS:
        v = by.get(name)
        if not v:
            continue
        print(f"{name:<11}" + "".join(
            f"{sum(1 for r in v if outcome(r, t)[0] == 'open') / len(v):>8.0%} "
            for t in TARGETS))


def in_points(by, title):
    """The control for the whole question: does a wider stop actually buy a
    longer run, or does price travel the same distance either way?"""
    print(f"\n{title}")
    print(f"{'stop size':<11}{'n':>5}{'med stop':>10}{'med pts':>9}{'p75 pts':>9}"
          f"{'P 30p':>8}{'P 50p':>8}{'P 75p':>8}{'P 100p':>8}")
    for _, _, name in BUCKETS:
        v = by.get(name)
        if not v:
            continue
        mv = [r["R"] * r["risk"] for r in v]
        mv.sort()
        print(f"{name:<11}{len(v):>5}{st.median(r['risk'] for r in v):>9.0f}p"
              f"{st.median(mv):>8.0f}p{mv[int(len(mv) * 0.75)]:>8.0f}p" +
              "".join(f"{sum(1 for m in mv if m >= k) / len(mv):>8.0%}"
                      for k in (30, 50, 75, 100)))


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "/tmp/sw_conf.json"
    rows = load(path)
    tag = "confirmed (sweep -> LH/HL)" if "conf" in path else "plain reclaim"
    print(f"{len(rows)} setups, {len({r['day'] for r in rows})} trading days — {tag}")
    by = table(rows, f"PROBABILITY OF REACHING EACH TARGET, by stop size — {tag}")
    expectancy(by, "EXPECTANCY")
    in_points(by, "THE SAME DATA IN POINTS — does a wider stop buy a longer run?")


# --- appended: the same question asked in points rather than in R ----------
# If the realistic run is a DISTANCE, the target should be set in points and
# the R multiple should be whatever that distance divides into your stop.

PT_TARGETS = [25, 40, 55, 70, 100, 150]


def fixed_point_targets(by):
    print("\nFIXED POINT TARGETS — hit rate, and the R each one pays per bucket")
    print(f"{'stop size':<11}{'med stop':>9}" +
          "".join(f"{str(t) + 'p':>16}" for t in PT_TARGETS))
    print(f"{'':<11}{'':>9}" + "".join(f"{'hit':>8}{'E(R)':>8}" for _ in PT_TARGETS))
    for _, _, name in BUCKETS:
        v = by.get(name)
        if not v:
            continue
        med = st.median(r["risk"] for r in v)
        cells = ""
        for T in PT_TARGETS:
            hit = sum(1 for r in v if r["R"] * r["risk"] >= T) / len(v)
            e = 0.0
            for r in v:
                if r["R"] * r["risk"] >= T:
                    e += T / r["risk"]          # paid in R, which varies per trade
                elif r["stopped"]:
                    e -= 1.0
            cells += f"{hit:>7.0%}{e / len(v):>+8.2f}"
        print(f"{name:<11}{med:>8.0f}p{cells}")


if __name__ == "__main__" and "--points" in sys.argv:
    fixed_point_targets(by)
