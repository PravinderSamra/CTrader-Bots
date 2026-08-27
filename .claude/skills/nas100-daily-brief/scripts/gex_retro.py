#!/usr/bin/env python3
"""
gex_retro.py — take the levels a PAST scan published, and draw what price
actually did to them.

The level board is a forecast: "mark these, expect a reaction here." Until now
that forecast was graded as a list of verdicts in the review. This draws it,
which is the only way to see whether a level was respected in the way that
matters — held on the first touch, or only after price had already sliced it.

    python3 gex_retro.py                          # yesterday's last scan vs today
    python3 gex_retro.py --from 2026-08-25 --to 2026-08-26
    python3 gex_retro.py --from 2026-08-25 --scan 1304 --out /tmp/retro.svg

Grading is review_day.grade_level, unchanged — the same rule the written
review uses, so the picture and the text can never disagree.
"""
import json, os, sys
from datetime import datetime, timezone, timedelta

import journal, review_day as R, levels_fuel as lf, ctrader_http as ct

BG, PANEL, GRID = "#0d1117", "#161b22", "#2a3038"
TEXT, DIM = "#e6edf3", "#8b949e"
PATH = "#58a6ff"
OUT_COL = {
    "respected": "#3fb950",     # stalled / rejected — the level did its job
    "broke": "#f85149",         # price went through
    "chopped": "#d29922",       # traded both sides
    "untouched": "#484f58",     # never reached
}
OUT_LABEL = {"respected": "HELD", "broke": "BROKE", "chopped": "CHOP",
             "untouched": "not reached"}


def _esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def classify(reaction):
    if not reaction or reaction == "never reached":
        return "untouched"
    if "stalled" in reaction:
        return "respected"
    if "chopped" in reaction:
        return "chopped"
    return "broke"


def pick_scan(day, want=None, root=None):
    scans = journal.load_day(day, root or journal.JOURNAL_ROOT)
    if not scans:
        return None
    scans.sort(key=lambda s: s["scan_utc"])
    if want:
        for s in scans:
            if s["scan_utc"][11:16].replace(":", "") == want:
                return s
    return scans[-1]


def session_bars(day, period="M_5"):
    """Bars belonging to one trading day, using the project's 21:00 UTC roll."""
    bars = ct.fetch_ohlcv_paged("NAS100", period, days=6)
    want = datetime.strptime(day, "%Y-%m-%d").date()
    return [b for b in bars if lf.trading_day(b["time"]) == want]


def build(src_day, tgt_day, scan_time=None, gamma_only=False):
    scan = pick_scan(src_day, scan_time)
    if not scan:
        raise SystemExit(f"no journal scans for {src_day}")
    bars = session_bars(tgt_day)
    if not bars:
        raise SystemExit(f"no bars for {tgt_day}")

    levels = (scan.get("prediction") or {}).get("levels") or []
    if gamma_only:
        levels = [l for l in levels if l.get("kind") in ("gamma", "structural",
                                                         "gamma-shelf")]
    graded = []
    for lv in levels:
        g = R.grade_level(lv, bars)
        graded.append({**lv, **g, "outcome": classify(g.get("reaction"))})
    graded.sort(key=lambda l: -l["price"])

    lo = min(b["low"] for b in bars)
    hi = max(b["high"] for b in bars)
    return {
        "src_day": src_day, "tgt_day": tgt_day,
        "scan_utc": scan["scan_utc"], "scan_session": scan.get("session_window"),
        "scan_price": (scan.get("prediction") or {}).get("price_at_scan"),
        "bars": bars, "levels": graded,
        "day_low": lo, "day_high": hi,
        "open": bars[0]["open"], "close": bars[-1]["close"],
        "gamma_only": gamma_only,
    }


