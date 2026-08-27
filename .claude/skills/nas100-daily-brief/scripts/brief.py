#!/usr/bin/env python3
"""
brief.py — Phase-1 end-to-end proof: the complete NAS100 daily brief, produced
from live data by the four prototype engines, with no model in the loop.

Everything here is deterministic. In Phase 2 the agent skill's job is to read
this JSON/markdown and add judgement on top — it should never be re-deriving
numbers a script can compute exactly.

    python3 brief.py            # markdown brief
    python3 brief.py --json     # full structured payload
"""
import json, sys
from datetime import datetime, timezone

import macro_probe, levels_fuel, gex_levels, bias_engine, session_context, journal


def gather(last_scan_iso=None):
    lv = levels_fuel.run()
    if "error" in lv:
        return {"error": "cTrader unavailable", "detail": lv}
    mc = macro_probe.run()
    gx = gex_levels.build(lv["price"])
    bs = bias_engine.score(mc, lv, gx)
    gx["expiry_structure"] = gex_levels.expiry_structure(gx)
    ctx = session_context.context(last_scan_iso=last_scan_iso)
    return {"levels": lv, "macro": mc, "gex": gx, "bias": bs, "context": ctx}


def level_board(d):
    """Merge liquidity + gamma levels into one ranked, annotated board."""
    lv, gx, px = d["levels"], d["gex"], d["levels"]["price"]
    budget = lv["fuel"]["remaining_budget"]
    wk = gx["buckets"].get("this_week", {})
    rows = []

    def push(name, price, kind, note):
        if price is None:
            return
        rows.append({"level": round(price, 1), "name": name, "kind": kind,
                     "dist": round(price - px, 1),
                     "side": "above" if price > px else "below",
                     "reach": "intraday" if abs(price - px) <= budget else "swing",
                     "note": note})

    L = lv["levels"]
    push("PDH", L.get("PDH"), "liquidity",
         "Yesterday's high — the biggest pile of stops above us. Sweep it, "
         "wait for a lower high on the 1m, then CISD = short")
    push("PDL", L.get("PDL"), "liquidity",
         "Yesterday's low — the biggest pile of stops below us. Sweep it, "
         "wait for a higher low on the 1m, then CISD = long")
    push("PD mid", L.get("PD_mid"), "magnet",
         "Middle of yesterday's range. A target to aim AT, not a trigger to trade — price drifts here on quiet days")
    push("PD close", L.get("PD_close"), "magnet", "Where yesterday settled. Price often comes back to fill a gap from here")
    # PWH/PWL flip role when price displaces outside the prior week entirely —
    # calling PWL "support" while trading below it would be actively misleading.
    pwh, pwl = L.get("PWH"), L.get("PWL")
    if pwh and pwl and px < pwl:
        push("PWL", pwl, "liquidity",
             "Last week's low — but we're trading BELOW the whole of last week, so it has flipped to RESISTANCE. Sweep it and short, don't buy it")
        push("PWH", pwh, "context", "Prior-week high — far overhead, context only")
    elif pwh and pwl and px > pwh:
        push("PWH", pwh, "liquidity",
             "Last week's high — but we're trading ABOVE the whole of last week, so it has flipped to SUPPORT. Sweep it and buy")
        push("PWL", pwl, "context", "Prior-week low — far below, context only")
    else:
        push("PWH", pwh, "liquidity", "Prior-week high — big pool, best Mon-Tue")
        push("PWL", pwl, "liquidity", "Prior-week low — big pool, best Mon-Tue")
    for tag, label in (("sessions_prev_day", "prev-day"), ("sessions_today", "today")):
        for sess, v in (L.get(tag) or {}).items():
            push(f"{sess.upper() if sess in ('ny',) else sess.title()} High ({label})", v["high"], "liquidity",
                 f"High of the {sess.upper() if sess in ('ny',) else sess.title()} session — the next session usually runs the stops above it")
            push(f"{sess.upper() if sess in ('ny',) else sess.title()} Low ({label})", v["low"], "liquidity",
                 f"Low of the {sess.upper() if sess in ('ny',) else sess.title()} session — the next session usually runs the stops below it")
    # Single-touch swing extremes are dropped entirely. They were nine of the
    # thirty rows on the old board, every one of them labelled "context only" —
    # i.e. the board itself said don't trade them, while they took a row each.
    # A lone swing high is not a pool of stops; it's just where price turned.
    # Multi-touch clusters ARE kept: equal highs/lows are a genuine stop
    # cluster and a primary strategy-1 sweep trigger. They're relabelled so
    # it's obvious why they earned a row.
    for p in lv["unmitigated_pools_above"] + lv["unmitigated_pools_below"]:
        if not p["confirmed"]:
            continue
        side = "highs" if p["price"] > px else "lows"
        push(f"Equal {side} \u00d7{p['touches']}", p["price"], "liquidity",
             f"{p['touches']} touches at this price, never traded through — "
             f"a real stop cluster. Prime S1 sweep trigger")

    gf = gx["gamma_flip"]
    flip_px = gf.get("nas100")
    # We KNOW which regime we're in, so state what applies today rather than
    # printing both branches and making the reader work out which is live.
    long_gamma = flip_px is not None and px > flip_px
    push("GAMMA FLIP", flip_px, "gamma",
         ("The line where the big desks switch from damping moves to pushing "
          "them. We're ABOVE it: they're damping, so fades work. Lose this and "
          "hold below and that reverses — stop fading."
          if long_gamma else
          "The line where the big desks switch from pushing moves along to "
          "damping them. We're BELOW it: they're pushing, so don't fade. "
          "Reclaim and hold above and fading becomes valid again."))
    # Wall strength belongs in the NAME, not buried at the end of a sentence —
    # 7k contracts and 168k contracts are not the same level and should not
    # look the same on a chart.
    full = gx["buckets"].get("full_45dte", {})

    def oi_short(n):
        return f"{n/1000:.0f}k" if n >= 1000 else str(int(n))

    cw, pw = wk.get("call_wall"), wk.get("put_wall")
    fcw, fpw = full.get("call_wall"), full.get("put_wall")

    # Strength is measured in GAMMA FORCE ($GEX), not contract count.
    #
    # An earlier version banded walls by open interest. Measured on real data
    # that is misleading: the 45-day put wall held 168,275 contracts against the
    # weekly put wall's 7,091 (24x the OI) but produced only 3.6x the hedging
    # force, because gamma collapses with distance from spot. Per contract it
    # was 11x WEAKER than the at-the-money weekly call wall. Contract count
    # says how many bets sit there; $GEX says how hard dealers must trade to
    # stay hedged, and only the second one moves price.
    #
    # The scale is RELATIVE to the strongest wall in this run, so it adapts to
    # a quiet week vs an OPEX week instead of relying on fixed thresholds that
    # would be wrong half the time.
    # Normalised WITHIN GROUP — this-week walls against each other, structural
    # walls against each other. Comparing across groups was misleading in the
    # other direction: the structural put wall has the highest absolute force
    # (1.01bn) purely because it holds 168k contracts, so it rendered as the
    # strongest thing on the board while sitting 609pts away and being
    # irrelevant to today. Dots now answer "how strong is this among walls of
    # its own kind", which is the question that has a useful answer. The
    # absolute $bn is printed alongside for cross-group comparison.
    _wk_peak = max((w.get("gex_$bn", 0) for w in (cw, pw) if w), default=0) or 1.0
    _st_peak = max((w.get("gex_$bn", 0) for w in (fcw, fpw) if w), default=0) or 1.0

    def wall_tag(w, structural=False):
        g = w.get("gex_$bn", 0) or 0
        share = g / (_st_peak if structural else _wk_peak)
        filled = max(1, min(5, int(share * 5 + 0.5)))
        return "\u25cf" * filled + "\u25cb" * (5 - filled) + f" {g:.2f}bn"

    if cw:
        # Same strike in both tenors = the wall is defended across expiries,
        # which is materially stronger than a one-week wall.
        conf = fcw and abs(fcw["nas100"] - cw["nas100"]) <= 5
        extra = (f" It is ALSO the 45-day call wall ({oi_short(fcw['oi'])} "
                 f"contracts) — defended across expiries, so it is the strongest "
                 f"ceiling on the board." if conf else "")
        push(f"CALL WALL {wall_tag(cw)}",
             cw["nas100"], "gamma",
             f"Heaviest ceiling this week ({oi_short(cw['oi'])} contracts) — "
             f"desks must SELL as price rises into it, so rallies stall. Take "
             f"profit into it. A held close above flips that selling to buying "
             f"and it becomes a launchpad.{extra}")
    if pw:
        conf = fpw and abs(fpw["nas100"] - pw["nas100"]) <= 5
        extra = (f" It is ALSO the 45-day put wall ({oi_short(fpw['oi'])} "
                 f"contracts) — defended across expiries, so it is the strongest "
                 f"floor on the board." if conf else "")
        push(f"PUT WALL {wall_tag(pw)}",
             pw["nas100"], "gamma",
             (f"Heaviest floor this week ({oi_short(pw['oi'])} contracts) — "
              f"expect a bounce and a good long-sweep here.{extra}" if long_gamma
              else
              f"Heaviest floor this week ({oi_short(pw['oi'])} contracts), BUT "
              f"today the desks are pushing moves along — if it breaks, expect "
              f"it to speed UP, not bounce. Don't buy the break.{extra}"))

    # STRUCTURAL walls from the 45-day book. These are frequently far outside
    # today's range and were being filtered off the board entirely — but a
    # 168k-contract concentration is the level a multi-day move stops at, and
    # it belongs on the chart even when it is not today's target.
    if fcw and (not cw or abs(fcw["nas100"] - cw["nas100"]) > 5):
        push(f"STRUCTURAL CALL WALL {wall_tag(fcw, structural=True)}",
             fcw["nas100"], "structural",
             f"The 45-day call wall ({oi_short(fcw['oi'])} contracts) — the "
             f"ceiling for the WEEK/MONTH, not today. "
             f"Mark it and leave it: it is where a multi-day rally runs out of "
             f"room, not an intraday trigger")
    if fpw and (not pw or abs(fpw["nas100"] - pw["nas100"]) > 5):
        push(f"STRUCTURAL PUT WALL {wall_tag(fpw, structural=True)}",
             fpw["nas100"], "structural",
             f"The 45-day put wall ({oi_short(fpw['oi'])} contracts) and the "
             f"biggest concentration on the chain — the floor for the "
             f"WEEK/MONTH. Mark it and leave "
             f"it: where a multi-day sell-off is defended, not an intraday trigger")
    push("MAX PAIN", gx["max_pain_week"]["nas100"], "gamma",
         "Where the most options expire worthless — price drifts toward it as "
         "the week goes on. Weak on a Monday, strong by Thursday/Friday")
    # Only shelves price REACTS at earn a row on the board.
    #
    # A negative shelf is, by definition, where price accelerates through. As a
    # chart marking it tells you nothing — you can't trade "it goes straight
    # past here". It stays in the data (bias_engine still reads it) but it is
    # not a level to draw, so it's out of the board and summarised in a footer.
    #
    # Positive shelves do cause a stall, so they stay — but only if they're big
    # enough to matter and close enough to reach today. The threshold scales
    # with the day's own gamma so it adapts instead of being a magic number.
    pos = [p for p in (wk.get("largest_abs_gex") or []) if p["sign"] == "+"]
    if pos:
        biggest = max(p["net_gex_$bn"] for p in pos)
        floor_bn = max(0.05, biggest * 0.35)
        for p in pos:
            if p["net_gex_$bn"] < floor_bn:
                continue
            if abs(p["nas100"] - px) > budget:
                continue
            push(f"Options shelf {p['net_gex_$bn']:.2f}bn", p["nas100"], "gamma-shelf",
                 "Heavy dealer hedging parked here — expect price to stall. "
                 "Good place to take partials rather than push through")

    # Merge rows that are the same price. Confluence should make ONE level
    # stronger, not print three rows: 29381.6 was appearing separately as call
    # wall, max pain and a GEX shelf, and 29133.6 as PDL, NY Low and an
    # unmitigated low. Same price, same line, names joined.
    rows.sort(key=lambda r: -r["level"])
    merge_tol = max(3.0, (lv["fuel"]["adr14"] or 0) * 0.008)
    merged = []
    for r in rows:
        if merged and abs(merged[-1]["level"] - r["level"]) <= merge_tol:
            m = merged[-1]
            if r["name"] not in m["name"]:
                m["name"] += " + " + r["name"]
            # strongest kind wins the row's colour/priority
            rank = {"gamma": 5, "structural": 4, "liquidity": 3,
                    "gamma-shelf": 2, "magnet": 1, "context": 0}
            if rank.get(r["kind"], 0) > rank.get(m["kind"], 0):
                m["kind"], m["note"] = r["kind"], r["note"]
            m["confluence"] = m.get("confluence", 1) + 1
            continue
        r["confluence"] = 1
        merged.append(r)

    # Anything beyond today's range budget can't be reached, so it isn't a level
    # to mark — it's a footnote. Keeps PWH at +885 out of the first row.
    # PDH/PDL and the session extremes are primary strategy-1 triggers. The
    # first cut of this filter pushed PDH into the footnote for being 162pts
    # away against a 156pt budget — technically out of budget, but it is the
    # level most likely to be swept all day. Core levels stay on the board and
    # get flagged as a stretch instead; only genuinely distant things drop out.
    CORE = ("PDH", "PDL", "PWH", "PWL", "High", "Low", "GAMMA FLIP",
            "CALL WALL", "PUT WALL")
    def keep(r):
        if r["reach"] == "intraday":
            return True
        # Structural walls are deliberately exempt from the budget filter: they
        # are week/month boundaries, so being out of today's range is the whole
        # point of them.
        if r["kind"] == "structural":
            return True
        core = any(c in r["name"] for c in CORE)
        return core and abs(r["dist"]) <= budget * 1.75
    board = [r for r in merged if keep(r)]
    far = [r for r in merged if not keep(r)]
    for r in board:
        r["stretch"] = r["reach"] != "intraday"
    return board, far


