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

import macro_probe, levels_fuel, gex_levels, bias_engine


def gather():
    lv = levels_fuel.run()
    if "error" in lv:
        return {"error": "cTrader unavailable", "detail": lv}
    mc = macro_probe.run()
    gx = gex_levels.build(lv["price"])
    bs = bias_engine.score(mc, lv, gx)
    return {"levels": lv, "macro": mc, "gex": gx, "bias": bs}


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
         "Prior-day high — densest stop cluster above. Sweep + 1m LH + CISD = short (S1)")
    push("PDL", L.get("PDL"), "liquidity",
         "Prior-day low — densest stop cluster below. Sweep + 1m HL + CISD = long (S1)")
    push("PD mid", L.get("PD_mid"), "magnet",
         "Prior-day equilibrium — a TARGET, not a trigger. Magnet on rangebound days")
    push("PD close", L.get("PD_close"), "magnet", "Settlement reference / gap-fill magnet")
    # PWH/PWL flip role when price displaces outside the prior week entirely —
    # calling PWL "support" while trading below it would be actively misleading.
    pwh, pwl = L.get("PWH"), L.get("PWL")
    if pwh and pwl and px < pwl:
        push("PWL", pwl, "liquidity",
             "Prior-week LOW, but price is below the whole prior week — this is now "
             "RESISTANCE. Trade it as an S1 short-sweep level, not a long-sweep level")
        push("PWH", pwh, "context", "Prior-week high — far overhead, context only")
    elif pwh and pwl and px > pwh:
        push("PWH", pwh, "liquidity",
             "Prior-week HIGH, but price is above the whole prior week — this is now "
             "SUPPORT. Trade it as an S1 long-sweep level")
        push("PWL", pwl, "context", "Prior-week low — far below, context only")
    else:
        push("PWH", pwh, "liquidity", "Prior-week high — big pool, best Mon-Tue")
        push("PWL", pwl, "liquidity", "Prior-week low — big pool, best Mon-Tue")
    for tag, label in (("sessions_prev_day", "prev-day"), ("sessions_today", "today")):
        for sess, v in (L.get(tag) or {}).items():
            push(f"{sess.upper() if sess in ('ny',) else sess.title()} High ({label})", v["high"], "liquidity",
                 f"{sess.upper() if sess in ('ny',) else sess.title()} session high — the next session routinely sweeps it")
            push(f"{sess.upper() if sess in ('ny',) else sess.title()} Low ({label})", v["low"], "liquidity",
                 f"{sess.upper() if sess in ('ny',) else sess.title()} session low — the next session routinely sweeps it")
    for p in lv["unmitigated_pools_above"] + lv["unmitigated_pools_below"]:
        q = "CONFIRMED pool" if p["confirmed"] else "single-touch (context only)"
        push(f"Unmitigated {'high' if p['price'] > px else 'low'}", p["price"],
             "liquidity" if p["confirmed"] else "context",
             f"{q}, {p['touches']} touch(es) — untouched liquidity still resting")

    gf = gx["gamma_flip"]
    push("GAMMA FLIP", gf.get("nas100"), "gamma",
         "THE volatility switch. Above = long gamma, dealers fade moves (S1 works). "
         "Below = short gamma, dealers amplify (S2 works). Not S/R — a regime line")
    if wk.get("call_wall"):
        push("CALL WALL", wk["call_wall"]["nas100"], "gamma",
             f"Largest call gamma above ({wk['call_wall']['oi']:,} OI). Magnetic ceiling — "
             f"rallies stall. Prime S1 short-sweep level. A HELD break above flips it to a "
             f"gamma squeeze -> S2 long")
    if wk.get("put_wall"):
        push("PUT WALL", wk["put_wall"]["nas100"], "gamma",
             f"Largest put gamma below ({wk['put_wall']['oi']:,} OI). Defended floor IN "
             f"POSITIVE GAMMA -> prime S1 long-sweep level. IN NEGATIVE GAMMA IT INVERTS: "
             f"a break is acceleration, not a bounce")
    push("MAX PAIN", gx["max_pain_week"]["nas100"], "gamma",
         "Weak magnet Mon, strong Thu/Fri. Coincident with the call wall = hard pin")
    for p in (wk.get("largest_abs_gex") or [])[:6]:
        sign = p["sign"]
        push(f"GEX shelf {sign}{abs(p['net_gex_$bn']):.2f}bn", p["nas100"], "gamma-shelf",
             ("POSITIVE shelf — expect a stall here; good place to fade / take partials"
              if sign == "+" else
              "NEGATIVE shelf — expect price to slice through; do NOT fade, good for continuation"))

    rows.sort(key=lambda r: -r["level"])
    return rows