def build_from_ladder(ladder_path, tgt_day, top=None):
    """Grade a PERSISTED CHART's ranked walls against a later session.

    This is the test of the chart itself — the C1-C3 / P1-P3 ranking — rather
    than of the brief's level board. They are different objects: the board is a
    curated mix of liquidity and gamma levels filtered by the range budget; the
    ladder is every strike bin ranked purely by gamma force.

    Only possible for charts drawn after 2026-08-26, because CBOE serves a live
    snapshot and nothing before that was saved.
    """
    import json as _json
    d = _json.load(open(ladder_path))
    bars = session_bars(tgt_day)
    if not bars:
        raise SystemExit(f"no bars for {tgt_day}")
    # Grade only what happened AFTER the ladder existed.
    #
    # session_bars returns the whole trading day from 21:00 the previous
    # evening. For a ladder published mid-session that means grading it against
    # price action that predates it — pure look-ahead. It did not bite on the
    # first test (a prior-evening ladder against a whole next day) which is
    # exactly why it survived.
    born = datetime.fromisoformat(d["generated_utc"])
    after = [b for b in bars if b["time"] >= born]
    clipped = len(bars) - len(after)
    if len(after) < 12:
        raise SystemExit(
            f"only {len(after)} bars after the ladder was published "
            f"({d['generated_utc']}) — too little forward data to grade")
    bars = after
    picks = []
    for x in d.get("ranked_positive", []) + d.get("ranked_negative", []):
        picks.append({"price": x["price"],
                      "name": f'{x["rank"]} {x["net_$bn"]:+.2f}bn ({x["oi"]:,} OI)',
                      "kind": "gamma", "rank": x["rank"]})
    for key, lab in (("call_resistance", "CALL RESISTANCE"),
                     ("put_support", "PUT SUPPORT")):
        if d.get(key) and not any(abs(p["price"] - d[key]) < 1 for p in picks):
            picks.append({"price": d[key], "name": lab, "kind": "gamma",
                          "rank": lab.split()[0][0]})
    if d.get("flip"):
        picks.append({"price": d["flip"], "name": "GAMMA FLIP", "kind": "gamma",
                      "rank": "F"})
    graded = []
    for lv in picks:
        g = R.grade_level(lv, bars)
        rr = role_reversal(lv["price"], bars)
        graded.append({**lv, **g, "outcome": classify(g.get("reaction")),
                       "role": rr})
    graded.sort(key=lambda l: -l["price"])
    return {
        "src_day": d["generated_utc"][:10], "tgt_day": tgt_day,
        "scan_utc": d["generated_utc"], "scan_session": "CHART LADDER",
        "scan_price": d["spot"], "bars": bars, "levels": graded,
        "day_low": min(b["low"] for b in bars),
        "day_high": max(b["high"] for b in bars),
        "open": bars[0]["open"], "close": bars[-1]["close"],
        "gamma_only": True, "from_ladder": os.path.basename(ladder_path),
        "bars_before_ladder_clipped": clipped,
    }


def latest_ladder(before_day=None):
    import glob as _glob
    root = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "..", "..", "..", "..")
    hits = []
    for base, _d, _f in os.walk(os.path.abspath(root)):
        if base.endswith(os.path.join("research", "chart-ladders")):
            hits = sorted(_glob.glob(os.path.join(base, "*.json")))
    if before_day:
        hits = [h for h in hits if os.path.basename(h)[:10] < before_day]
    # Refuse pre-fix ladders outright.
    #
    # Files written before 2026-08-27 carry `book: None` (the 45-day book) and
    # predate the wall-dominance fix. Grading one measures the version with the
    # bugs in it, and doing exactly that produced a withdrawn H11 observation.
    import json as _j
    ok = []
    for h in hits:
        try:
            j = _j.load(open(h))
            if j.get("book") == "week" and not j.get("pre_fix"):
                ok.append(h)
        except Exception:
            continue
    return ok[-1] if ok else None


