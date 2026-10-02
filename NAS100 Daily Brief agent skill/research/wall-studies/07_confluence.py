"""Does CONFLUENCE at a level raise the hit rate of the sweep -> LH/HL setup?

Every prior analysis graded a level in isolation. This asks a different
question: when two DIFFERENT KINDS of level sit on top of each other, is the
reversal better?

Families, deliberately coarse:
    gamma     call/put wall, gamma flip, options shelf, max pain
    pool      equal highs / equal lows
    session   Asia / London / NY high-low
    day/week  PDH, PDL, PWH, PWL, PD mid, PD close

"structure" is any non-gamma family. A setup is labelled by the families
present within CONF_TOL points of the swept level, among the levels the brief
actually published that day.

NOTE ON THE FIRST ATTEMPT: an earlier version labelled by len(families) > 1,
which called "PDH + London High" a gamma+structure confluence when it contains
no gamma at all. Families are now tested explicitly.

INDEPENDENCE: the row count is not the sample size. One level swept six times
in a day is six rows but one observation of the level. Distinct (day, level)
pairs are reported alongside, and a bucket with few distinct pairs proves
nothing however many rows it carries.
"""
import json, glob, statistics as st, collections

CONF_TOL = 12.0        # pts; same order as the equal-highs cluster tolerance

FAM = {
    "gamma wall": "gamma", "gamma flip": "gamma",
    "options shelf": "gamma", "max pain": "gamma",
    "equal highs/lows": "pool",
    "Asia H/L": "session", "London H/L": "session", "NY H/L": "session",
    "prev-day H/L": "day/week", "prev-week H/L": "day/week",
    "PD mid/close": "day/week",
}


def classify(name):
    n = name.upper()
    if "CALL WALL" in n or "PUT WALL" in n:  return "gamma wall"
    if "GAMMA FLIP" in n:                    return "gamma flip"
    if "SHELF" in n:                         return "options shelf"
    if "MAX PAIN" in n:                      return "max pain"
    if "PDH" in n or "PDL" in n:             return "prev-day H/L"
    if "PWH" in n or "PWL" in n:             return "prev-week H/L"
    if "EQUAL" in n:                         return "equal highs/lows"
    if "ASIA" in n:                          return "Asia H/L"
    if "LONDON" in n:                        return "London H/L"
    if "NY" in n:                            return "NY H/L"
    if "PD MID" in n or "PD CLOSE" in n:     return "PD mid/close"
    return "other"


def levels_for(day):
    out = {}
    for f in sorted(glob.glob(f"NAS100 Daily Brief agent skill/journal/{day}/*.json")):
        j = json.load(open(f))
        if j.get("test_artefact") or not j.get("is_trading_day"):
            continue
        for l in j["prediction"].get("levels", []):
            if "STRUCTURAL" in l["name"]:
                continue
            out.setdefault(round(l["price"], 1), l["name"])
    return out


def label(fams):
    """fams is a set of family names. Exclusive, exhaustive labelling."""
    non_gamma = fams - {"gamma"}
    if "gamma" in fams and non_gamma:
        return "gamma + structure"
    if "gamma" in fams:
        return "gamma alone"
    if len(non_gamma) > 1:
        return "structure + structure"
    if non_gamma == {"pool"}:
        return "pool alone"
    if non_gamma == {"session"}:
        return "session alone"
    if non_gamma == {"day/week"}:
        return "day/week alone"
    return "other"


def summarise(rows, tag):
    if not rows:
        return None
    n = len(rows)
    pairs = len({(r["day"], r["level"]) for r in rows})
    days = len({r["day"] for r in rows})
    r1 = sum(1 for r in rows if r["R"] >= 1) / n
    r2 = sum(1 for r in rows if r["R"] >= 2) / n
    stp = sum(1 for r in rows if r["stopped"]) / n
    medR = st.median(r["R"] for r in rows)
    medmv = st.median(r["R"] * r["risk"] for r in rows)
    return (tag, n, pairs, days, r1, r2, stp, medR, medmv)


def bucket(rows, tol, cache):
    """-> {label: [rows]}, each row tagged with the families near its level."""
    out = collections.defaultdict(list)
    for r in rows:
        d = r["day"]
        if d not in cache:
            cache[d] = levels_for(d)
        near = [nm for p, nm in cache[d].items() if abs(p - r["level"]) <= tol]
        fams = {FAM.get(classify(nm)) for nm in near}
        fams.discard(None)
        r["_fams"], r["_names"] = fams, near
        out[label(fams)].append(r)
    return out


def line(tag, v):
    m = len(v)
    return (f"  {tag:<24}{m:>5} rows{len({(r['day'], r['level']) for r in v}):>5} pairs"
            f"{len({r['day'] for r in v}):>4}d"
            f"  >=1R {sum(1 for r in v if r['R'] >= 1) / m:>4.0%}"
            f"  >=2R {sum(1 for r in v if r['R'] >= 2) / m:>4.0%}"
            f"  stop {sum(1 for r in v if r['stopped']) / m:>4.0%}"
            f"  medR {st.median(r['R'] for r in v):>5.2f}"
            f"  medmv {st.median(r['R'] * r['risk'] for r in v):>4.0f}p")


def same_day_control(rows, target, buckets):
    """A bucket can only be judged against the days it actually appears on.
    Comparing it to the whole dataset credits it for the days it turned up."""
    v = buckets.get(target, [])
    if not v:
        return
    days = {r["day"] for r in v}
    other = [r for r in rows if r["day"] in days and label(r["_fams"]) != target]
    print(line(target, v))
    print(line("  other levels, same days", other))
    beat = elig = 0
    for d in sorted(days):
        a = [r for r in v if r["day"] == d]
        z = [r for r in other if r["day"] == d]
        if len(a) < 4 or not z:
            continue
        elig += 1
        beat += (sum(1 for r in a if r["R"] >= 1) / len(a)
                 > sum(1 for r in z if r["R"] >= 1) / len(z))
    print(f"    beat its own day's other levels on {beat}/{elig} days with >=4 rows")


if __name__ == "__main__":
    rows = json.load(open("/tmp/sw_conf.json"))
    cache = {}

    # A real confluence effect should not depend on how wide you draw the band.
    # One that strengthens as the band narrows to a handful of observations, or
    # fades as it widens, is a counting artefact.
    for tol in (5, CONF_TOL, 25, 40):
        b = bucket(rows, tol, cache)
        print(f"--- tol {tol:.0f}pts")
        for k in sorted(b, key=lambda k: -sum(1 for r in b[k] if r["R"] >= 1) / len(b[k])):
            print(line(k, b[k]))
        cache.clear()

    b = bucket(rows, CONF_TOL, cache)
    for target in ("structure + structure", "gamma + structure", "gamma alone"):
        print(f"\nSAME-DAY CONTROL at {CONF_TOL:.0f}pts — {target}")
        same_day_control(rows, target, b)

    print(f"\nstructure+structure, one line per distinct day/level pair")
    seen = {}
    for r in b.get("structure + structure", []):
        seen.setdefault((r["day"], r["level"]), r)
    for (d, px), r in sorted(seen.items()):
        print(f"  {d}  {px:>9.1f}  {'+'.join(sorted(r['_fams'])):<20}"
              f" {' | '.join(sorted(set(r['_names'])))}")