def markdown(d):
    lv, mc, gx, bs = d["levels"], d["macro"], d["gex"], d["bias"]
    px, f = lv["price"], lv["fuel"]
    v, rf = mc["volatility"], mc["rates_fx"]
    o = []
    A = o.append
    A(f"# NAS100 Daily Brief — {lv['trading_day']}")
    A(f"_generated {lv['generated_utc']} · price **{px}** (bid {lv['bid']} / ask {lv['ask']})_\n")

    A(f"## 1. The call: **{bs['label']}**  (score {bs['score']:+d})\n")
    A(f"**{bs['strategy_call']}**\n")
    if bs.get("event_gate"):
        A(f"> ⚠️ **{bs['event_gate']}**\n")
    A("| component | pts | reasoning |")
    A("|---|---|---|")
    for r in bs["components"]:
        A(f"| {r['component']} | {r['points']:+d} | {r['why']} |")
    A("")

    A("## 2. Regime\n")
    A(f"- **Gamma:** flip at **{gx['gamma_flip']['nas100']}**, price {px} → "
      f"**{gx['gamma_flip']['spot_position']}**")
    for k, b in gx["buckets"].items():
        A(f"  - `{k}`: net GEX **{b['net_gex_$bn_per_1pct']} $bn/1%** [{b['regime']}]")
    A(f"- **Vol:** VXN {v['vxn_nasdaq_ivol'].get('last')} "
      f"({v['vxn_nasdaq_ivol'].get('chg_pct')}%) · VIX {v['vix'].get('last')} · "
      f"VIX9D/VIX {v['vix9d_over_vix']} → {v['term_read']} · VVIX {v['vvix'].get('last')}")
    A(f"- **Rates/FX:** US10y {rf['us10y'].get('last')} ({rf['us10y'].get('chg_pct')}%) · "
      f"DXY {rf['dxy'].get('last')} ({rf['dxy'].get('chg_pct')}%)")
    A(f"- **CFD/index offset:** {gx['cfd_offset']} (NDX {gx['ndx_spot']} vs CFD {px}) — "
      f"all gamma levels below are already converted to CFD price")
    A(f"- **Data freshness:** NDX chain {gx['as_of']['ndx']}, QQQ chain {gx['as_of']['qqq']}\n")

    fr = mc.get("fred") or {}
    A("### Real rates, credit & liquidity (FRED)\n")
    if fr.get("key_present"):
        for x in fr.get("read", []):
            mark = "🟢" if x["signal"] > 0 else ("🔴" if x["signal"] < 0 else "⚪")
            A(f"- {mark} {x['text']}")
        A(f"\n_{fr.get('series_ok')} series, published with a 1-2 day lag — "
          f"this is regime context, not an intraday trigger._\n")
    else:
        A("- _FRED_API_KEY not set — running on nominal yields only. "
          "The real-yield read (the most direct driver of tech multiples) "
          "is missing._\n")

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
    A(f"**Stop management:** " + {
        "ROOM_TO_EXPAND": "leave the structural stop alone; trail only on confirmed 1m structure breaks.",
        "MODERATE": "structural stop; break-even at 1R or 50% of remaining budget, whichever first.",
        "LOW_FUEL": "active management from entry — break-even at 0.7R, 50% off at the first pool, trail tight.",
        "EXHAUSTED": "do not initiate; if already in, take partials and be flat before the close.",
    }[f["expansion_state"]] + "\n")

    A("## 4. Level board — mark these\n")
    A("| NAS100 | distance | type | level | reach | what to expect |")
    A("|---|---|---|---|---|---|")
    for r in level_board(d):
        A(f"| **{r['level']}** | {r['dist']:+.1f} | {r['kind']} | {r['name']} | "
          f"{r['reach']} | {r['note']} |")
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
    d = gather()
    if "error" in d:
        print(json.dumps(d, indent=2, default=str)); sys.exit(1)
    if "--json" in sys.argv:
        d["level_board"] = level_board(d)
        print(json.dumps(d, indent=2, default=str))
    else:
        print(markdown(d))