def role_reversal(level, bars, tol=25.0):
    """Did the level hold AFTER price settled on one side of it?

    `grade_level` scores the FIRST touch and a window of bars after it. On a
    news-driven open the first touch is the worst possible sample: it grades
    the noise and ignores everything that follows.

    It also has no concept of ROLE REVERSAL. A call wall that caps price, gets
    reclaimed, and then acts as support is a level doing its job well — the
    first-touch rule calls that "chopped". And "broke UP through it" is scored
    as a failure even when the level sits below price and is simply never
    revisited, which for a call wall in a rally is normal.

    On 2026-08-27 the trader read C1 29,464 as: swept once, reclaimed, then
    support for the rest of the day, never broken again. The tool graded it
    CHOP. The trader was right. This measures what he actually looked at.
    """
    if not bars:
        return None
    # A level price never went near cannot have "held" anything. Without this
    # a strike 650pts below spot scored as SUPPORT with a +651.6 excursion,
    # because the minimum low was trivially above it. Untested is not passed.
    if not any(b["low"] - 6 <= level <= b["high"] + 6 for b in bars):
        return None
    last_far = None
    side_above = bars[-1]["close"] >= level
    for b in bars:
        if (b["close"] < level) if side_above else (b["close"] > level):
            last_far = b["time"]
    after = [b for b in bars if last_far is None or b["time"] > last_far]
    if len(after) < 6:
        return None
    touches = [b for b in after if b["low"] - 6 <= level <= b["high"] + 6]
    if side_above:
        worst = min(b["low"] for b in after)
        held = worst >= level - tol
        excursion = worst - level
    else:
        worst = max(b["high"] for b in after)
        held = worst <= level + tol
        excursion = worst - level
    return {
        "settled_side": "above" if side_above else "below",
        "settled_from": last_far.strftime("%H:%M") if last_far else "open",
        "minutes_held": len(after) * 5,
        "touches_after": len(touches),
        "worst_excursion": round(excursion, 1),
        "held": held,
        "acted_as": ("support" if side_above else "resistance") if held else "lost",
    }


def score(d):
    lv = d["levels"]
    reached = [l for l in lv if l["outcome"] != "untouched"]
    c = {k: sum(1 for l in lv if l["outcome"] == k) for k in OUT_COL}
    return {
        "published": len(lv), "reached": len(reached),
        **c,
        "held_rate_of_reached": (round(c["respected"] / len(reached) * 100, 1)
                                 if reached else None),
        "decisive_rate": (round((c["respected"] + c["broke"]) / len(reached) * 100, 1)
                          if reached else None),
    }


