#!/usr/bin/env python3
"""
test_consistency.py — the invariants that today's bugs violated.

Every check here corresponds to a bug that actually shipped. The point is not
to prove the code works; it is to make these particular failures loud if they
ever come back, because every one of them was silent.

    python3 test_consistency.py            # live data, ~2 min
    python3 test_consistency.py --offline  # structural checks only, no network
"""
import os as _os
# The LIVE half calls gather(), which persists GEXBot ladders. Those are
# archive artefacts now (D11 put the directory in sync_archive PATHS), so a
# test run must not manufacture them. Set before brief is imported.
_os.environ["NAS100_NO_PERSIST"] = "1"

import glob, json, os, subprocess, sys
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
PASS, FAIL = [], []


def check(name, ok, detail=""):
    (PASS if ok else FAIL).append((name, detail))
    print(f"  {'PASS' if ok else 'FAIL'}  {name}" + (f"  — {detail}" if detail else ""))


def _research(sub):
    d = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
    for base, _x, _y in os.walk(d):
        if base.endswith("NAS100 Daily Brief agent skill"):
            return os.path.join(base, "research", sub)
    return None


def offline_checks():
    print("\nSTRUCTURAL (no network)")

    # D4 — walls must be side-dominated, at source
    src = open(os.path.join(HERE, "gex_levels.py")).read()
    check("gex_levels requires call dominance for the call wall",
          'cands_c = [p for p in above if p["call_gex"] > p["put_gex"]]' in src)
    check("gex_levels requires put dominance for the put wall",
          'cands_p = [p for p in below if p["put_gex"] > p["call_gex"]]' in src)

    chart = open(os.path.join(HERE, "gex_chart.py")).read()
    check("gex_chart applies the same dominance rule",
          'b["call_gex"] > b["put_gex"]' in chart and 'b["put_gex"] > b["call_gex"]' in chart)

    # book mismatch — chart must default to the brief's book
    check("chart defaults to the week book (dte<=7), matching the brief",
          'BOOKS = {"week": 7, "full": 45}' in chart and 'book="week"' in chart)

    # one build per scan
    brief = open(os.path.join(HERE, "brief.py")).read()
    check("brief.py can draw the chart from its own gather()",
          "--chart" in brief and "gex_chart.collect(d=d" in brief)

    # verification runs must not journal
    check("brief.py supports --no-journal",
          '"--no-journal" in sys.argv' in brief)

    # both graders honour test_artefact
    import review_day as R_MOD
    rv = open(os.path.join(HERE, "review_day.py")).read()
    tr = open(os.path.join(HERE, "track.py")).read()
    check("review_day excludes test_artefact entries", 'test_artefact' in rv)
    check("track excludes test_artefact entries", 'test_artefact' in tr)

    # D3 — day completeness by clock, not bar count
    check("track grades a day only after it has ended",
          "_day_complete" in tr and "hour=21" in tr)
    check("track reports held-back days out loud", "HELD BACK" in tr)
    check("track reports H1 per day as well as per scan",
          "mean_error_per_day" in tr)

    # ladder retro guards
    rt = open(os.path.join(HERE, "gex_retro.py")).read()
    check("ladder retro clips bars to after the ladder was published",
          'b["time"] >= born' in rt)
    check("ladder auto-pick refuses pre-fix (non-week) ladders",
          '.get("book") == "week"' in rt)
    # Behavioural, not a grep: the guard moved to review_day when the settled
    # read became the official verdict, and a source-text assertion silently
    # passed on the wrong file. Exercise it instead.
    import datetime as _dt
    import gex_retro as _GR
    _t0 = _dt.datetime(2026, 9, 9, 13, 0, tzinfo=_dt.timezone.utc)
    _bars = [{"time": _t0 + _dt.timedelta(minutes=5 * i), "open": 29500.0,
              "high": 29510.0, "low": 29490.0, "close": 29500.0}
             for i in range(40)]
    check("role_reversal returns None for a level price never reached",
          _GR.role_reversal(28850.0, _bars) is None)
    check("role_reversal still reads a level price did reach",
          (_GR.role_reversal(29495.0, _bars) or {}).get("held") is True)

    # H7: the flip must not vote when the brief refuses to quote it. These two
    # suppressions were shipped a commit apart and the gap was worth -5 points
    # on a live build, so the invariant is that they move TOGETHER.
    import bias_engine as _BE

    # Minimal REAL payload rather than a magic auto-dict: if bias_engine grows
    # a new required field this test should fail loudly, not silently pass.
    _lv = {"price": 29400.0,
           "fuel": {"adr_used_pct": 50.0, "adr14": 300.0,
                    "expansion_state": "MODERATE"},
           "levels": {}}
    _gx = {"gamma_flip": {"nas100": 29500.0},
           "buckets": {"this_week": {"net_gex_$bn_per_1pct": 0.5,
                                     "call_wall": {"nas100": 29600.0},
                                     "put_wall": {"nas100": 29200.0}}}}
    _mc = {"volatility": {"vxn_nasdaq_ivol": {}, "vix": {}, "vvix": {}},
           "rates_fx": {"us10y": {}, "us5y": {}, "dxy": {}},
           "breadth_proxy": {}, "index": {"ndx_daily": {}, "es_daily": {}},
           "calendar": {}, "fred": {}}

    def _gamma_pts(sess):
        try:
            r = _BE.score(_mc, _lv, _gx, session=sess)
        except Exception:
            return None
        return sum(c["points"] for c in r["components"]
                   if c["component"] == "gamma" and "flip" in c["why"])

    _on, _off = _gamma_pts("OVERNIGHT"), _gamma_pts("PRE_NY")
    check("flip-derived gamma votes are withheld overnight", _on == 0)
    check("flip-derived gamma votes still count in session", (_off or 0) != 0)
    check("non-flip gamma votes survive the overnight suppression",
          any(c["component"] == "gamma" and "flip" not in c["why"]
              for c in _BE.score(_mc, _lv, _gx, session="OVERNIGHT")["components"]))

    # the settled read is the official verdict, first-touch kept for comparison
    _g = R_MOD.grade_level({"price": 29495.0, "name": "T"}, _bars)
    check("grade_level verdict comes from the settled read",
          "held as" in _g.get("reaction", ""))
    check("grade_level still reports the superseded first-touch verdict",
          "first_touch_reaction" in _g)
    check("a touched-but-unsettled level is not counted as a break",
          _GR.classify("touched, no settled read (too few bars on one side)")
          == "unsettled")

    # the single grading rule
    check("track and gex_retro both import review_day (one grader)",
          "import journal, review_day as R" in tr and "review_day as R" in rt)

    # persisted ladders must record their book
    lad = _research("chart-ladders")
    if lad and os.path.isdir(lad):
        files = sorted(glob.glob(os.path.join(lad, "*.json")))
        recent = [f for f in files if os.path.basename(f)[:10] >= "2026-08-27"]
        bad = []
        for f in recent:
            j = json.load(open(f))
            if j.get("book") != "week" and not j.get("pre_fix"):
                bad.append(os.path.basename(f))
        check("every ladder records book=week or is marked pre_fix",
              not bad, f"offenders: {bad}" if bad else f"{len(recent)} checked")