# The budget forecasts how much further the day's HIGH-LOW RANGE can grow. It
# has never forecast how far price will travel, and the two diverge sharply once
# a range is established. Measured 2026-08-24: a 0.0pt budget was followed by
# 5.3pts of range extension (right) while price traversed 284.4pts inside the
# range. The old wording ("do not initiate", "range is spent") described
# movement and so read as "nothing will happen", which was actively misleading
# on the day it mattered most.
_FUEL_MEANING = {
    "SESSION_PENDING": (
        "**The new trading day has not opened yet** — the feed is quiet across "
        "the 21:00 UTC rollover, so there is no range to measure and no fuel "
        "read. Treat the full ADR as available and re-scan once the session "
        "has ticks. This is *unknown*, not *exhausted*: the previous day's "
        "range tells you nothing about this one.",
        "no fuel-based stop guidance until the session opens \u2014 size and manage "
        "off structure alone, and re-run the brief after the open."),
    "ROOM_TO_EXPAND": (
        "The range can still grow. New highs/lows are live — breakouts and "
        "continuation have somewhere to go.",
        "leave the structural stop alone; trail only on confirmed 1m structure breaks."),
    "MODERATE": (
        "The range has room but not unlimited room. Continuation is fine to the "
        "nearest pool; don't plan on a third leg.",
        "structural stop; break-even at 1R or 50% of remaining budget, whichever first."),
    "LOW_FUEL": (
        "The range is close to done. Expect price to keep MOVING but mostly "
        "**inside** the extremes rather than making new ones — favour fades "
        "over chasing breaks.",
        "active management from entry \u2014 break-even at 0.7R, 50% off at the "
        "first pool, trail tight."),
    "EXHAUSTED": (
        "**The day's range is set — but that is not the same as 'nothing will "
        "happen'.** Expect real movement still, just **within** the extremes "
        "rather than beyond them. Continuation into new highs/lows is the "
        "low-probability trade; the range width is where the remaining "
        "opportunity is.",
        "don't chase a break. If already in a continuation trade, take partials "
        "\u2014 you are trading the last few points of extension. Fading the "
        "extremes back into the range is the higher-probability side here, even "
        "when the gamma regime favours continuation."),
}