def render(d, path):
    bars, levels = d["bars"], d["levels"]
    s = score(d)

    L, R_, TOP, BOT = 96, 372, 176, 108
    PLOT_W, PLOT_H = 880, 620
    W, H = L + PLOT_W + R_, TOP + PLOT_H + BOT

    pad = (d["day_high"] - d["day_low"]) * 0.06 or 30
    ymin = min(d["day_low"], min(l["price"] for l in levels) if levels else d["day_low"]) - pad
    ymax = max(d["day_high"], max(l["price"] for l in levels) if levels else d["day_high"]) + pad
    # keep the price path readable: don't let one far-away level squash it
    span = d["day_high"] - d["day_low"]
    ymin = max(ymin, d["day_low"] - span * 1.1)
    ymax = min(ymax, d["day_high"] + span * 1.1)

    def y(p):
        return TOP + PLOT_H - (p - ymin) / (ymax - ymin) * PLOT_H

    def x(i):
        return L + i / max(1, len(bars) - 1) * PLOT_W

    o = []
    A = o.append
    A(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" '
      f'height="{H}" font-family="Segoe UI,Helvetica,Arial,sans-serif">')
    A(f'<rect width="{W}" height="{H}" fill="{BG}"/>')
    A(f'<rect x="{L}" y="{TOP}" width="{PLOT_W}" height="{PLOT_H}" fill="{PANEL}" rx="6"/>')

    A(f'<text x="28" y="46" fill="{TEXT}" font-size="29" font-weight="700">'
      f'Retrospective — levels of {d["scan_utc"][:10]} vs {d["tgt_day"]} price</text>')
    A(f'<text x="28" y="74" fill="{DIM}" font-size="16">'
      f'Levels published {_esc(d["scan_utc"][:16].replace("T"," "))}Z '
      f'({_esc(d["scan_session"] or "")}) at spot '
      f'<tspan fill="{TEXT}">{d["scan_price"]:,.0f}</tspan> &#183; '
      f'{d["tgt_day"]} ran {d["day_low"]:,.0f}&#8211;{d["day_high"]:,.0f}, '
      f'closed <tspan fill="{TEXT}">{d["close"]:,.0f}</tspan></text>')
    A(f'<text x="28" y="102" fill="{TEXT}" font-size="17" font-weight="600">'
      f'{s["reached"]} of {s["published"]} levels reached &#183; '
      f'<tspan fill="{OUT_COL["respected"]}">{s["respected"]} held</tspan> &#183; '
      f'<tspan fill="{OUT_COL["broke"]}">{s["broke"]} broke</tspan> &#183; '
      f'<tspan fill="{OUT_COL["chopped"]}">{s["chopped"]} chopped</tspan> &#183; '
      f'<tspan fill="{DIM}">{s["untouched"]} never reached</tspan></text>')
    # Fixed grid. The first version measured its own label widths to advance
    # x and the estimate was short, so the items overlapped each other.
    for n, k in enumerate(("respected", "broke", "chopped", "untouched")):
        lab = {"respected": "HELD — stalled or rejected",
               "broke": "BROKE — went through",
               "chopped": "CHOP — traded both sides",
               "untouched": "never reached"}[k]
        cx = 28 + n * 300
        A(f'<rect x="{cx}" y="120" width="13" height="13" fill="{OUT_COL[k]}" rx="3"/>')
        A(f'<text x="{cx+19}" y="131" fill="{DIM}" font-size="14">{_esc(lab)}</text>')

    # y grid
    steps = 6
    for n in range(steps + 1):
        p = ymin + (ymax - ymin) * n / steps
        yy = y(p)
        A(f'<line x1="{L}" y1="{yy:.1f}" x2="{L+PLOT_W}" y2="{yy:.1f}" '
          f'stroke="{GRID}" stroke-width="0.6"/>')
        A(f'<text x="{L-12}" y="{yy+5:.1f}" fill="{DIM}" font-size="14" '
          f'text-anchor="end">{p:,.0f}</text>')

    # hour ticks
    last_h = None
    for i, b in enumerate(bars):
        if b["time"].hour != last_h:
            last_h = b["time"].hour
            A(f'<line x1="{x(i):.1f}" y1="{TOP}" x2="{x(i):.1f}" y2="{TOP+PLOT_H}" '
              f'stroke="{GRID}" stroke-width="0.6"/>')
            A(f'<text x="{x(i):.1f}" y="{TOP+PLOT_H+22}" fill="{DIM}" font-size="13" '
              f'text-anchor="middle">{b["time"].strftime("%H:%M")}</text>')

    # level lines — drawn UNDER the price path so the path stays readable
    used = []
    for l in levels:
        if not (ymin <= l["price"] <= ymax):
            continue
        col = OUT_COL[l["outcome"]]
        yy = y(l["price"])
        dash = "none" if l["outcome"] == "respected" else ("3,4" if l["outcome"] == "untouched" else "8,5")
        op = "0.45" if l["outcome"] == "untouched" else "0.95"
        A(f'<line x1="{L}" y1="{yy:.1f}" x2="{L+PLOT_W}" y2="{yy:.1f}" stroke="{col}" '
          f'stroke-width="2" stroke-dasharray="{dash}" opacity="{op}"/>')
        # mark the touch
        if l.get("bar_index") is not None and l["outcome"] != "untouched":
            A(f'<circle cx="{x(l["bar_index"]):.1f}" cy="{yy:.1f}" r="5.5" '
              f'fill="{col}" stroke="{BG}" stroke-width="2"/>')
        ly = yy
        while any(abs(ly - u) < 19 for u in used):
            ly += 19
        used.append(ly)
        # The verdict occupies its own right-aligned column, so the name must
        # be clipped to fit BEFORE it. At 34 chars "STRUCTURAL CALL WALL
        # ●●●●● 1.66bn" printed straight through "BROKE".
        name = l["name"]
        if len(name) > 21:
            name = name[:20] + "…"
        A(f'<text x="{L+PLOT_W+12}" y="{ly+5:.1f}" fill="{col}" font-size="14" '
          f'font-weight="600">{l["price"]:,.0f}</text>')
        A(f'<text x="{L+PLOT_W+74}" y="{ly+5:.1f}" fill="{TEXT}" font-size="13">'
          f'{_esc(name)}</text>')
        A(f'<text x="{W-14}" y="{ly+5:.1f}" fill="{col}" font-size="12" '
          f'text-anchor="end" font-weight="700">{OUT_LABEL[l["outcome"]]}</text>')

    # price path on top
    pts = " ".join(f'{x(i):.1f},{y(b["close"]):.1f}' for i, b in enumerate(bars))
    A(f'<polyline points="{pts}" fill="none" stroke="{PATH}" stroke-width="2.4" '
      f'stroke-linejoin="round"/>')
    A(f'<circle cx="{x(0):.1f}" cy="{y(bars[0]["open"]):.1f}" r="5" fill="{PATH}"/>')
    A(f'<circle cx="{x(len(bars)-1):.1f}" cy="{y(bars[-1]["close"]):.1f}" r="5" '
      f'fill="#fff" stroke="{PATH}" stroke-width="2"/>')

    fy = H - 66
    hr = s["held_rate_of_reached"]
    for n, line in enumerate([
        f'Of the levels price actually reached, {hr}% held (stalled or rejected) '
        f'and {s["decisive_rate"]}% produced a decisive reaction either way.',
        'A level is HELD when price stalled there without a clean break in either '
        'direction; BROKE when it went through; CHOP when it traded both sides.',
        'Grading is review_day.grade_level, the same rule the written review uses. '
        'Dots mark first touch. Levels are from the source scan and were never '
        'updated intraday.']):
        A(f'<text x="28" y="{fy+n*20}" fill="{DIM}" font-size="13">{_esc(line)}</text>')
    A('</svg>')
    open(path, "w").write("\n".join(o))
    return path


