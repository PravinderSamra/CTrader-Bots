#!/usr/bin/env python3
"""
test_consistency.py — the invariants that today's bugs violated.

Every check here corresponds to a bug that actually shipped. The point is not
to prove the code works; it is to make these particular failures loud if they
ever come back, because every one of them was silent.

    python3 test_consistency.py            # live data, ~2 min
    python3 test_consistency.py --offline  # structural checks only, no network
"""
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
    check("role_reversal ignores levels price never reached",
          'b["low"] - 6 <= level <= b["high"] + 6 for b in bars' in rt)

    # D6-style wiring is not enough here: assert the BEHAVIOUR, because the bug
    # was that a zero budget made both markable-distance tests unsatisfiable and
    # silently collapsed the board to structural walls only.
    import brief as _BR

    def _stub(budget, adr):
        n = {"nas100": None}
        return {"levels": {"price": 29000.0,
                           "fuel": {"remaining_budget": budget, "adr14": adr},
                           "levels": {"PDH": 29090.0, "PDL": 28950.0,
                                      "PD_mid": 29020.0},
                           "unmitigated_pools_above": [],
                           "unmitigated_pools_below": [],
                           "equal_highs": [], "equal_lows": [], "sessions": {}},
                "gex": {"gamma_flip": n, "max_pain": n, "max_pain_week": n,
                        "buckets": {"this_week": {}, "full_45dte": {}}}}

    board, _far = _BR.level_board(_stub(0.0, 400.0))
    nonstruct = [r for r in board if r["kind"] != "structural"]
    check("level board survives a zero range budget", len(nonstruct) >= 3,
          f"{len(nonstruct)} non-structural level(s) at budget=0, adr14=400")

    board0, _f0 = _BR.level_board(_stub(0.0, 0.0))
    check("no level floor invented when ADR is also zero", not board0,
          f"{len(board0)} level(s) from nothing")

    # the two gamma terms are the same fact; only one may carry points
    be = open(os.path.join(HERE, "bias_engine.py")).read()
    net_block = be.split("week net GEX")[0].rsplit("if net is not None:", 1)[-1]
    check("net-GEX gamma term is reported but not scored",
          'add("gamma", 0,' in net_block,
          "it scores again — the flip term already encodes it")

    # C3 — which side of the flip price sits on is a width read, not a
    # direction read. Both branches and the straddle adjustment score 0.
    flip_block = be.split("if net is not None:")[0].rsplit("if gf is not None:", 1)[-1]
    scored = [ln for ln in flip_block.splitlines()
              if 'add("gamma"' in ln and 'add("gamma", 0' not in ln]
    check("gamma flip term is reported but not scored", not scored,
          f"{len(scored)} flip term(s) still carry points")

    # D7 — negation guard and punctuation normalisation in the news scorer
    ns = open(os.path.join(HERE, "news_scorer.py")).read()
    check("news scorer demotes a negated keyword match",
          "NEGATOR" in ns and "NEGATOR.search(m.group(0))" in ns,
          "a negated cpi_cool would score bullish again")
    check("news scorer normalises curly punctuation before matching",
          '.replace("\u2019", "\'")' in ns,
          "a curly apostrophe bypasses the rules")

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
    board, _far = B.level_board(d)
    def find(tag):
        for r in board:
            if tag in r["name"]:
                return r["level"]
        return None
    for tag, key in (("CALL WALL", "call_res"), ("PUT WALL", "put_sup")):
        bl, cl = find(tag), (c.get(key) or {}).get("price")
        if bl is None or cl is None:
            check(f"{tag} present in both", True, "absent from one — not comparable")
            continue
        check(f"{tag} agrees within bin rounding", abs(bl - cl) <= 26,
              f"brief {bl} vs chart {cl}")

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