def budget_txt(d):
    return f"{d['levels']['fuel']['remaining_budget']:.0f}pt"


def path_read(d):
    """What sits BETWEEN price and the next real barrier, in each direction.

    This is the intraday translation of a distant structural wall. A wall 609pts
    away is not a level a day trader will reach — but the corridor leading to it
    is very much today's business. If every gamma shelf in between is negative
    there is nothing to slow a move, so a break has room and must not be faded.
    If a positive shelf sits in the way, expect a stall there instead.
    """
    gx, lv = d["gex"], d["levels"]
    px = lv["price"]; budget = lv["fuel"]["remaining_budget"]
    adr = lv["fuel"]["adr14"] or 1
    wk = gx["buckets"].get("this_week", {})
    shelves = wk.get("largest_abs_gex") or []
    out = {}

    for side, sign in (("below", -1), ("above", +1)):
        span = [p_ for p_ in shelves
                if 0 < (p_["nas100"] - px) * sign <= adr * 1.2]
        if not span:
            out[side] = None
            continue
        span.sort(key=lambda p_: (p_["nas100"] - px) * sign)
        # a positive shelf is the only thing that actually brakes a move
        brake = next((p_ for p_ in span if p_["sign"] == "+"), None)
        far = span[-1]
        net = sum(p_["net_gex_$bn"] for p_ in span)
        dist_to_far = abs(far["nas100"] - px)
        out[side] = {
            "shelves": len(span),
            "net_bn": round(net, 3),
            "first_brake": brake["nas100"] if brake else None,
            "brake_dist": round(abs(brake["nas100"] - px), 0) if brake else None,
            "corridor_end": far["nas100"],
            "corridor_pts": round(dist_to_far, 0),
            "corridor_adr": round(dist_to_far / adr, 2),
            "in_budget": dist_to_far <= budget,
            "friction": "NONE" if brake is None else
                        ("LOW" if brake and abs(brake["nas100"] - px) > budget else "SOME"),
        }
    return out


