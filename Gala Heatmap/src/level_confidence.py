#!/usr/bin/env python3
"""
LEVEL CONFIDENCE — score a level you're about to trade, from every layer at once.

You give it the level(s) you marked. It answers, for each: how confident should
you be that this holds, which direction does the evidence favour, where does the
stop go, and what is the realistic R.

It combines:
  1. This level's own history          (level_stats — measured)
  2. Real COMEX volume profile         (gold_context — measured)
  3. Options open interest by strike   (CBOE — measured)
  4. Dealer gamma regime               (CBOE — measured)
  5. CFTC positioning                  (measured)
  6. Session performance at this level (measured)

--as-of: the honesty switch
---------------------------
`--as-of 2026-07-31T15:30:00Z` truncates EVERY price series to that instant, so
the output is exactly what could have been said at that moment. Without it, a
"how would this have gone" answer is worthless — the level's own statistics would
include the very touches you are asking about.

One layer cannot be reconstructed: **the options chain**. CBOE publishes the
current book only; there is no free historical chain. So under --as-of, gamma and
OI are reported as UNAVAILABLE unless a journal entry snapshotted them at the
time. That is the single strongest argument for the journal — it is the only way
the gamma hypothesis will ever become testable.

About the score
---------------
The *inputs* are measured. The *weights* combining them are a judgement call and
are not yet validated — nothing has calibrated them. They are printed as an
itemised breakdown, never as a bare number, so you can see what drove it and
disagree. `journal_review.py` is what will eventually calibrate them against your
own logged outcomes.

Usage
-----
    python3 level_confidence.py --level 4049.44
    python3 level_confidence.py --level 4049.44 --level 4103.00 --direction short
    python3 level_confidence.py --level 4049.44 --as-of 2026-07-31T15:30:00Z
    python3 level_confidence.py --level 4049.44 --journal      # append to trade-journal/
"""

from __future__ import annotations

import argparse
import json
import os
import statistics as stats
import sys
from dataclasses import asdict
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ctrader_http import CTraderClient, CTraderError, iso, now_ms  # noqa: E402
from level_stats import (find_touch_events, derive_stop_distance, replay,  # noqa: E402
                         replay_rejection, independent_counts,
                         summarise, _pct, resolve_symbol)
from pivots import find_pivots  # noqa: E402
import gold_context as gc  # noqa: E402

DAY_MS = 86_400_000
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def parse_ts(s: str | None) -> int | None:
    if not s:
        return None
    s = s.strip().replace("Z", "+00:00")
    return int(datetime.fromisoformat(s).timestamp() * 1000)


# ------------------------------------------------------------------- scoring

