"""Sweep -> failed re-break -> reversal, measured two ways.

v1 counted MFE off wicks, which rewards a spike nobody could exit into. v2
measures on CLOSES: a setup "reaches 1R" only if a bar CLOSES at or beyond 1R
before the stop is touched. That is the difference between a number and a fill.

v2 also tests the trader's actual refinement, which v1 ignored: after the
reclaim, does price put in a LOWER HIGH (bearish) / HIGHER LOW (bullish) before
continuing? That is the "failed to make a new HH" confirmation. It costs entry
price — you are in later and worse — so it has to earn its keep.
"""
import json, datetime as dt, collections, statistics as st, glob

TOL = 2.0
STOP_BUF = 8.0
MAX_BARS_ABOVE = 24
SWING = 2          # bars either side to call a local extreme


def load_bars():
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


def find_sweeps(bars, P, side):
    out, i, n = [], 0, len(bars)
    while i < n:
        b = bars[i]
        beyond = (b["h"] > P + TOL) if side == "up" else (b["l"] < P - TOL)
        if not beyond:
            i += 1
            continue
        j, ext = i, (b["h"] if side == "up" else b["l"])
        while j < n and j - i < MAX_BARS_ABOVE:
            bj = bars[j]
            ext = max(ext, bj["h"]) if side == "up" else min(ext, bj["l"])
            if ((bj["c"] < P) if side == "up" else (bj["c"] > P)) and j > i:
                out.append({"i_entry": j, "ext": ext, "entry": bj["c"], "t": bj["t"]})
                break
            j += 1
        i = max(j, i) + 1
    return out


def confirm_lh(bars, k, side, ext, within=12):
    """After the reclaim at index k, find the first swing high (bearish) /
    swing low (bullish). Return (index, price) if it is LOWER / HIGHER than the
    sweep extreme — the 'failed to make a new HH' confirmation."""
    w = bars[k + 1:k + 1 + within]
    for i in range(SWING, len(w) - SWING):
        if side == "up":
            piv = w[i]["h"]
            if all(w[i]["h"] >= w[i + o]["h"] for o in range(-SWING, SWING + 1)):
                return (k + 1 + i, piv) if piv < ext else None
        else:
            piv = w[i]["l"]
            if all(w[i]["l"] <= w[i + o]["l"] for o in range(-SWING, SWING + 1)):
                return (k + 1 + i, piv) if piv > ext else None
    return None


def run(bars, entry, stop, i_from, side):
    """Close-based grading. -> (max R reached on a CLOSE, stopped?)"""
    risk = abs(entry - stop)
    if risk < 3:
        return None
    best = 0.0
    for b in bars[i_from + 1:]:
        adverse = b["h"] if side == "up" else b["l"]
        if (adverse >= stop) if side == "up" else (adverse <= stop):
            return best / risk, True
        fav = (entry - b["c"]) if side == "up" else (b["c"] - entry)
        best = max(best, fav)
    return best / risk, False


if __name__ == "__main__":
    B = load_bars()
    plain, confirmed = [], []
    for day in sorted(B):
        lv = levels_for(day)
        bars = B[day]
        if not lv or len(bars) < 100:
            continue
        for P, name in lv.items():
            for side in ("up", "down"):
                for s in find_sweeps(bars, P, side):
                    stop = s["ext"] + STOP_BUF if side == "up" else s["ext"] - STOP_BUF
                    base = {"day": day, "t": s["t"].isoformat(), "level": P,
                            "name": name, "kind": classify(name), "side": side,
                            "sweep_pts": round(abs(s["ext"] - P), 1),
                            "risk": round(abs(s["entry"] - stop), 1),
                            "hour": s["t"].hour}
                    r = run(bars, s["entry"], stop, s["i_entry"], side)
                    if r:
                        plain.append({**base, "R": round(r[0], 2), "stopped": r[1]})
                    # --- with the lower-high / higher-low confirmation ---
                    c = confirm_lh(bars, s["i_entry"], side, s["ext"])
                    if c:
                        k2, piv = c
                        e2 = bars[k2]["c"]
                        r2 = run(bars, e2, stop, k2, side)
                        if r2:
                            confirmed.append({**base, "R": round(r2[0], 2),
                                              "stopped": r2[1],
                                              "risk": round(abs(e2 - stop), 1)})
    json.dump(plain, open("/tmp/sw_plain.json", "w"))
    json.dump(confirmed, open("/tmp/sw_conf.json", "w"))
    print(f"plain reclaim      : {len(plain)}")
    print(f"with LH/HL confirm : {len(confirmed)}")
