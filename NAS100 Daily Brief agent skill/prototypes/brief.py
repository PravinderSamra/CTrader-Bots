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
    if wk.get("call_wall"):
        push("CALL WALL", wk["call_wall"]["nas100"], "gamma",
             f"The heaviest ceiling on the board — desks have to SELL as price "
             f"rises into it, so rallies stall here. Take profit into it. If "
             f"price closes above and holds, that selling flips to buying and "
             f"it becomes a launchpad instead ({wk['call_wall']['oi']:,} contracts)")
    if wk.get("put_wall"):
        push("PUT WALL", wk["put_wall"]["nas100"], "gamma",
             (f"The heaviest floor on the board — expect a bounce and a good "
              f"long-sweep here ({wk['put_wall']['oi']:,} contracts)"
              if long_gamma else
              f"Heaviest floor on the board, BUT today the desks are pushing "
              f"moves along — so if this breaks, expect it to speed UP, not "
              f"bounce. Don't buy the break ({wk['put_wall']['oi']:,} contracts)"))
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
            rank = {"gamma": 4, "liquidity": 3, "gamma-shelf": 2, "magnet": 1, "context": 0}
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
        core = any(c in r["name"] for c in CORE)
        return core and abs(r["dist"]) <= budget * 1.75
    board = [r for r in merged if keep(r)]
    far = [r for r in merged if not keep(r)]
    for r in board:
        r["stretch"] = r["reach"] != "intraday"
    return board, far


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

    A("<details><summary>Full options numbers and data ages</summary>\n")
    for k, b in gx["buckets"].items():
        A(f"- `{k}`: net GEX **{b['net_gex_$bn_per_1pct']} $bn per 1% move** "
          f"[{b['regime']}]")
    A(f"- CFD/index offset **{gx['cfd_offset']}** (NDX {gx['ndx_spot']} vs CFD {px}) "
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
    A(f"**Stop management:** " + {
        "ROOM_TO_EXPAND": "leave the structural stop alone; trail only on confirmed 1m structure breaks.",
        "MODERATE": "structural stop; break-even at 1R or 50% of remaining budget, whichever first.",
        "LOW_FUEL": "active management from entry — break-even at 0.7R, 50% off at the first pool, trail tight.",
        "EXHAUSTED": "do not initiate; if already in, take partials and be flat before the close.",
    }[f["expansion_state"]] + "\n")

    A("## 4. Level board — mark these\n")
    board, far = level_board(d)
    A(f"_Same price = one line, so a level named twice is two reasons to "
      f"respect it (⭐). Today's remaining range budget is "
      f"**{f['remaining_budget']:.0f}pts** — anything marked _(stretch)_ is "
      f"beyond that, so treat it as partials-only._\n")
    A("| NAS100 | dist | level | what to expect |")
    A("|---|---|---|---|")
    for r in board:
        star = " ⭐" if r.get("confluence", 1) > 1 else ""
        tag = " _(stretch)_" if r.get("stretch") else ""
        dist = f"{r['dist']:+.0f}" if abs(r["dist"]) >= 1.0 else "at price"
        A(f"| **{r['level']}** | {dist} | {r['name']}{star}{tag} | {r['note']} |")
    A("")
    if far:
        A("_Beyond today's range (context only, don't mark): "
          + " · ".join(f"{r['level']:.0f} {r['name']}" for r in far[:6]) + "_\n")

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
        d["level_board"], d["level_board_far"] = level_board(d)
        print(json.dumps(d, indent=2, default=str))
    else:
        print(markdown(d))
