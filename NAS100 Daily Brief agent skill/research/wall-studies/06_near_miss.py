"""The levels price ALMOST reached — the blind spot in every prior analysis.

Everything measured so far required price to touch a level. On 2026-10-02 the
best trade of the day came from a level price never touched: the CALL WALL at
31,046.7, missed by 9.6pts, which marked the high to the point.

A "near miss" is observable in real time, so this is a signal and not hindsight:
price makes a swing extreme inside a band BELOW the level (for a level above),
never trades through it, and turns. You know at the turn.

Compared head to head against the swept version of the same level, same grading
(closes, not wicks), same stop rule.
"""
import json, datetime as dt, collections, statistics as st, glob

STOP_BUF = 8.0
SWING = 3          # bars either side for a local extreme


def load():
    B = collections.defaultdict(list)
    for b in json.load(open("/tmp/m5_all.json")):
        t = dt.datetime.fromisoformat(b["t"])
        B[t.strftime("%Y-%m-%d")].append(
            {"t": t, "o": b["o"], "h": b["h"], "l": b["l"], "c": b["c"]})
    return B


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


def kind(name):
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
    return "other"


def run_trade(bars, i_entry, entry, stop, side):
    """side 'short' or 'long'. Close-based MFE, stop on wick. -> (R, stopped)"""
    risk = abs(entry - stop)
    if risk < 3:
        return None
    best = 0.0
    for b in bars[i_entry + 1:]:
        adverse = b["h"] if side == "short" else b["l"]
        if (adverse >= stop) if side == "short" else (adverse <= stop):
            return best / risk, True
        fav = (entry - b["c"]) if side == "short" else (b["c"] - entry)
        best = max(best, fav)
    return best / risk, False


def near_misses(bars, P, band):
    """Swing highs that land within `band` BELOW P without ever exceeding P
    (checked only up to that bar — no look-ahead), then turn."""
    out = []
    n = len(bars)
    for i in range(SWING, n - SWING):
        w = bars[i - SWING:i + SWING + 1]
        # local high
        if bars[i]["h"] != max(x["h"] for x in w):
            continue
        h = bars[i]["h"]
        if not (P - band <= h < P):
            continue
        # price must not have traded through P earlier today
        if max(x["h"] for x in bars[:i + 1]) >= P:
            continue
        out.append({"i": i + SWING, "ext": h, "entry": bars[i + SWING]["c"]})
    return out


def near_misses_low(bars, P, band):
    out = []
    n = len(bars)
    for i in range(SWING, n - SWING):
        w = bars[i - SWING:i + SWING + 1]
        if bars[i]["l"] != min(x["l"] for x in w):
            continue
        l = bars[i]["l"]
        if not (P < l <= P + band):
            continue
        if min(x["l"] for x in bars[:i + 1]) <= P:
            continue
        out.append({"i": i + SWING, "ext": l, "entry": bars[i + SWING]["c"]})
    return out


if __name__ == "__main__":
    B = load()
    rows = []
    for day in sorted(B):
        lv = levels_for(day)
        bars = B[day]
        if not lv or len(bars) < 100:
            continue
        px0 = bars[0]["c"]
        for P, name in lv.items():
            for band in (10, 20, 35):
                if P > px0:
                    for m in near_misses(bars, P, band):
                        r = run_trade(bars, m["i"], m["entry"],
                                      m["ext"] + STOP_BUF, "short")
                        if r:
                            rows.append({"day": day, "band": band, "side": "short",
                                         "kind": kind(name), "name": name,
                                         "miss": round(P - m["ext"], 1),
                                         "risk": round(abs(m["entry"] - m["ext"] - STOP_BUF), 1),
                                         "R": round(r[0], 2), "stopped": r[1]})
                else:
                    for m in near_misses_low(bars, P, band):
                        r = run_trade(bars, m["i"], m["entry"],
                                      m["ext"] - STOP_BUF, "long")
                        if r:
                            rows.append({"day": day, "band": band, "side": "long",
                                         "kind": kind(name), "name": name,
                                         "miss": round(m["ext"] - P, 1),
                                         "risk": round(abs(m["entry"] - m["ext"] + STOP_BUF), 1),
                                         "R": round(r[0], 2), "stopped": r[1]})
    json.dump(rows, open("/tmp/nearmiss.json", "w"))
    print(f"{len(rows)} near-miss setups")
