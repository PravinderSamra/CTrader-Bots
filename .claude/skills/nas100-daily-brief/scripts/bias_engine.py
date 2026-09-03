#!/usr/bin/env python3
"""
bias_engine.py — Phase-1 prototype: the NAS100 directional-bias score.

Deterministic, auditable, and every component prints its own contribution so a
wrong call can be traced to the input that caused it. Consumes the other three
prototypes.

Score range roughly -20..+20.  >= +6 bullish, <= -6 bearish, else neutral.
"""
import json, math, sys
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

# Expected cumulative share of the day's range consumed, keyed by **US Eastern
# hour** — not UTC. The original table was keyed by UTC hour and happened to be
# correct only during EDT: it put the big NY-open jump at 14:00 UTC, which is
# 10:00 ET in summer but 09:00 ET in winter. Keying on ET makes the curve track
# the actual session shape year-round, through both DST switches.
#
# 17:00 ET is the broker day roll / Globex reopen; 09:30 ET is the NY cash open,
# which is where roughly 45% of the day's range gets spent.
_CONSUMED_BY_ET_HOUR = {
    17: .02, 18: .04, 19: .06, 20: .08, 21: .10, 22: .12, 23: .14,
    0: .16, 1: .18, 2: .20,
    3: .25, 4: .30, 5: .34, 6: .38, 7: .42, 8: .45, 9: .50,
    10: .66, 11: .78, 12: .85, 13: .89, 14: .92, 15: .96, 16: 1.0,
}


def expected_consumed(now_utc=None):
    """-> (fraction_of_ADR_normally_spent_by_now, 'HH:MM ET') for the current
    moment, DST-resolved."""
    now = now_utc or datetime.now(timezone.utc)
    et = now.astimezone(ZoneInfo("America/New_York"))
    return _CONSUMED_BY_ET_HOUR.get(et.hour, 0.5), et.strftime("%H:%M ET")


def _pct(x):
    return None if x is None else round(x, 2)