def main():
    a = sys.argv
    def opt(flag, default=None):
        return a[a.index(flag) + 1] if flag in a else default
    tgt = opt("--to")
    src = opt("--from")
    if not tgt:
        tgt = str(lf.trading_day(datetime.now(timezone.utc)))
    if not src:
        root = journal.JOURNAL_ROOT
        days = sorted(x for x in os.listdir(root)
                      if os.path.isdir(os.path.join(root, x)) and x < tgt)
        if not days:
            raise SystemExit("no earlier journal day to draw from")
        src = days[-1]
    out = opt("--out", f"/tmp/NAS100-retro-{src}-vs-{tgt}.svg")
    if "--ladder" in a:
        lp = opt("--ladder")
        if lp in (None, "auto"):
            lp = latest_ladder(before_day=tgt)
            if not lp:
                raise SystemExit(
                    "no persisted chart ladder earlier than %s. Ladders are "
                    "saved from 2026-08-26 onward; CBOE has no historical "
                    "chain, so charts before that cannot be rebuilt." % tgt)
        d = build_from_ladder(lp, tgt)
        out = opt("--out", f"/tmp/NAS100-retro-ladder-vs-{tgt}.svg")
    else:
        d = build(src, tgt, scan_time=opt("--scan"),
                  gamma_only=("--gamma-only" in a))
    s = score(d)
    print(f"RETRO  {src} levels  vs  {tgt} price")
    print(f"  scan {d['scan_utc'][:16].replace('T',' ')}Z ({d['scan_session']}) "
          f"@ {d['scan_price']:,.1f}")
    print(f"  {tgt}: {d['open']:,.1f} -> {d['close']:,.1f}  "
          f"range {d['day_low']:,.1f}-{d['day_high']:,.1f}")
    print(f"  {s['reached']}/{s['published']} reached · {s['respected']} held · "
          f"{s['broke']} broke · {s['chopped']} chopped · "
          f"{s['untouched']} never reached")
    if s["held_rate_of_reached"] is not None:
        print(f"  held rate (of reached) {s['held_rate_of_reached']}% · "
              f"decisive {s['decisive_rate']}%")
    print()
    for l in d["levels"]:
        rr = l.get("role")
        extra = ""
        if rr:
            extra = (f"   [settled {rr['settled_side']} from {rr['settled_from']}, "
                     f"{rr['minutes_held']}min, worst {rr['worst_excursion']:+.1f} "
                     f"-> {rr['acted_as'].upper()}]")
        print(f"  {l['price']:>10,.1f}  {OUT_LABEL[l['outcome']]:<12} "
              f"{l['name'][:34]}{extra}")
    print(f"\n  {render(d, out)}")


if __name__ == "__main__":
    main()