def live_checks():
    print("\nLIVE (one build, compared against itself)")
    sys.path.insert(0, HERE)
    import brief as B, gex_chart as GC

    d = B.gather()
    if "error" in d:
        check("gather() succeeded", False, str(d.get("detail"))[:120]); return
    c = GC.collect(d=d, book="week")

    # the flip must be identical — they come from one build
    bf = (d["gex"].get("gamma_flip") or {}).get("nas100")
    check("chart flip == brief flip", bf == c["flip"],
          f"brief {bf} vs chart {c['flip']}")

    # walls must agree to bin rounding
    board, far = B.level_board(d)

    def levels_for(tag):
        """EVERY level the brief prints under this wall role, board + footnote.

        Three bugs lived in the single-row version of this lookup.

        It searched only `board`. D7's fix deliberately moved un-truncatable
        walls into the `far` footnote so a wall pushed off the board still
        appears somewhere — so the wall the chart drew read as "missing"
        whenever that fix did its job.

        It substring-matched `tag in name`, so "STRUCTURAL CALL WALL" shadowed
        "CALL WALL" and the check compared two different levels: on 2026-09-10
        that printed as brief 29308.4 vs chart 29508.0 and failed a build whose
        walls agreed to 0.1pt.

        And it took the FIRST match, but the brief ranks secondary walls and
        prints several rows under one role — so the nearest weak wall was
        compared against the chart's strongest one, ~200pts away.

        The contract is not "the first row matches". It is D7's contract: the
        wall the chart drew must be markable from the brief. So collect them
        all and let the caller ask whether any of them is the chart's.

        Names are matched per confluence segment. A row that carries several
        roles prints them joined — "PDL + London Low (prev-day) + STRUCTURAL
        CALL WALL" — so a plain `startswith` on the whole name misses a wall
        sharing a level with anything else, and reports a false D7. Splitting on
        " + " first keeps the exact-role match that stops "STRUCTURAL CALL WALL"
        shadowing "CALL WALL", while still finding a wall inside a confluence.
        """
        out = []
        for r in list(board) + list(far):
            if r.get("level") is None:
                continue
            parts = str(r.get("name", "")).split(" + ")
            if any(seg.strip().startswith(tag) for seg in parts):
                out.append(r["level"])
        return out

    for tag, key in (("CALL WALL", "call_res"), ("PUT WALL", "put_sup")):
        levels, cl = levels_for(tag), (c.get(key) or {}).get("price")
        if cl is None:
            # The chart drew no such wall — nothing to compare against.
            check(f"{tag} present in the chart build", True,
                  "chart has no such wall — not comparable")
            continue
        # A wall the chart drew but the brief prints NOWHERE is defect D7, the
        # exact failure this check exists to catch. The old code asserted True
        # in this branch and passed, so the guard was blind to the one thing it
        # guarded.
        check(f"{tag} the chart drew is markable from the brief",
              any(abs(b - cl) <= 26 for b in levels),
              f"chart drew {cl}; brief prints {levels or 'no such row'} — D7"
              if not any(abs(b - cl) <= 26 for b in levels) else "")

    # D4 — no strike may carry contradictory labels
    problems = GC.consistency_check(c)
    check("no strike carries contradictory labels", not problems,
          "; ".join(problems) if problems else "")

    # walls are actually dominated by their own side
    for key, lab in (("call_res", "call"), ("put_sup", "put")):
        w = c.get(key)
        if not w:
            continue
        ok = (w["call_gex"] > w["put_gex"]) if lab == "call" else (w["put_gex"] > w["call_gex"])
        check(f"{lab} wall is {lab}-dominated", ok,
              f"{w['price']:,.0f} call {w['call_gex']/1e9:.2f}bn put {w['put_gex']/1e9:.2f}bn")

    # ranks must match their sign
    check("every C rank has positive net", all(b["net"] > 0 for b in c["ranked_up"]))
    check("every P rank has negative net", all(b["net"] < 0 for b in c["ranked_dn"]))


if __name__ == "__main__":
    offline_checks()
    if "--offline" not in sys.argv:
        live_checks()
    print(f"\n{len(PASS)} passed, {len(FAIL)} failed")
    sys.exit(1 if FAIL else 0)