def markdown_levels_only(d):
    """The chart-marking answer only: where we are, what to mark, how to manage.
    Same renderer and same wording as the full brief — a subset, never a
    rewrite, so /nas100-brief levels can't drift from /nas100-brief."""
    lv = d["levels"]; f = lv["fuel"]; px = lv["price"]
    c = d.get("context") or {}
    o = []; A = o.append
    A(f"# NAS100 levels \u2014 {c.get('trading_day', lv['trading_day'])}")
    A(f"_{c.get('now_uk', '')} \u00b7 price **{px}**_\n")
    if c.get("headline"):
        A(f"> {c['headline']}\n")
    A(f"**Fuel:** ADR14 {f['adr14']} \u00b7 {f['adr_used_pct']}% used \u00b7 "
      f"**{f['remaining_budget']:.0f}pts budget left** \u2192 "
      f"`{f['expansion_state']}`\n")
    pr = path_read(d)
    for side, label, verb in (("below", "DOWNSIDE", "breakdown"),
                              ("above", "UPSIDE", "breakout")):
        r = pr.get(side)
        if not r:
            continue
        if r["friction"] == "NONE":
            A(f"- **{label} path clear** to {r['corridor_end']} "
              f"({r['corridor_pts']:.0f}pts) \u2014 nothing to slow a {verb}. "
              f"Don't fade it.")
        elif r["friction"] == "LOW":
            A(f"- **{label} path mostly clear** \u2014 first brake "
              f"{r['first_brake']} is beyond today's budget.")
        else:
            A(f"- **{label} stalls at {r['first_brake']}** "
              f"({r['brake_dist']:.0f}pts) \u2014 partials into it.")
    A("")
    meaning, mgmt = _FUEL_MEANING[f["expansion_state"]]
    A(f"_Budget = how much further the RANGE can grow, not how far price "
      f"travels._ {meaning}\n")
    A(f"**Stop management:** {mgmt}\n")
    for line in expected_move_md(d, compact=True):
        A(line)
    board, far = level_board(d)
    A("_Wall strength ●●●○○ is **gamma force** relative to the strongest wall "
      "of the same type, not contract count._\n")
    A("| NAS100 | dist | level | what to expect |")
    A("|---|---|---|---|")
    for r in board:
        star = " \u2b50" if r.get("confluence", 1) > 1 else ""
        tag = (" _(stretch)_" if r.get("stretch") and r["kind"] != "structural"
               else "")
        dist = f"{r['dist']:+.0f}" if abs(r["dist"]) >= 1.0 else "at price"
        A(f"| **{r['level']}** | {dist} | {r['name']}{star}{tag} | {r['note']} |")
    if far:
        A("\n_Beyond today's range (context only, don't mark): "
          + " \u00b7 ".join(f"{r['level']:.0f} {r['name']}" for r in far[:6]) + "_")
    sw = secondary_walls_md(d, board)
    if sw:
        A("")
        for line in sw:
            A(line)
    return "\n".join(o)


def expected_move_md(d, compact=False):
    """Market-implied boundaries for the next session, from the ATM straddle."""
    em = (d["gex"] or {}).get("expected_move")
    if not em:
        return []
    when = ("the rest of today" if em["dte"] == 0
            else "tomorrow" if em["dte"] == 1
            else f"the next {em['dte']} sessions")
    if compact:
        return [f"**Expected move ({when}):** ±**{em['em_pts']:.0f}pts** "
                f"({em['em_pct']:.2f}%) → **{em['lower']:.0f} .. {em['upper']:.0f}** "
                f"_(close-to-close, not a high-low range — do not compare to ADR)_\n"]
    return [
        f"- **Expected move, {when}:** ±**{em['em_pts']:.0f}pts** "
        f"({em['em_pct']:.2f}%) → **{em['lower']:.0f} .. {em['upper']:.0f}**",
        f"  - from the {em['expiry']} ATM straddle at {em['straddle']:.0f}pts "
        f"(ATM IV {em['iv_atm']*100:.1f}%) — the market's own price for the move, "
        f"not a vol index scaled down",
        f"  - **this is a CLOSE-to-close band, not a high-low range.** ADR measures "
        f"high-low and is always the larger number; comparing the two directly is "
        f"the same error as reading the range budget as price travel. Price closes "
        f"inside this band roughly two days in three, and routinely trades outside "
        f"it intraday.\n",
    ]