def score(macro, levels, gex):
    """Each rule appends (component, points, reason). Points are signed:
    positive = bullish NAS100."""
    R = []
    add = lambda c, p, why: R.append({"component": c, "points": p, "why": why})

    # ---------------- 1. Dealer gamma regime (weight: highest) -------------
    gf = (gex.get("gamma_flip") or {}).get("nas100")
    px = levels["price"]
    wk = (gex.get("buckets") or {}).get("this_week") or {}
    net = wk.get("net_gex_$bn_per_1pct")
    if gf is not None:
        dist_pct = (px - gf) / px * 100
        # C3, 2026-09-03 — scored 0. Which side of the flip price sits on is a
        # VOLATILITY statement, not a directional one: short gamma means dealers
        # amplify whatever move is happening, so it forecasts a WIDER RANGE, not
        # a LOWER CLOSE. Scoring it as direction was the single largest source
        # of error in the first 8 days: gamma averaged -1.9/day and scored -5 on
        # five days of eight, while every other component averaged within +/-0.6
        # of zero. Gamma WAS the bias. It was also asymmetric (+2 above, -3
        # below), so time spent below the flip made the model structurally
        # bearish — it called bearish on 8 of 11 scans in a window where price
        # rose on 8 of 11. The regime read is real and still published here, in
        # the shape section, and in the strategy selection, which is where it
        # belongs and where it has been working.
        if px > gf:
            add("gamma", 0, f"above flip {gf} by {round(px-gf,1)}pts — long-gamma, "
                            f"dips supported, upside grinds "
                            f"(regime read — not scored: tells you the day's WIDTH, "
                            f"not its direction)")
        else:
            add("gamma", 0, f"below flip {gf} by {round(gf-px,1)}pts — SHORT gamma, "
                            f"dealers amplify: downside accelerates, rallies unstable "
                            f"(regime read — not scored: tells you the day's WIDTH, "
                            f"not its direction)")
        if abs(dist_pct) < 0.15:
            # Also 0: this only ever existed to damp the flip term's score, and
            # that score is now 0. It additionally carried a real bug — it read
            # `+1 if px > gf else +1`, adding +1 on BOTH branches, so a term
            # labelled "reduce conviction" INCREASED it above the flip (+2 -> +3).
            add("gamma", 0,
                "but price is straddling the flip (<0.15%) — regime unstable, "
                "treat the width read as low-confidence")
    if net is not None:
        # Scored 0 deliberately — this is a narrative row, not an independent
        # observation. The gamma flip IS the spot where net GEX crosses zero,
        # so "below flip" and "net GEX negative" are the same fact stated
        # twice: across every scan on record the two terms have never once
        # carried opposite signs. Scoring both let one observation supply up
        # to 5 points of a score whose typical magnitude is 4-8 (on 2026-08-31
        # gamma supplied -5 of the -7). Expansion also has no direction: a
        # short-gamma book forecasts a wider RANGE, not a lower CLOSE, so the
        # sign it was contributing was never earned. Removing it changed
        # labels on 3 of 9 graded calls and left the record a wash, which is
        # the point — it removes false conviction, not error. The regime read
        # itself is real and still published here and in the shape section.
        add("gamma", 0,
            f"week net GEX {net} $bn/1% -> "
            f"{'expansion likely' if net < 0 else 'pinning likely'} "
            f"(regime read — not scored: same fact as the flip term above)")

    # walls relative to price
    cw = (wk.get("call_wall") or {}).get("nas100")
    pw = (wk.get("put_wall") or {}).get("nas100")
    if cw and pw:
        span = cw - pw
        pos = (px - pw) / span if span else .5
        if pos > 0.8:
            add("gamma", -2, f"price sits in the top 20% of the wall band "
                             f"({pw}-{cw}) — poor risk/reward for longs")
        elif pos < 0.2:
            add("gamma", +2, f"price sits in the bottom 20% of the wall band "
                             f"({pw}-{cw}) — poor risk/reward for shorts")
        else:
            add("gamma", 0, f"price mid-band ({pw}-{cw}), {round(pos*100)}% up the range")

    # ---------------- 2. Volatility regime ---------------------------------
    v = macro["volatility"]
    vxn = (v["vxn_nasdaq_ivol"] or {}).get("last")
    vxn_chg = (v["vxn_nasdaq_ivol"] or {}).get("chg_pct")
    term = v.get("vix9d_over_vix")
    if vxn_chg is not None:
        add("vol", -2 if vxn_chg > 5 else (+2 if vxn_chg < -5 else 0),
            f"VXN {vxn} ({vxn_chg:+.1f}%) — "
            f"{'fear rising, bearish' if vxn_chg>5 else 'fear falling, bullish' if vxn_chg<-5 else 'stable'}")
    if term is not None:
        if term > 1.0:
            add("vol", -2, f"VIX9D/VIX {term} BACKWARDATED — near-term stress, "
                           f"expect range expansion, downside skew")
        elif term < 0.92:
            add("vol", +1, f"VIX9D/VIX {term} contango — calm, mean-reversion "
                           f"favoured, mild upward drift")
        else:
            add("vol", 0, f"VIX9D/VIX {term} flat")
    vixl = (v["vix"] or {}).get("last"); vvix = (v["vvix"] or {}).get("last")
    if vxn and vixl:
        ratio = round(vxn / vixl, 2)
        add("vol", -1 if ratio > 1.35 else 0,
            f"VXN/VIX {ratio} — {'tech-specific stress priced above the broad market' if ratio>1.35 else 'normal tech premium'}")
    if vvix:
        add("vol", -1 if vvix > 100 else 0,
            f"VVIX {vvix} — {'active tail hedging' if vvix>100 else 'no tail-hedge bid'}")

    # ---------------- 3. Rates / FX ----------------------------------------
    rf = macro["rates_fx"]
    y10 = rf["us10y"].get("chg_pct"); y5 = rf["us5y"].get("chg_pct")
    dxy = rf["dxy"].get("chg_pct")
    if y10 is not None:
        add("rates", -3 if y10 > 1.0 else (+3 if y10 < -1.0 else
            (-1 if y10 > 0.3 else (+1 if y10 < -0.3 else 0))),
            f"US10y {rf['us10y'].get('last')} ({y10:+.2f}%) — "
            f"{'yields up, multiple compression, BEARISH tech' if y10>0.3 else 'yields down, BULLISH tech' if y10<-0.3 else 'yields flat'}")
    if y5 is not None and y10 is not None and y5 > y10 + 0.5:
        add("rates", -1, "short end leading the sell-off — hawkish Fed repricing, "
                         "the more damaging kind for tech")
    if dxy is not None:
        add("rates", -2 if dxy > 0.4 else (+2 if dxy < -0.4 else 0),
            f"DXY {rf['dxy'].get('last')} ({dxy:+.2f}%) — "
            f"{'dollar bid, risk-off' if dxy>0.4 else 'dollar soft, risk-on' if dxy<-0.4 else 'dollar flat'}")

    # ---------------- 3b. FRED: real rates, credit, liquidity ---------------
    # Nominal yields say WHAT rates did; these say WHY, and the why is what
    # actually reprices long-duration tech. Weighted below the intraday levers
    # because FRED publishes with a 1-2 day lag — this is regime, not trigger.
    fr = macro.get("fred") or {}
    if fr.get("key_present"):
        _W = {"real_yields": 3, "yield_decomp": 1, "credit": 2,
              "fin_conditions": 1, "liquidity": 1, "curve": 1}
        for item in fr.get("read", []):
            w = _W.get(item["tag"], 1)
            sig = item["signal"]
            pts = max(-w, min(w, sig * w)) if sig else 0
            add("macro", pts, item["text"])
    else:
        add("macro", 0, "FRED layer unavailable (no FRED_API_KEY) — running "
                        "on nominal yields only, real-rate read is missing")

    # ---------------- 4. Breadth / mega-cap leadership ----------------------
    bp = macro["breadth_proxy"]
    megas = {k: bp[k].get("chg_pct") for k in ("nvda", "msft", "aapl", "avgo")
             if isinstance(bp.get(k), dict) and bp[k].get("chg_pct") is not None}
    if megas:
        avg = sum(megas.values()) / len(megas)
        up = sum(1 for x in megas.values() if x > 0)
        add("breadth", +2 if avg > 0.8 else (-2 if avg < -0.8 else 0),
            f"mega-cap avg {avg:+.2f}% ({up}/{len(megas)} up): " +
            ", ".join(f"{k.upper()} {x:+.2f}%" for k, x in megas.items()))
        nd = macro["index"]["ndx_daily"].get("chg_pct")
        # require the mega-caps to actually be DOWN, not merely below the index.
        # `nd > 0.3 > avg` fired on avg = +0.01%, which is not a divergence.
        if nd is not None and avg is not None and nd > 0.3 and avg < -0.2:
            add("breadth", -2, "index up while mega-caps are down — narrow, "
                               "tail-carried rally; these fade into the close")
    es = bp.get("es_sp500", {}).get("chg_pct")
    nd = macro["index"]["ndx_daily"].get("chg_pct")
    if es is not None and nd is not None:
        add("breadth", +1 if nd > es + 0.2 else (-1 if nd < es - 0.2 else 0),
            f"NDX {nd:+.2f}% vs ES {es:+.2f}% — "
            f"{'tech leading, genuine risk appetite' if nd>es+0.2 else 'tech lagging, rotation out of tech' if nd<es-0.2 else 'in line'}")

    # ---------------- 5. Structure / fuel ----------------------------------
    f = levels["fuel"]; lv = levels["levels"]
    used, adr = f["adr_used_pct"], f["adr14"]
    frac, et_label = expected_consumed()
    exp = frac * 100
    ratio = round(used / exp, 2) if exp else None
    add("fuel", 0, f"ADR14 {adr}, {used}% used vs ~{round(exp)}% normal by "
                   f"{et_label} -> fuel_ratio {ratio} "
                   f"({'burning hot' if ratio and ratio>1.4 else 'coiled' if ratio and ratio<0.6 else 'normal'}) "
                   f"[{f['expansion_state']}]")
    if f["expansion_state"] in ("LOW_FUEL", "EXHAUSTED"):
        add("fuel", 0, "fuel is short — this dampens CONVICTION in any "
                       "continuation call, it does not change direction")
    if lv.get("PD_close") and lv.get("PD_mid"):
        add("structure", +1 if px > lv["PD_mid"] else -1,
            f"price {'above' if px>lv['PD_mid'] else 'below'} PD mid {lv['PD_mid']} "
            f"(PDH {lv['PDH']} / PDL {lv['PDL']})")
    # Whole-of-prior-week displacement is one of the strongest structural
    # reads there is, and it is easy to miss by eye: if price is trading
    # entirely outside last week's range, the weekly draw has already flipped.
    pwh, pwl = lv.get("PWH"), lv.get("PWL")
    if pwh and pwl:
        if px < pwl:
            add("structure", -3, f"price is BELOW the entire prior-week range "
                                 f"({pwl}-{pwh}) — weekly draw has flipped bearish; "
                                 f"PWL {pwl} is now resistance, not support")
        elif px > pwh:
            add("structure", +3, f"price is ABOVE the entire prior-week range "
                                 f"({pwl}-{pwh}) — weekly draw has flipped bullish; "
                                 f"PWH {pwh} is now support, not resistance")
        else:
            add("structure", 0, f"price inside the prior-week range ({pwl}-{pwh})")

    ab = levels.get("unmitigated_pools_above") or []
    be = levels.get("unmitigated_pools_below") or []
    n_ab = sum(1 for p in ab if p.get("reach") == "intraday")
    n_be = sum(1 for p in be if p.get("reach") == "intraday")
    add("structure", +1 if n_ab > n_be else (-1 if n_be > n_ab else 0),
        f"in-reach unmitigated pools: {n_ab} above / {n_be} below — "
        f"draw {'higher' if n_ab>n_be else 'lower' if n_be>n_ab else 'balanced'}")

    # ---------------- 5b. News (HIGH-confidence items only) -----------------
    # Only headlines the pre-filter could classify unambiguously vote here.
    # Everything else is surfaced for the model to read in context — see
    # research/09-news-sentiment-replacement.md for why keyword scoring alone
    # is not trustworthy enough to move a number.
    ns = macro.get("news_scored") or {}
    if "_error" not in ns:
        pts = ns.get("bias_points", 0)
        c = ns.get("counts", {})
        add("news", pts,
            f"{ns.get('scored_high_confidence', 0)} auto-scored headline(s) "
            f"({c.get('bullish', 0)} bull / {c.get('bearish', 0)} bear) -> "
            f"{ns.get('label')}; {ns.get('needs_model_judgement', 0)} more need "
            f"reading in context (not counted here)")
        for it in (ns.get("high_confidence") or [])[:3]:
            add("news", 0, f"  \u2022 [{it['rule']}] {it['title'][:88]}")

    # ---------------- 6. Events (gate, not direction) -----------------------
    cal = macro["calendar"]
    soon = [e for e in (cal.get("upcoming_next_24h") or []) if 0 <= e["hours_away"] <= 1.5]
    hi = [e for e in soon if e["impact"] == "High"]
    gate = None
    if hi:
        gate = (f"STAND ASIDE — {hi[0]['title']} in {hi[0]['hours_away']}h. "
                f"No entries until 30min after the print; then use the "
                f"post-print 30-min range H/L as the day's sweep levels.")
    earn = cal.get("heavyweight_earnings_next_5d") or []
    for e in earn:
        add("events", 0, f"{e['symbol']} earnings {e['date']} {e.get('when','')} "
                         f"(cons {e.get('eps_forecast')}) — "
                         f"{'INDEX-DEFINING event; day before pins, day after expands' if e['symbol']=='NVDA' else 'sector-relevant'}")

    total = sum(r["points"] for r in R)
    label = ("STRONGLY BULLISH" if total >= 10 else "BULLISH" if total >= 6 else
             "MILDLY BULLISH" if total >= 3 else
             "STRONGLY BEARISH" if total <= -10 else "BEARISH" if total <= -6 else
             "MILDLY BEARISH" if total <= -3 else "NEUTRAL / TWO-WAY")

    # strategy selection (doc 05)
    if gf and px > gf and (net or 0) > 0:
        strat = ("STRATEGY 1 — sweep -> failed re-break -> CISD reversal. "
                 "Positive gamma above the flip: dealers fade extensions, so "
                 "sweeps genuinely fail. Trade the walls and the day-frame levels.")
    elif gf and px < gf:
        strat = ("STRATEGY 2 — CISD -> HH/HL -> fib OTE continuation. "
                 "Below the flip in negative gamma: dealers amplify, sweeps run "
                 "rather than fail. Strategy-1 fades have a materially lower hit "
                 "rate here — only take them at the far walls.")
    else:
        strat = "Straddling the flip — reduce size and let the regime resolve."

    return {"score": total, "label": label, "components": R,
            "event_gate": gate, "strategy_call": strat,
            "fuel_ratio": ratio}


if __name__ == "__main__":
    import macro_probe, levels_fuel, gex_levels
    m = macro_probe.run()
    l = levels_fuel.run()
    g = gex_levels.build(l["price"])
    out = score(m, l, g)
    if "--json" in sys.argv:
        print(json.dumps(out, indent=2, default=str)); sys.exit(0)
    print(f"BIAS {out['score']:+d}  ->  {out['label']}\n")
    for r in out["components"]:
        print(f"  [{r['component']:9}] {r['points']:+d}  {r['why']}")
    print(f"\nSTRATEGY: {out['strategy_call']}")
    if out["event_gate"]:
        print(f"\n!! {out['event_gate']}")
