"""Grade ranked gamma walls (C1-C3 / P1-P3) against what price actually did.

Reports BOTH readings for every wall:
  first-touch  -- what the shipped grader says (M4/D5: 8pt tolerance, first
                  touch only, no concept of role reversal)
  settled      -- role_reversal(): once price picked a side, did the level hold
                  it, and how far did the worst poke go?

The second is what the trader actually looks at: poked through, came back,
then respected.
"""
import json, sys, datetime as dt
from pathlib import Path

# These were absolute paths under /home/user/CTrader-Bots. A scheduled session
# gets its checkout wherever add_repo puts it — which is lower-cased
# /home/user/ctrader-bots — so anything pinned to the capitalised path is
# broken everywhere except the machine it was written on. Derive from __file__.
_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))
import gex_retro as R

BARS = [{"time": dt.datetime.fromisoformat(b["t"]), "open": b["o"],
         "high": b["h"], "low": b["l"], "close": b["c"]}
        for b in json.load(open("/tmp/nas100_m5.json"))]

def _skill_research():
    """Locate 'NAS100 Daily Brief agent skill/research' from this file's position."""
    for base in _HERE.parents:
        cand = base / "NAS100 Daily Brief agent skill" / "research"
        if cand.is_dir():
            return cand
    raise SystemExit("could not locate 'NAS100 Daily Brief agent skill/research' "
                     f"above {_HERE}")


LAD = _skill_research() / "chart-ladders"


def day_bars(day, after=None):
    out = [b for b in BARS if b["time"].strftime("%Y-%m-%d") == day]
    if after:
        out = [b for b in out if b["time"] >= after]
    return out


def touched(level, bars, tol=6.0):
    return any(b["low"] - tol <= level <= b["high"] + tol for b in bars)


def first_touch(level, bars, tol=8.0, window=24):
    """The shipped grader's shape: first touch, then a fixed window."""
    for i, b in enumerate(bars):
        if b["low"] - tol <= level <= b["high"] + tol:
            w = bars[i:i + window]
            up = max(x["high"] for x in w) - level
            dn = level - min(x["low"] for x in w)
            if up > 25 and dn > 25:
                verdict = "chopped"
            elif up > 25:
                verdict = "broke UP"
            elif dn > 25:
                verdict = "broke DOWN"
            else:
                verdict = "held tight"
            return {"at": b["time"].strftime("%H:%M"), "verdict": verdict,
                    "up": round(up, 1), "dn": round(dn, 1)}
    return None


def grade(ladder_file, target_day):
    d = json.loads((LAD / ladder_file).read_text())
    born = dt.datetime.fromisoformat(d["generated_utc"])
    same_day = born.strftime("%Y-%m-%d") == target_day
    bars = day_bars(target_day, after=born if same_day else None)
    rows = []
    for grp in ("ranked_positive", "ranked_negative"):
        for r in d.get(grp, []):
            lv = r["price"]
            t = touched(lv, bars)
            rows.append({
                "rank": r["rank"], "price": lv, "net": r["net_$bn"], "oi": r["oi"],
                "touched": t,
                "first": first_touch(lv, bars) if t else None,
                "settled": R.role_reversal(lv, bars) if t else None,
            })
    return {"ladder": ladder_file, "born": d["generated_utc"], "spot": d["spot"],
            "flip": d["flip"], "target": target_day,
            "bars": len(bars),
            "day_hi": max(b["high"] for b in bars) if bars else None,
            "day_lo": min(b["low"] for b in bars) if bars else None,
            "rows": rows}


PAIRS = [
    # 2026-08-26-2212 EXCLUDED: pre_fix (45-day book, never delivered) -- H11 withdrawal
    ("2026-08-27-1358.json", "2026-08-27"),   # last corrected ladder of that morning
    ("2026-08-27-2233.json", "2026-08-28"),
    ("2026-09-08-1539.json", "2026-09-09"),
]

for f, day in PAIRS:
    g = grade(f, day)
    print("=" * 78)
    print(f"{g['ladder']}  born {g['born'][:16]}  spot {g['spot']}  flip {g['flip']}")
    print(f"  -> graded against {g['target']}  ({g['bars']} bars, "
          f"hi {g['day_hi']} lo {g['day_lo']})")
    for r in g["rows"]:
        if not r["touched"]:
            print(f"  {r['rank']} {r['price']:>9.1f}  net {r['net']:+.3f}  "
                  f"oi {r['oi']:>6}  UNTOUCHED")
            continue
        ft = r["first"]; st = r["settled"]
        ftxt = f"{ft['verdict']:<11} (up {ft['up']:+.0f} dn {ft['dn']:+.0f} @{ft['at']})" if ft else "-"
        if st:
            stxt = (f"settled {st['settled_side']} from {st['settled_from']}, "
                    f"{st['minutes_held']}min, {st['touches_after']} re-tests, "
                    f"worst {st['worst_excursion']:+.1f} -> "
                    f"{'HELD as ' + st['acted_as'] if st['held'] else 'LOST'}")
        else:
            stxt = "no settled read (too few bars after)"
        print(f"  {r['rank']} {r['price']:>9.1f}  net {r['net']:+.3f}  oi {r['oi']:>6}")
        print(f"        first-touch: {ftxt}")
        print(f"        settled    : {stxt}")
    print()