def score_level(level: float, direction: str, hist: dict, ctx: dict,
                spot: float) -> dict:
    """Combine the layers into a score with an itemised, inspectable breakdown.

    direction: "short" (fading a resistance test) or "long" (fading a support test)
    """
    items: list[tuple[str, float, str]] = []   # (label, points, detail)
    side = "resistance" if direction == "short" else "support"

    # ---- 1. Base: this level's measured behaviour in this exact setup ------
    bucket = hist.get("bucket") or {}
    n = bucket.get("n", 0)
    if n:
        exp = bucket["expectancy_r"]
        base = max(0.0, min(60.0, (exp + 1.0) / 4.0 * 60.0))
        # Sample weight keys off DISTINCT DAYS, not raw events. Touch events
        # within a day are dominated by that day's regime, so 23 events across
        # 4 days is 4 observations wearing a big number. Weighting on the raw
        # count handed full confidence to a 4-day sample.
        nd = bucket.get("n_days", 0)
        nv = bucket.get("n_visits", 0)
        if nd >= 12:
            adeq, adeq_lbl = 1.00, "12+ days"
        elif nd >= 8:
            adeq, adeq_lbl = 0.80, "8–11 days"
        elif nd >= 5:
            adeq, adeq_lbl = 0.60, "5–7 days"
        elif nd >= 3:
            adeq, adeq_lbl = 0.40, "3–4 days"
        else:
            adeq, adeq_lbl = 0.20, "<3 days"
        base *= adeq
        trg = bucket.get("n_triggered", n)
        items.append((f"Level history ({side}, {hist['bias']} day)", base,
                      f"**{nd} distinct days** / {nv} visits / {n} events"
                      f"{f', {trg} triggered' if trg != n else ''} · "
                      f"held {bucket['hold_rate']*100:.0f}%, expectancy {exp:+.2f}R · "
                      f"sample weight {adeq:.2f} ({adeq_lbl})"))
        if bucket["hold_rate"] < 0.5:
            items.append(("Breaks more than it holds", -15.0,
                          f"held only {bucket['hold_rate']*100:.0f}% — favour break-and-retest"))
    else:
        items.append((f"Level history ({side}, {hist['bias']} day)", 0.0,
                      "NO SAMPLES for this setup at this level — no base to score from"))

    # ---- 1b. Robustness: does the edge survive other stop widths? ----------
    rb = hist.get("robustness") or []
    if len(rb) >= 5:
        pos = sum(1 for r in rb if r["expectancy_r"] > 0)
        frac = pos / len(rb)
        if frac >= 0.85:
            items.append(("Edge robustness", 8.0,
                          f"expectancy positive at {pos}/{len(rb)} stop widths "
                          f"({rb[0]['stop']:.1f}–{rb[-1]['stop']:.1f} pts) — not a single-stop artefact"))
        elif frac <= 0.4:
            items.append(("Edge robustness", -10.0,
                          f"expectancy positive at only {pos}/{len(rb)} stop widths — "
                          f"the edge is fragile to stop placement"))
        else:
            items.append(("Edge robustness", 0.0,
                          f"expectancy positive at {pos}/{len(rb)} stop widths — mixed"))

    # ---- 2. Gamma regime ---------------------------------------------------
    gex = ctx.get("net_gex")
    if gex is None:
        items.append(("Dealer gamma regime", 0.0,
                      "UNAVAILABLE — options chain cannot be reconstructed historically"))
    elif gex > 0:
        items.append(("Dealer gamma regime", 10.0,
                      f"net GEX {gex/1e6:+.1f}M — dealers hedge against moves → pinning "
                      f"regime, favours fading the level"))
    else:
        items.append(("Dealer gamma regime", -8.0,
                      f"net GEX {gex/1e6:+.1f}M — dealers hedge with moves → trending "
                      f"regime, levels break more easily"))

    # ---- 3. Volume node confluence ----------------------------------------
    node = ctx.get("nearest_node")
    if node:
        d = abs(node["price"] - level)
        if d <= 8:
            pts = 8.0 if node["kind"] in ("POC", "HVN") else 3.0
            items.append(("Volume node confluence", pts,
                          f"{node['kind']} at {node['price']:,.2f} ({node['price']-level:+.1f}) "
                          f"— real COMEX volume transacted here"))
        else:
            items.append(("Volume node confluence", 0.0,
                          f"nearest node {node['kind']} at {node['price']:,.2f} "
                          f"({node['price']-level:+.1f}) — too far to count"))
    else:
        items.append(("Volume node confluence", 0.0, "no volume profile available"))

    # ---- 4. Options open interest -----------------------------------------
    oi = ctx.get("nearest_oi")
    # Tolerance is set by how precisely a GLD strike can be mapped to spot, not
    # by a round number. Measured 1-sigma is ~8 points; 2-sigma is the honest
    # "this strike could be here" band. Claiming tighter would be false precision.
    unc = ctx.get("spot_uncertainty") or 7.7
    oi_tol = max(10.0, 2 * unc)
    if oi is None:
        items.append(("Options OI confluence", 0.0, "UNAVAILABLE at this timestamp"))
    elif abs(oi["spot"] - level) <= oi_tol:
        items.append(("Options OI confluence", 7.0,
                      f"{oi['total_oi']:,.0f} contracts at {oi['spot']:,.2f} ±{unc:.1f} "
                      f"({oi['spot']-level:+.1f}) — committed size within the "
                      f"±{oi_tol:.0f}pt mapping tolerance"))
    else:
        items.append(("Options OI confluence", 0.0,
                      f"nearest significant OI {oi['spot']:,.2f} ({oi['spot']-level:+.1f}) — "
                      f"outside the ±{oi_tol:.0f}pt tolerance"))

    # ---- 5. Gamma flip side ------------------------------------------------
    flip = ctx.get("gamma_flip")
    if flip and gex is not None:
        below = spot < flip
        if (direction == "short" and below) or (direction == "long" and not below):
            items.append(("Gamma flip position", 5.0,
                          f"flip {flip:,.2f}, price {'below' if below else 'above'} it — "
                          f"consistent with a {direction}"))
        else:
            items.append(("Gamma flip position", -3.0,
                          f"flip {flip:,.2f}, price {'below' if below else 'above'} it — "
                          f"leans against a {direction}"))

    # ---- 6. Session ---------------------------------------------------------
    sess = hist.get("session_bucket") or {}
    if sess.get("n", 0) >= 4:
        if sess["expectancy_r"] > 0.5:
            items.append((f"Session ({hist['session']})", 5.0,
                          f"n={sess['n']}, expectancy {sess['expectancy_r']:+.2f}R at this level"))
        elif sess["expectancy_r"] < 0:
            items.append((f"Session ({hist['session']})", -5.0,
                          f"n={sess['n']}, expectancy {sess['expectancy_r']:+.2f}R — "
                          f"this level has not worked in this session"))
        else:
            items.append((f"Session ({hist['session']})", 0.0,
                          f"n={sess['n']}, expectancy {sess['expectancy_r']:+.2f}R — neutral"))

    # ---- 7. COT -------------------------------------------------------------
    cot = ctx.get("cot")
    if cot:
        mm_net = cot["mm_long"] - cot["mm_short"]
        ratio = cot["mm_long"] / max(1, cot["mm_short"])
        if ratio > 6 and direction == "short":
            items.append(("Positioning (COT)", 5.0,
                          f"managed money {mm_net:+,} long/short {ratio:.1f}× — crowded long, "
                          f"fuel below"))
        elif ratio > 6 and direction == "long":
            items.append(("Positioning (COT)", -3.0,
                          f"managed money crowded long ({ratio:.1f}×) — less fuel for upside"))
        else:
            items.append(("Positioning (COT)", 0.0, f"managed money {mm_net:+,}, "
                                                    f"long/short {ratio:.1f}× — not extreme"))

    total = sum(p for _, p, _ in items)
    total = max(0.0, min(100.0, total))

    if total >= 70:
        verdict, note = "TAKE", "Evidence supports the trade at normal size."
    elif total >= 50:
        verdict, note = "CAUTION", "Playable at reduced size, or wait for a cleaner trigger."
    elif total >= 30:
        verdict, note = "WEAK", "Not enough behind it. Skip unless price action is exceptional."
    else:
        verdict, note = "SKIP", "The evidence does not support this trade."

    if n < 4:
        note += " NOTE: thin history at this level — the base is barely supported."
    if gex is None:
        note += " Gamma layer missing, so the ceiling here is ~85."

    return {"score": round(total, 1), "verdict": verdict, "note": note, "items": items}