def secondary_walls(d, board):
    """Gamma concentrations that are NOT the single call/put wall.

    The board names one call wall and one put wall. Those two fields are
    `max(above, key=call_gex)` and `max(below, key=put_gex)`, which means a
    heavy strike that is neither cannot appear at all — and on 2026-08-25 the
    largest concentration within 280pts of spot was exactly that: 1.29bn of
    CALL gamma sitting BELOW spot (in-the-money calls, dealers buying dips).
    Price pivoted on it for the whole afternoon and it was never published.

    Windowed on ADR, not on the range budget. The budget forecasts how much
    further the RANGE can grow; these are levels price can still REACH inside
    the range, which is a different question and the one that matters when
    fuel is exhausted but price is still travelling 250pts.
    """
    gx, px = d["gex"], d["levels"]["price"]
    adr = d["levels"]["fuel"].get("adr14") or 0
    wk = gx["buckets"].get("this_week", {})
    ranked = wk.get("walls_ranked") or {}
    if not ranked:
        return []
    window = adr * 0.75 or 250.0
    on_board = [r["level"] for r in board]
    tol = max(6.0, adr * 0.015)
    out = []
    for side in ("above", "below"):
        for w in ranked.get(side, []):
            lvl = w["nas100"]
            if abs(lvl - px) > window:
                continue
            if any(abs(lvl - b) <= tol for b in on_board):
                continue          # already published, don't print it twice
            out.append({**w, "dist": round(lvl - px, 1), "side": side})
    out.sort(key=lambda w: -w["gex_$bn"])
    return out[:6]


def secondary_walls_md(d, board):
    rows = secondary_walls(d, board)
    if not rows:
        return []
    o = ["**Other gamma concentrations in range** — the heaviest strikes behind "
         "the headline call/put wall, which name only one level each side. "
         "Read the last column for what each one DOES: call-dominant strikes "
         "brake a move, put-dominant strikes speed it up. They are not all "
         "support.\n",
         "| NAS100 | dist | force | contracts | what it does |",
         "|---|---|---|---|---|"]
    # Behaviour follows the SIGN of dealer gamma at the strike, under this
    # repo's stated convention (dealers long calls, short puts):
    #   call-dominant -> dealers long gamma  -> they damp   -> barrier / pin
    #   put-dominant  -> dealers short gamma -> they amplify -> accelerant
    #
    # The first version of this table got both put cases wrong. It called every
    # put-dominant strike below spot "a genuine floor", which is the opposite
    # of what short gamma does, and labelled put strikes ABOVE spot
    # "out-of-the-money" when a put struck above spot is IN the money — while
    # calling the single largest force in the table "thin". On 2026-08-26 that
    # put two "genuine floors" below spot on the same page as a brief saying
    # the downside path was clear and not to fade it.
    long_gamma = (d["gex"].get("gamma_flip") or {}).get("nas100")
    long_gamma = long_gamma is not None and d["levels"]["price"] > long_gamma
    for w in rows:
        itm = ((w["dominant"] == "CALL" and w["side"] == "below") or
               (w["dominant"] == "PUT" and w["side"] == "above"))
        money = "in-the-money" if itm else "out-of-the-money"
        if w["dominant"] == "CALL":
            what = (f"{money} call gamma — dealers are LONG gamma here, so they "
                    f"damp moves: expect a "
                    + ("stall and dip-buying, it acts as **support**"
                       if w["side"] == "below" else
                       "stall — rallies lose momentum into it"))
        else:
            what = (f"{money} put gamma — dealers are SHORT gamma here, so they "
                    f"**amplify**: price tends to accelerate THROUGH rather than "
                    f"stall. Not a floor"
                    + ("" if not long_gamma else
                       ". Net book is long gamma today, so treat it as a "
                       "speed-bump rather than an accelerant"))
        o.append(f"| **{w['nas100']:.1f}** | {w['dist']:+.0f} | {w['gex_$bn']:.2f}bn | "
                 f"{w['oi']:,} | {what} |")
    return o


