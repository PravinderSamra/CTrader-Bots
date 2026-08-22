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

# expected cumulative share of the day's range consumed, by UTC hour,
# for the NAS100 CFD session (21:00 roll). Doc 06 section 2a.
_CONSUMED_BY_HOUR = {
    21: .02, 22: .04, 23: .06, 0: .08, 1: .10, 2: .12, 3: .14, 4: .16,
    5: .18, 6: .20, 7: .25, 8: .30, 9: .34, 10: .38, 11: .42, 12: .45,
    13: .50, 14: .66, 15: .78, 16: .85, 17: .89, 18: .92, 19: .96, 20: 1.0,
}


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
        if px > gf:
            add("gamma", +2, f"above flip {gf} by {round(px-gf,1)}pts — long-gamma, "
                             f"dips supported, upside grinds")
        else:
            add("gamma", -3, f"below flip {gf} by {round(gf-px,1)}pts — SHORT gamma, "
                             f"dealers amplify: downside accelerates, rallies unstable")
        if abs(dist_pct) < 0.15:
            add("gamma", +1 if px > gf else +1,
                "but price is straddling the flip (<0.15%) — regime unstable, "
                "reduce conviction")
    if net is not None:
        add("gamma", -2 if net < -0.2 else (+2 if net > 0.2 else 0),
            f"week net GEX {net} $bn/1% -> "
            f"{'expansion likely' if net < 0 else 'pinning likely'}")

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
    hour = datetime.now(timezone.utc).hour
    exp = _CONSUMED_BY_HOUR.get(hour, 0.5) * 100
    ratio = round(used / exp, 2) if exp else None
    add("fuel", 0, f"ADR14 {adr}, {used}% used vs ~{round(exp)}% normal by "
                   f"{hour:02d}:00 UTC -> fuel_ratio {ratio} "
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