# --------------------------------------------------------------------- gather

def gather(symbol: str, levels: list[float], direction: str | None,
           as_of_ms: int | None, days: int, quiet: bool = False,
           entry_model: str = "rejection", stop_floor: float | None = None,
           spread: float = 0.35, vp_interval: str = "5m",
           vp_range: str = "30d") -> dict:
    log = (lambda *a: None) if quiet else (lambda *a: print(*a, file=sys.stderr))
    cli = CTraderClient()
    sym_id, sym_name = resolve_symbol(cli, symbol)

    end = as_of_ms or now_ms()
    start = end - days * DAY_MS
    log(f"[1/5] {sym_name} · window {iso(start)} → {iso(end)}"
        f"{'  (AS-OF replay)' if as_of_ms else ''}")

    h1 = cli.trendbars(sym_id, "H_1", start, end)
    m1 = cli.trendbars(sym_id, "M_1", start, end)
    if as_of_ms:                      # belt and braces — never see past the cutoff
        h1 = [b for b in h1 if b["ts"] < as_of_ms]
        m1 = [b for b in m1 if b["ts"] < as_of_ms]
    if len(m1) < 300:
        raise CTraderError(f"only {len(m1)} M1 bars before the cutoff — widen --days")
    log(f"[2/5] {len(h1)} H1 · {len(m1)} M1 bars")

    spot = m1[-1]["c"]
    if not as_of_ms:
        sp = cli.spot([sym_id])
        q = (sp.get("prices") or sp.get("spotPrices") or [{}])[0]
        mid = ((q.get("bid", 0) + q.get("ask", 0)) / 2) / 1e5
        spot = mid or spot

    # Day bias at the cutoff, using that day's opening print.
    day_opens: dict[str, float] = {}
    for b in m1:
        k = datetime.fromtimestamp(b["ts"] / 1000, tz=timezone.utc).strftime("%Y-%m-%d")
        day_opens.setdefault(k, b["o"])
    today = datetime.fromtimestamp(m1[-1]["ts"] / 1000, tz=timezone.utc).strftime("%Y-%m-%d")
    d_open = day_opens.get(today, spot)
    move = (spot - d_open) / d_open if d_open else 0
    bias = "bullish" if move > 0.0008 else "bearish" if move < -0.0008 else "flat"
    hour = datetime.fromtimestamp(m1[-1]["ts"] / 1000, tz=timezone.utc).hour
    session = "asia" if hour < 7 else "london" if hour < 12 else "us" if hour < 17 else "late"
    log(f"[3/5] spot {spot:,.2f} · day open {d_open:,.2f} ({move*100:+.2f}%) "
        f"→ {bias} day · {session} session")

    band = spot * 0.00035
    brk = spot * 0.00025

    per_level = []
    for lv in levels:
        evs = find_touch_events(m1, lv, band, break_buffer=brk, day_opens=day_opens)
        dirn = direction or ("short" if lv >= spot else "long")
        side = "resistance" if dirn == "short" else "support"
        bucket = [e for e in evs if e.side == side and e.day_bias == bias]
        sess_b = [e for e in evs if e.side == side and e.session == session]

        # Derive the stop from the SETUP bucket, not from all touches — the
        # all-touches p90 is diluted by trivial chop visits and comes out
        # unusably tight. Then replay with THAT stop, so the expectancy you are
        # shown is the expectancy of the trade you are actually being handed.
        pierces = ([e.pierce for e in bucket if not e.broke]
                   or [e.pierce for e in evs if not e.broke])
        stop_dist = (max(band, min(band * 6, _pct(pierces, 0.90))) if pierces
                     else derive_stop_distance(evs, band, band * 6) if evs else band)
        # The rejection model needs a floor, and the wick rule does not supply a
        # usable one — measured, an unfloored wick stop returns -0.33R against
        # +0.52R at a 5-point floor. Default to a fraction of spot rather than a
        # magic number so it travels across instruments.
        floor = stop_floor if stop_floor is not None else spot * 0.00125
        # Stop-sensitivity sweep. A single stop distance can land on an unlucky
        # spot purely by sample noise, so check whether the edge survives across
        # a range of plausible stops. An edge that only exists at one stop width
        # is not an edge.
        robustness = []
        if bucket:
            for mult in (0.6, 0.8, 1.0, 1.3, 1.7, 2.2, 3.0):
                if entry_model == "rejection":
                    sd = max(band * 0.5, floor * mult)
                    replay_rejection(evs, m1, lv, stop_floor=sd, spread=spread,
                                     horizon=60, target_r=3.0)
                else:
                    sd = max(band * 0.5, stop_dist * mult)
                    replay(evs, m1, sd, 60, 3.0)
                b2 = [e for e in evs if e.side == side and e.day_bias == bias
                      and e.triggered]
                if not b2:
                    continue
                robustness.append({
                    "stop": round(sd, 2),
                    "win_rate": sum(1 for e in b2 if e.r_outcome > 0) / len(b2),
                    "expectancy_r": stats.mean(e.r_outcome for e in b2),
                })
        if evs:
            if entry_model == "rejection":
                replay_rejection(evs, m1, lv, stop_floor=floor, spread=spread,
                                 horizon=60, target_r=3.0)
            else:
                replay(evs, m1, stop_dist, 60, 3.0)   # restore the reported stop
        per_level.append({
            "robustness": robustness,
            "entry_model": entry_model, "stop_floor": floor, "spread": spread,
            "level": lv, "direction": dirn, "side": side,
            "events": evs, "stop_dist": stop_dist,
            "hist": {
                "bias": bias, "session": session, "robustness": robustness,
                "all": summarise(evs),
                # Re-summarised AFTER the replay so these reflect the stop above.
                "bucket": summarise(bucket) if bucket else {},
                "session_bucket": summarise(sess_b) if sess_b else {},
                "pivots_near": len([p for p in find_pivots(h1, 3)
                                    if abs(p.price - lv) <= lv * 0.0006]),
            },
        })

    # ---- context layers ----------------------------------------------------
    ctx: dict = {"as_of_replay": bool(as_of_ms)}
    log("[4/5] futures volume profile…")
    try:
        fut = gc.yahoo_ohlcv("GC=F", "3mo" if days > 30 else "1mo", "1h")
        if as_of_ms:
            fut = [b for b in fut if b["ts"] < as_of_ms]
        basis = gc.compute_basis(fut, h1)      # basis needs hourly vs XAUUSD H1
        try:                                    # profile wants the finest bars
            fine = gc.yahoo_ohlcv("GC=F", vp_range, vp_interval)
            if as_of_ms:
                fine = [b for b in fine if b["ts"] < as_of_ms]
            if len(fine) < 200:
                fine = fut
        except Exception:
            fine = fut
        vp = gc.volume_profile(gc.futures_to_spot(fine, basis), 120)
        ctx["basis"] = basis["current"]
        ctx["basis_stdev"] = basis["stdev_recent"]
        ctx["roll"] = basis["roll"]
        ctx["vp"] = vp
        ctx["vp_bars"] = vp.get("n_bars", 0)
        ctx["vp_interval"] = vp_interval if len(vp.get("hist", [])) else "1h"
        log(f"      basis {basis['current']:+.2f} · POC {vp['poc']:,.2f} spot "
            f"· {vp.get('n_bars', 0):,} volume bars")
    except Exception as e:
        log(f"      volume profile unavailable: {str(e)[:100]}")

    if as_of_ms:
        log("[5/5] options chain: SKIPPED — no free historical chain exists")
        ctx["options_note"] = ("Options/gamma cannot be reconstructed for a past "
                               "timestamp. CBOE serves the current book only.")
    else:
        log("[5/5] options chain + COT…")
        try:
            etf = gc.yahoo_ohlcv("GLD", "1mo", "1h")
            cal = gc.calibrate_ratio(etf, h1)
            chain = gc.cboe_chain("GLD")
            opts = gc.options_levels(chain, cal["ratio"], root="GLD")
            ctx["net_gex"] = opts["net_gex"]
            ctx["gamma_flip"] = opts["gamma_flip"]
            ctx["ratio"] = cal["ratio"]
            ctx["spot_uncertainty"] = cal.get("spot_uncertainty")
            ctx["ratio_stdev"] = cal.get("ratio_stdev")
            ctx["opt_rows"] = opts["rows"]
            ctx["expiries"] = opts["expiries"]
            flip_s = f"{opts['gamma_flip']:,.2f}" if opts.get("gamma_flip") else "n/a"
            log(f"      net GEX {opts['net_gex']/1e6:+.1f}M · flip {flip_s}")
        except Exception as e:
            log(f"      options unavailable: {str(e)[:100]}")

    try:
        cot = gc.cftc_gold(4)
        if as_of_ms:
            cutoff = datetime.fromtimestamp(as_of_ms / 1000, tz=timezone.utc).strftime("%Y-%m-%d")
            cot = [c for c in cot if c["date"] <= cutoff]
        ctx["cot"] = cot[0] if cot else None
    except Exception:
        ctx["cot"] = None

    # per-level context resolution
    for pl in per_level:
        lv = pl["level"]
        if ctx.get("vp"):
            vp = ctx["vp"]
            cands = [{"price": vp["poc"], "kind": "POC"}] + \
                    [{"price": p, "kind": "HVN"} for p, _ in vp["hvn"]] + \
                    [{"price": p, "kind": "LVN"} for p, _ in vp["lvn"]]
            pl_node = min(cands, key=lambda c: abs(c["price"] - lv))
        else:
            pl_node = None
        if ctx.get("opt_rows"):
            rows = ctx["opt_rows"]
            cut = sorted((r["total_oi"] for r in rows), reverse=True)
            cut = cut[max(0, len(cut) // 4)] if cut else 0
            big = [r for r in rows if r["total_oi"] >= cut]
            pl_oi = min(big, key=lambda r: abs(r["spot"] - lv)) if big else None
        else:
            pl_oi = None
        lctx = {**ctx, "nearest_node": pl_node, "nearest_oi": pl_oi}
        pl["ctx"] = lctx
        pl["score"] = score_level(lv, pl["direction"], pl["hist"], lctx, spot)

    return {"symbol": sym_name, "symbol_id": sym_id, "spot": spot, "bias": bias,
            "session": session, "day_open": d_open, "as_of": end,
            "as_of_replay": bool(as_of_ms), "ctx": ctx, "levels": per_level,
            "days": days}


# ---------------------------------------------------------------------- report

def render(res: dict) -> str:
    L: list[str] = []
    a = L.append
    a(f"# Level Confidence — {res['symbol']}")
    a("")
    stamp = iso(res["as_of"])
    a(f"{'**AS-OF REPLAY** — ' if res['as_of_replay'] else ''}{stamp} UTC · "
      f"spot {res['spot']:,.2f} · day open {res['day_open']:,.2f} · "
      f"**{res['bias']} day** · {res['session']} session")
    a("")
    if res["as_of_replay"]:
        a("> Every price series is truncated to this instant. Nothing below uses data")
        a("> that did not exist at the time.")
        if res["ctx"].get("options_note"):
            a("> ")
            a(f"> ⚠️ {res['ctx']['options_note']}")
        a("")

    c = res["ctx"]
    a("## Market context")
    a("")
    if c.get("basis") is not None:
        a(f"- GC basis {c['basis']:+.2f} pts" +
          (f" · **roll detected {c['roll']['date']}** ({c['roll']['jump']:+.1f})" if c.get("roll") else ""))
    if c.get("vp"):
        vp = c["vp"]
        a(f"- Volume profile (spot terms): POC **{vp['poc']:,.2f}** · "
          f"VA {vp['val']:,.2f}–{vp['vah']:,.2f} "
          f"({c.get('vp_bars', 0):,} × {c.get('vp_interval', '?')} volume bars)")
    if c.get("net_gex") is not None:
        regime = "PINNING (fades favoured)" if c["net_gex"] > 0 else "TRENDING (breaks favoured)"
        a(f"- Net dealer gamma **{c['net_gex']/1e6:+.1f}M** per 1% → **{regime}**"
          + (f" · flip {c['gamma_flip']:,.2f}" if c.get("gamma_flip") else ""))
    else:
        a("- Net dealer gamma: **unavailable**")
    if c.get("cot"):
        ct = c["cot"]
        a(f"- COT {ct['date']}: managed money {ct['mm_long']-ct['mm_short']:+,} net "
          f"({ct['mm_long']/max(1,ct['mm_short']):.1f}× long/short)")
    a("")

    a("## How your levels translate")
    a("")
    a("You give levels in **XAUUSD spot**. Futures and options are priced differently,")
    a("so every comparison below is converted into spot first — never the other way round.")
    a("")
    a("| Your level (spot) | = GC futures | = GLD strike | Options mapping precision |")
    a("|---|---|---|---|")
    for pl in res["levels"]:
        lv = pl["level"]
        fut_s = f"{lv + c['basis']:,.2f}" if c.get("basis") is not None else "—"
        r = c.get("ratio")
        gld_s = f"{lv / r:,.2f}" if r else "—"
        unc = c.get("spot_uncertainty")
        unc_s = f"±{unc:.1f} pts" if unc else "—"
        a(f"| {lv:,.2f} | {fut_s} | {gld_s} | {unc_s} |")
    a("")
    if c.get("spot_uncertainty"):
        a(f"The futures basis is stable (stdev {c.get('basis_stdev', 0):.2f} pts), so volume-profile")
        a(f"levels land accurately. The GLD ratio is not: ±{c['spot_uncertainty']:.1f} spot points against a")
        a(f"strike spacing of only {r:.1f}. **A single option strike cannot be pinned to a single spot**")
        a("**price** — treat mapped strikes as bands. CME's own OG options would remove this")
        a("entirely, since their strikes sit on the futures price and the basis maps cleanly.")
        a("")

    em = res["levels"][0]["entry_model"] if res["levels"] else "rejection"
    sf = res["levels"][0]["stop_floor"] if res["levels"] else 0
    sp = res["levels"][0]["spread"] if res["levels"] else 0
    a("## Trade model")
    a("")
    if em == "rejection":
        a(f"**Rejection entry** — wait for a bar to wick through the level and close back")
        a(f"inside it, then enter at that close. Stop beyond that bar's printed wick, but")
        a(f"never tighter than **{sf:.2f} pts**. Spread of {sp:.2f} charged on entry.")
        a("")
        a("The floor is not cosmetic. Measured on this instrument, the unfloored wick rule")
        a("gives a ~1.6 pt stop and **−0.33R**; a 5-pt floor gives **+0.52R** and 7 pts")
        a("**+0.62R**. The entry timing was never the problem — the stop was.")
    else:
        a("**Limit at the level** — assumes a resting order fills at the level itself.")
        a("Better average price than the rejection model, but you are also filled on every")
        a("break, and it is not the trade described in the strategy.")
    a("")

    for pl in res["levels"]:
        s = pl["score"]
        lv, d = pl["level"], pl["direction"]
        a(f"## {lv:,.2f} — {d.upper()} ({pl['side']} test)")
        a("")
        a(f"### Score {s['score']:.0f}/100 — **{s['verdict']}**")
        a("")
        a(f"{s['note']}")
        a("")
        a("| Component | Points | Detail |")
        a("|---|---:|---|")
        for label, pts, detail in s["items"]:
            a(f"| {label} | {pts:+.1f} | {detail} |")
        a(f"| **Total** | **{s['score']:.1f}** | |")
        a("")
        b = pl["hist"]["bucket"]
        if b.get("n"):
            # The stop quoted must be the stop the replay actually used, or the
            # expectancy underneath it is describing a different trade.
            rejection = pl["entry_model"] == "rejection"
            stop = pl["stop_floor"] if rejection else pl["stop_dist"]
            entry = lv
            stop_px = entry + stop if d == "short" else entry - stop
            t1 = entry - stop * 2 if d == "short" else entry + stop * 2
            t2 = entry - stop * 3 if d == "short" else entry + stop * 3
            a("**The trade, if you take it**")
            a("")
            if rejection:
                a(f"- Entry: on the rejection close, around {entry:,.2f} "
                  f"(the exact fill depends on where that bar closes)")
                a(f"- Stop: **{stop:.2f} pts minimum** beyond the printed wick — so no closer "
                  f"than ~{stop_px:,.2f}. Widen it if the wick is deeper; never tighten it.")
                a(f"- Deepest wick ever seen at this level: {b['pierce_max']:.2f} pts")
            else:
                a(f"- Entry: {entry:,.2f} (resting limit at the level)")
                a(f"- Stop: **{stop_px:,.2f}** — {stop:.2f} pts beyond, the p90 wick-through "
                  f"on non-break visits (deepest ever {b['pierce_max']:.2f})")
            a(f"- Target 2R {t1:,.2f} · 3R {t2:,.2f}")
            sig = (f", {b.get('n_triggered', 0)} produced a signal"
                   if pl["entry_model"] == "rejection" else "")
            a(f"- History: **{b.get('n_days',0)} distinct days** "
              f"({b.get('n_visits',0)} visits, {b['n']} events{sig}) "
              f"— held {b['hold_rate']*100:.0f}%, win {b['win_rate']*100:.0f}%, "
              f"expectancy {b['expectancy_r']:+.2f}R")
            a(f"- Cost: {pl['spread']:.2f} spread = "
              f"{pl['spread']/max(0.01, stop)*100:.0f}% of risk")
            if b.get("n_days", 0) < 5:
                a(f"- ⚠️ Only {b.get('n_days',0)} distinct days behind this. Events within a")
                a("  day share that day's regime, so the effective sample is small regardless")
                a("  of the event count.")
            a("")
            if pl.get("robustness"):
                a("**Stop sensitivity** — does the edge depend on getting the stop exactly right?")
                a("")
                a("| Stop (pts) | Win rate | Expectancy |")
                a("|---|---|---|")
                for r in pl["robustness"]:
                    mark = " ←" if abs(r["stop"] - pl["stop_dist"]) < 0.01 else ""
                    a(f"| {r['stop']:.2f}{mark} | {r['win_rate']*100:.0f}% | {r['expectancy_r']:+.2f}R |")
                a("")

            recent = sorted(pl["events"], key=lambda e: e.start_ts, reverse=True)[:5]
            a("| Last touches | Side | Day | Pierce | Broke | Result |")
            a("|---|---|---|---|---|---|")
            for e in recent:
                res = (f"{e.r_outcome:+.1f}R" if e.triggered else "_no signal_")
                a(f"| {iso(e.start_ts)} | {e.side} | {e.day_bias} | {e.pierce:.2f} | "
                  f"{'yes' if e.broke else 'no'} | {res} |")
            a("")
        else:
            a(f"⚠️ No prior {pl['side']} tests of this level on a {pl['hist']['bias']} day in "
              f"the {res['days']}-day window. There is no history to lean on.")
            a("")
    return "\n".join(L)


# ---------------------------------------------------------------------- journal

def journal_entries(res: dict) -> list[dict]:
    """One entry per level. Snapshots the gamma/OI state — which is the ONLY way
    it is ever recoverable, since no free historical options chain exists."""
    out = []
    c = res["ctx"]
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    as_of = datetime.fromtimestamp(res["as_of"] / 1000, tz=timezone.utc)\
        .strftime("%Y-%m-%dT%H:%M:%SZ")
    for pl in res["levels"]:
        s, b = pl["score"], pl["hist"]["bucket"]
        stop = pl["stop_floor"] if pl["entry_model"] == "rejection" else pl["stop_dist"]
        entry = pl["level"]
        out.append({
            "id": f"{as_of}-{res['symbol']}-{pl['level']:.2f}-{pl['direction']}",
            "logged_at": stamp,
            "source": "gala-level-confidence",
            "provenance": "as_of_replay" if res["as_of_replay"] else "live",
            "instrument": res["symbol"],
            "as_of": as_of,
            "price_at_idea": round(res["spot"], 3),
            "session": res["session"],
            "day_bias": res["bias"],
            "level": pl["level"],
            "direction": pl["direction"],
            "side": pl["side"],
            "verdict": s["verdict"],
            "score": s["score"],
            "score_items": [{"label": l, "points": p, "detail": d} for l, p, d in s["items"]],
            "entry": round(entry, 3),
            "stop": round(entry + stop if pl["direction"] == "short" else entry - stop, 3),
            "stop_distance": round(stop, 3),
            "target_2r": round(entry - stop * 2 if pl["direction"] == "short"
                               else entry + stop * 2, 3),
            "target_3r": round(entry - stop * 3 if pl["direction"] == "short"
                               else entry + stop * 3, 3),
            "entry_model": pl["entry_model"],
            "stop_floor": round(pl["stop_floor"], 3),
            "spread": pl["spread"],
            "history": {
                "n": b.get("n", 0),
                "n_visits": b.get("n_visits", 0),
                "n_days": b.get("n_days", 0),
                "n_triggered": b.get("n_triggered", 0),
                "hold_rate": round(b.get("hold_rate", 0), 3),
                "win_rate": round(b.get("win_rate", 0), 3),
                "expectancy_r": round(b.get("expectancy_r", 0), 3),
                "pierce_p90": round(b.get("pierce_p90", 0), 2),
                "pierce_max": round(b.get("pierce_max", 0), 2),
            },
            # The layer that cannot be rebuilt later. This is the archive.
            "gamma": {
                "net_gex": c.get("net_gex"),
                "gamma_flip": c.get("gamma_flip"),
                "regime": (None if c.get("net_gex") is None else
                           ("pinning" if c["net_gex"] > 0 else "trending")),
                "expiries": c.get("expiries"),
                "gld_ratio": c.get("ratio"),
                "gld_ratio_stdev": c.get("ratio_stdev"),
                "strike_mapping_uncertainty_pts": c.get("spot_uncertainty"),
                "nearest_oi": (None if not pl["ctx"].get("nearest_oi") else {
                    "spot": round(pl["ctx"]["nearest_oi"]["spot"], 2),
                    "total_oi": pl["ctx"]["nearest_oi"]["total_oi"],
                    "call_oi": pl["ctx"]["nearest_oi"]["call_oi"],
                    "put_oi": pl["ctx"]["nearest_oi"]["put_oi"],
                }),
            },
            "volume_profile": (None if not c.get("vp") else {
                "poc": round(c["vp"]["poc"], 2),
                "vah": round(c["vp"]["vah"], 2),
                "val": round(c["vp"]["val"], 2),
                "basis": round(c.get("basis", 0), 2),
                "nearest_node": (None if not pl["ctx"].get("nearest_node") else {
                    "price": round(pl["ctx"]["nearest_node"]["price"], 2),
                    "kind": pl["ctx"]["nearest_node"]["kind"],
                }),
            }),
            "robustness": [{"stop": r["stop"], "win_rate": round(r["win_rate"], 3),
                            "expectancy_r": round(r["expectancy_r"], 3)}
                           for r in pl.get("robustness", [])],
            "cot": c.get("cot"),
            "outcome": None,   # filled by journal_review.py
        })
    return out


def append_journal(entries: list[dict], path: str | None = None) -> str:
    month = datetime.now(timezone.utc).strftime("%Y-%m")
    path = path or os.path.join(REPO, "trade-journal", f"{month}.jsonl")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a") as f:          # append-only; never rewrite history
        for e in entries:
            f.write(json.dumps(e) + "\n")
    return path


def main() -> int:
    p = argparse.ArgumentParser(description="Score levels from every data layer")
    p.add_argument("--symbol", default="XAUUSD")
    p.add_argument("--level", action="append", type=float, required=True,
                   help="a level you marked (repeatable)")
    p.add_argument("--direction", choices=["short", "long"], default=None,
                   help="default: short if the level is above spot, long if below")
    p.add_argument("--as-of", default=None,
                   help="ISO timestamp — replay what could have been said then")
    p.add_argument("--days", type=int, default=14)
    p.add_argument("--entry", choices=["rejection", "level"], default="rejection",
                   help="rejection (default): wait for a bar to wick through and close "
                        "back inside, then enter — the strategy as actually described. "
                        "level: enter at the level on a resting limit.")
    p.add_argument("--stop-floor", type=float, default=None,
                   help="minimum stop in points. Default 0.125%% of spot (~5 pts on "
                        "gold). The raw wick rule gives ~1.6 pts and loses money.")
    p.add_argument("--spread", type=float, default=0.35,
                   help="round-trip spread in points, charged on entry")
    p.add_argument("--vp-interval", default="5m", help="futures bars for the volume profile")
    p.add_argument("--vp-range", default="30d", help="volume profile lookback")
    p.add_argument("--journal", action="store_true", help="append to trade-journal/")
    p.add_argument("--json", action="store_true", help="emit JSON instead of markdown")
    p.add_argument("--out", default=None)
    args = p.parse_args()

    res = gather(args.symbol, args.level, args.direction, parse_ts(args.as_of),
                 args.days, quiet=args.json, entry_model=args.entry,
                 stop_floor=args.stop_floor, spread=args.spread,
                 vp_interval=args.vp_interval, vp_range=args.vp_range)

    if args.json:
        print(json.dumps(journal_entries(res), indent=1))
    else:
        report = render(res)
        print(report)
        if args.out:
            os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
            with open(args.out, "w") as f:
                f.write(report + "\n")
            print(f"\nWrote {args.out}", file=sys.stderr)

    if args.journal:
        path = append_journal(journal_entries(res))
        print(f"Journalled {len(res['levels'])} entr"
              f"{'y' if len(res['levels'])==1 else 'ies'} → {path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except CTraderError as e:
        print(f"FAILED: {e}", file=sys.stderr)
        sys.exit(1)