def markdown(d):
    lv, mc, gx, bs = d["levels"], d["macro"], d["gex"], d["bias"]
    px, f = lv["price"], lv["fuel"]
    v, rf = mc["volatility"], mc["rates_fx"]
    o = []
    A = o.append
    c = d.get("context") or {}
    A(f"# NAS100 Daily Brief — {c.get('trading_day', lv['trading_day'])}")
    A(f"_{c.get('now_uk', '')} · price **{px}** (bid {lv['bid']} / ask {lv['ask']})_\n")
    if c.get("headline"):
        A(f"> {c['headline']}\n")
    ps = c.get("previous_scan")
    if ps and "relation" in ps:
        A(f"> {ps['relation']}\n")
    elif c.get("first_scan"):
        A("> First scan on record — nothing to compare against yet.\n")

    A(f"## 1. The call: **{bs['label']}**  (score {bs['score']:+d})\n")
    A(f"**{bs['strategy_call']}**\n")
    if bs.get("event_gate"):
        A(f"> ⚠️ **{bs['event_gate']}**\n")
    # The full component table is transparency, not a decision input. Collapsed
    # here — but every row is still written to the journal, because the whole
    # point of Phase 4 is asking which components actually predicted the day.
    tallies = {}
    for r in bs["components"]:
        tallies[r["component"]] = tallies.get(r["component"], 0) + r["points"]
    drivers = sorted(tallies.items(), key=lambda kv: -abs(kv[1]))
    A("Driven by: " + " · ".join(
        f"**{k} {v:+d}**" for k, v in drivers if v != 0) + "\n")
    A("<details><summary>Full scoring breakdown "
      f"({len(bs['components'])} checks)</summary>\n")
    A("| component | pts | reasoning |")
    A("|---|---|---|")
    for r in bs["components"]:
        A(f"| {r['component']} | {r['points']:+d} | {r['why']} |")
    A("\n</details>\n")

    A("## 2. Regime — what kind of day is this?\n")

    flip = gx["gamma_flip"]["nas100"]
    wk = gx["buckets"].get("this_week", {})
    net = wk.get("net_gex_$bn_per_1pct") or 0
    long_gamma = flip is not None and px > flip

    # Each block leads with the technical read, then explains it. Keeps the
    # brief scannable once the vocabulary is familiar, and teaches the terms by
    # always pairing them with what they mean.
    A(f"**Gamma:** flip at **{flip}**, price {px} \u2192 "
      f"**{gx['gamma_flip']['spot_position']}** \u00b7 "
      f"this week's net GEX **{net} $bn per 1% move**\n")
    if long_gamma:
        A(f"> The big options desks are **leaning against** today's move. When "
          f"price runs up they sell into it; when it dips they buy. That squashes "
          f"the range and makes moves fade back.\n"
          f">\n"
          f"> \u27a4 **Sweeps of a high or low tend to genuinely fail** \u2014 exactly "
          f"what Strategy 1 needs. This is your fade day.\n"
          f">\n"
          f"> \u27a4 It stops working below **{flip}**. If price loses that and holds "
          f"below, they flip to pushing moves along instead \u2014 stop fading.\n")
    else:
        A(f"> The big options desks are **pushing today's move along**, not "
          f"leaning against it. As price falls they have to sell more; as it "
          f"rises they buy more. Their hedging adds fuel to whatever is already "
          f"happening.\n"
          f">\n"
          f"> \u27a4 **Sweeps tend to keep running rather than fail.** Fading is the "
          f"wrong trade today \u2014 Strategy 2 (go with the move) is the right one.\n"
          f">\n"
          f"> \u27a4 It flips at **{flip}**. Reclaim and hold above and they start "
          f"damping moves again, and fading becomes valid.\n")

    vxn = v["vxn_nasdaq_ivol"].get("last"); vxn_c = v["vxn_nasdaq_ivol"].get("chg_pct")
    term = v.get("vix9d_over_vix"); vixl = v["vix"].get("last")
    implied = round(px * (vxn / 100) / (252 ** 0.5)) if vxn else None
    A(f"**Volatility:** VXN **{vxn}** ({vxn_c:+.1f}%) \u00b7 VIX {vixl} \u00b7 "
      f"VIX9D/VIX **{term}** \u2192 {v['term_read'].split(' — ')[0]} \u00b7 "
      f"VVIX {v['vvix'].get('last')}\n")
    A(f"> **VXN is the Nasdaq's own fear gauge.** At {vxn} it's "
      f"{'down' if (vxn_c or 0) < 0 else 'up'} {abs(vxn_c or 0):.1f}% \u2014 "
      f"{'fear is easing' if (vxn_c or 0) < 0 else 'fear is building'}, and it "
      f"prices a **~{implied}pt day**.\n>")
    if term is not None:
        A(f"> **VIX9D/VIX compares worry about the next 9 days against the next "
          f"month.** At {term} the near-term worry is "
          f"{'HIGHER' if term > 1.0 else 'lower'}. "
          + ("Something specific is spooking people short-term \u2014 expect a "
             "bigger range than normal." if term > 1.0 else
             "Nothing urgent is spooking anyone \u2014 a calmer, more rangebound "
             "day.") + "\n>")
    if vxn and vixl:
        rr = round(vxn / vixl, 2)
        A(f"> **VXN vs VIX** is tech's nerves against the whole market's. Tech is "
          f"priced **{(rr - 1) * 100:.0f}% jumpier**."
          + (" That's a big gap \u2014 the nervousness is specifically about tech, "
             "not stocks in general.\n" if rr > 1.35 else " A normal gap.\n"))

    y10, y10c = rf["us10y"].get("last"), rf["us10y"].get("chg_pct")
    dxy, dxyc = rf["dxy"].get("last"), rf["dxy"].get("chg_pct")
    A(f"**Rates / FX:** US10y **{y10}%** ({y10c:+.2f}%) \u00b7 "
      f"DXY **{dxy}** ({dxyc:+.2f}%)\n")
    A("> **The 10-year yield is the rate everything else is priced off.** "
      + ("It's rising, which hurts tech more than anything else \u2014 tech is "
         "valued on profits far in the future, and those are worth less when "
         "rates go up." if (y10c or 0) > 0.3 else
         "It's falling, which helps tech more than anything else, for the same "
         "reason in reverse." if (y10c or 0) < -0.3 else
         "Barely moved today \u2014 not a factor.") + "\n>")
    A("> **DXY is the dollar against a basket of currencies.** "
      + ("It's bid, which usually means money is leaving risky assets.\n"
         if (dxyc or 0) > 0.4 else
         "It's soft, which usually helps risk appetite.\n" if (dxyc or 0) < -0.4 else
         "Flat \u2014 not a factor today.\n"))

    es = gx.get("expiry_structure") or {}
    if es:
        A(f"**Shape of the day:** `{es['shape']}` "
          f"(confidence {es['confidence']}) \u00b7 today {es['near_0_2dte']} \u00b7 "
          f"this week {es['this_week']} \u00b7 45-day {es['full_45dte']} "
          f"$bn per 1%\n")
        A(f"> {es['what_it_is']}\n>\n> \u27a4 {es['what_to_do']}\n")

    basis = gx.get("basis") or {}
    if basis.get("method") == "nq_implied":
        A(f"> \u2139\ufe0f **Options levels are anchored to an inferred index price.** "
          f"NDX cash last traded {basis['cash_last_trade']} "
          f"({basis['cash_age_min']:.0f} min ago) \u2014 it does not print outside US "
          f"cash hours. The reference has been rolled forward by the NQ futures "
          f"move ({basis['nq_move_since_close']:+.1f}) to **{basis['ndx_reference']}**. "
          f"CBOE's published greeks are from that same stale timestamp, so gamma "
          f"has been **recomputed at the current spot** rather than taken as "
          f"published. Levels are good; they firm up once cash opens.\n")
    elif basis.get("method") == "stale_cash_UNCORRECTED":
        A(f"> \u26a0\ufe0f **WARNING \u2014 {basis.get('warning')}**\n")

    A("<details><summary>Data ages and conversion</summary>\n")
    A(f"- CFD/index offset **{gx['cfd_offset']}** (NDX reference {gx['ndx_spot']} "
      f"vs CFD {px}, price basis `{basis.get('method', 'live_cash')}`, "
      f"greeks `{basis.get('greeks', 'cboe_published')}`) "
      f"\u2014 every options level below is already converted to your chart's price")
    A(f"- Data age: NDX chain {gx['as_of']['ndx']}, QQQ chain {gx['as_of']['qqq']}")
    A("\n</details>\n")

    fr = mc.get("fred") or {}
    A("**Rates, borrowing and money supply**\n")
    if fr.get("key_present"):
        for x in fr.get("read", []):
            mark = "🟢" if x["signal"] > 0 else ("🔴" if x["signal"] < 0 else "⚪")
            A(f"- {mark} {x['text']}")
        A("\n_These update once a day or so — they set the mood for the week, "
          "they are not a signal to trade off right now._\n")
    else:
        A("- _No FRED key set, so the real-interest-rate picture is missing "
          "\u2014 running on headline bond yields only._\n")

    A("## 3. Fuel & range budget\n")
    vxn = v["vxn_nasdaq_ivol"].get("last")
    implied = round(px * (vxn / 100) / (252 ** 0.5), 1) if vxn else None
    A(f"- ADR14 **{f['adr14']}** · today's range **{f['today_range']}** "
      f"(**{f['adr_used_pct']}% used**) · raw budget left **{f['remaining_budget']}** "
      f"→ `{f['expansion_state']}`")
    A(f"- fuel_ratio vs time of day: **{bs['fuel_ratio']}**")
    A(f"- VXN-implied daily range: **{implied}** pts "
      f"({'below' if implied and implied < f['adr14'] else 'above'} ADR — "
      f"{'options market prices a quieter day, use the smaller budget' if implied and implied < f['adr14'] else 'options market prices expansion, ADR understates'})")
    A(f"- volume: **{f['volume_state']}** ({f['volume_relative']})\n")
    for line in expected_move_md(d):
        A(line)
    pr = path_read(d)
    for side, label, verb in (("below", "DOWNSIDE", "breakdown"),
                              ("above", "UPSIDE", "breakout")):
        r = pr.get(side)
        if not r:
            continue
        if r["friction"] == "NONE":
            A(f"- **{label} path: clear.** Every options shelf from here to "
              f"{r['corridor_end']} ({r['corridor_pts']:.0f}pts, "
              f"{r['corridor_adr']}× ADR) is negative gamma — **nothing "
              f"structural to slow a {verb}.** If it goes, it has room. Do not "
              f"fade it.")
        elif r["friction"] == "LOW":
            A(f"- **{label} path: mostly clear.** First real brake is "
              f"{r['first_brake']} ({r['brake_dist']:.0f}pts away), which is "
              f"beyond today's {budget_txt(d)} budget — so inside today's range "
              f"there is little to stop a {verb}.")
        else:
            A(f"- **{label} path: has friction.** Expect a stall at "
              f"{r['first_brake']} ({r['brake_dist']:.0f}pts away) — take "
              f"partials into it rather than assuming a clean {verb}.")
    A("")
    meaning, mgmt = _FUEL_MEANING[f["expansion_state"]]
    A(f"**What the budget means:** it forecasts how much further the day's "
      f"**range** can grow \u2014 not how far price will travel. {meaning}\n")
    A(f"**Stop management:** {mgmt}\n")

    A("## 4. Level board — mark these\n")
    board, far = level_board(d)
    A("_Wall strength ●●●○○ is **gamma force** relative to the strongest wall "
      "of the same type — how hard dealers must trade to stay hedged there. Not "
      "contract count: a far-away wall can hold 24x the contracts and still "
      "push price less, because gamma collapses with distance._\n")
    A(f"_Same price = one line, so a level named twice is two reasons to "
      f"respect it (⭐). Today's remaining range budget is "
      f"**{f['remaining_budget']:.0f}pts** — anything marked _(stretch)_ is "
      f"beyond that, so treat it as partials-only._\n")
    A("| NAS100 | dist | level | what to expect |")
    A("|---|---|---|---|")
    for r in board:
        star = " ⭐" if r.get("confluence", 1) > 1 else ""
        tag = (" _(stretch)_" if r.get("stretch") and r["kind"] != "structural"
               else "")
        dist = f"{r['dist']:+.0f}" if abs(r["dist"]) >= 1.0 else "at price"
        A(f"| **{r['level']}** | {dist} | {r['name']}{star}{tag} | {r['note']} |")
    A("")
    if far:
        A("_Beyond today's range (context only, don't mark): "
          + " · ".join(f"{r['level']:.0f} {r['name']}" for r in far[:6]) + "_\n")

    for line in secondary_walls_md(d, board):
        A(line)
    A("")

    A("## 5. Events\n")
    up = mc["calendar"].get("upcoming_next_24h") or []
    if up:
        for e in up:
            A(f"- **[{e['impact']}]** {e['utc'][11:16]} UTC — {e['title']} "
              f"(cons {e['forecast'] or 'n/a'}, prev {e['previous'] or 'n/a'}) "
              f"— in {e['hours_away']}h")
    else:
        A("- No High/Medium US events in the next 24h.")
    for e in mc["calendar"].get("heavyweight_earnings_next_5d") or []:
        A(f"- **EARNINGS** {e['date']} {e['symbol']} ({e.get('when')}) — "
          f"cons {e.get('eps_forecast')}")
    A("")

    A("## 6. News that matters\n")
    ns = mc.get("news_scored") or {}
    if "_error" not in ns:
        A(f"_{ns['headlines_pulled']} headlines from {ns['feeds_ok']}/"
          f"{ns['feeds_total']} feeds -> {ns['passed_relevance']} relevant -> "
          f"**{ns['scored_high_confidence']} auto-scored**, "
          f"{ns['needs_model_judgement']} for judgement._\n")
        A(f"**Scored: {ns['label']} ({ns['raw_score']:+.2f})**\n")
        if ns.get("high_confidence"):
            A("| dir | headline | reaction | size / half-life |")
            A("|---|---|---|---|")
            for it in ns["high_confidence"][:6]:
                d = "🟢 bull" if it["direction"] > 0 else ("🔴 bear" if it["direction"] < 0 else "⚪ amb")
                A(f"| {d} | {it['title'][:74]} | {it['note']} | "
                  f"~{it['magnitude_pts']}pts / {it['half_life_min']}min |")
            A("")
        else:
            A("_No headline was unambiguous enough to auto-score — "
              "read the judgement list below._\n")
        if ns.get("for_model_judgement"):
            A("**Needs reading in context** (negation, hypotheticals and "
              "relevance are handled here, not by keywords):\n")
            for it in ns["for_model_judgement"][:8]:
                fl = f" — _{'; '.join(it['flags'])}_" if it.get("flags") else ""
                A(f"- [{it['rule']}] {it['title'][:96]}{fl}")
            A("")
    else:
        for src in ("nasdaq_24h", "mag7_24h", "cnbc", "fed_press"):
            items = [h for h in mc["news"].get(src, []) if "title" in h][:4]
            if items:
                A(f"**{src}**")
                for h in items:
                    A(f"- {h['title']}")
                A("")
    A("---")
    A("_All figures computed from CBOE delayed quotes, cTrader NAS100 (id 116), "
      "Yahoo chart API, ForexFactory and Nasdaq calendars. No API keys. "
      "GEX assumes the standard long-call/short-put dealer convention — levels "
      "and regime are robust, absolute dollar figures are approximate._")
    return "\n".join(o)


if __name__ == "__main__":
    # Chain scans together: the previous scan's timestamp is what lets the
    # brief say "new trading day" vs "continuation".
    d = gather(last_scan_iso=journal.last_scan_utc())
    if "error" in d:
        print(json.dumps(d, indent=2, default=str)); sys.exit(1)

    def _chart():
        """Draw the gamma chart from THIS scan's build, not a fresh one.

        Running gex_chart.py as a separate process re-fetched and re-derived
        everything. On 2026-08-27 the two ran 16 seconds apart, spot moved
        4.6pts, and the CFD offset shifted with it — so the brief published a
        flip of 28,966.9 and the chart drew 28,972.0, and every level on the
        chart sat 5.1pts off its counterpart in the brief. Two files delivered
        as one scan have to come from one computation.
        """
        try:
            import gex_chart
            i = sys.argv.index("--chart")
            out = (sys.argv[i + 1] if len(sys.argv) > i + 1
                   and not sys.argv[i + 1].startswith("--") else "/tmp/nas100-gex.svg")
            c = gex_chart.collect(d=d, book="week")
            gex_chart.render(c, out)
            gex_chart.persist(c)
            print(f"\n_[chart: {out}]_", file=sys.stderr)
            return out
        except Exception as e:
            print(f"\n_[chart FAILED: {type(e).__name__}: {e}]_", file=sys.stderr)
            return None

    if "--levels" in sys.argv:
        if "--chart" in sys.argv:
            _chart()
        print(markdown_levels_only(d)); sys.exit(0)
    if "--json" in sys.argv:
        d["level_board"], d["level_board_far"] = level_board(d)
        print(json.dumps(d, indent=2, default=str))
    else:
        text = markdown(d)
        print(text)
        # Journal AFTER rendering, and never let a write failure break output.
        d.setdefault("level_board", level_board(d)[0])
        res = journal.write(d, text)
        if isinstance(res, dict):
            print(f"\n_[journal write failed: {res['_error']}]_", file=sys.stderr)
        if "--chart" in sys.argv:
            _chart()
