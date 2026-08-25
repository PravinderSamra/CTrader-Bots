#!/usr/bin/env python3
"""
gex_levels.py — Phase-1 prototype: the annotated NAS100 gamma/OI level board.

Combines the NDX index chain and the QQQ ETF chain (QQQ strikes scaled into NDX
points by the live NDX/QQQ ratio) into ONE dealer-gamma picture, then emits the
marked-up level list: what each level is, what reaction to expect there, and
what it implies above vs. below.

    python3 gex_levels.py <NAS100_CFD_PRICE>
    python3 gex_levels.py 29290.5 --json
"""
import json, ssl, sys, urllib.request
from collections import defaultdict
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
import cboe_gex as G


def load_combined(max_dte=45):
    S_ndx, _ = G.spot_ndx()
    qq = G._get(G.CBOE_QTE.format("QQQ"))["data"]
    S_qqq = float(qq.get("current_price") or qq.get("close"))
    ratio = S_ndx / S_qqq

    ndx_rows, ndx_asof, _ = G.load_chain("_NDX", max_dte=max_dte)
    qqq_rows, qqq_asof, _ = G.load_chain("QQQ", max_dte=max_dte)

    # Rescale QQQ into NDX space. Gamma is per-1-point-of-underlying, so a
    # QQQ contract's gamma expressed in NDX points is gamma/ratio; the dollar
    # GEX formula then uses the NDX spot. Net effect on the $ figure is that a
    # QQQ contract contributes gamma_qqq * OI * 100 * S_qqq^2 * 0.01 — i.e. we
    # keep each chain's own spot for the dollar maths and only move the STRIKE.
    for r in qqq_rows:
        r["strike_native"] = r["strike"]          # keep the QQQ-space strike
        r["scale"] = ratio                        # NDX points per QQQ dollar
        r["strike"] = round(r["strike"] * ratio, 0)
        r["src"] = "QQQ"; r["spot"] = S_qqq
    for r in ndx_rows:
        r["strike_native"] = r["strike"]
        r["scale"] = 1.0
        r["src"] = "NDX"; r["spot"] = S_ndx
    return ndx_rows + qqq_rows, S_ndx, S_qqq, ratio, {"ndx": ndx_asof, "qqq": qqq_asof}


def expected_move(rows, S_ndx, cfd_offset, now_utc=None):
    """The market's own forecast for the next session, from the ATM straddle.

    An at-the-money call plus put is what it costs to own the move in either
    direction, so its price IS the expected absolute move. That is a sharper
    number than the VXN-derived range the brief already prints, which takes a
    30-day vol index and scales it to one day.

    IMPORTANT — this is NOT comparable to ADR. The straddle prices a
    CLOSE-to-close move; ADR measures the HIGH-LOW range, which is always the
    larger of the two. Reading "EM 162 vs ADR 409" as "the market expects a
    quiet day" is the same class of error as reading the range budget as
    though it forecast price travel. They measure different things.

    Skips a 0DTE expiry after the US cash close, when its quotes are final
    rather than live.
    """
    now = now_utc or datetime.now(timezone.utc)
    by_exp = defaultdict(list)
    for r in rows:
        if r.get("src") != "NDX":        # price the index, not the ETF proxy
            continue
        by_exp[(r["dte"], r["exp"])].append(r)
    for (dte, exp) in sorted(by_exp):
        if dte < 0 or (dte == 0 and now.hour >= 20):
            continue                     # expired or settling
        sub = by_exp[(dte, exp)]
        ks = sorted({r["strike"] for r in sub}, key=lambda k: abs(k - S_ndx))
        # Walk out from the money rather than demanding the single nearest
        # strike. `load_chain` drops strikes with no open interest, so the
        # exact ATM can be missing a call or a put — and taking only ks[0]
        # threw away the ENTIRE expiry when that happened, silently falling
        # through to a 7-day straddle and reporting it as the next session's
        # expected move (481pts instead of 162).
        atm = c = p = None
        for k in ks[:6]:
            cc = next((r for r in sub if r["strike"] == k and r["cp"] == "C"), None)
            pp = next((r for r in sub if r["strike"] == k and r["cp"] == "P"), None)
            if cc and pp and cc["bid"] and pp["bid"]:
                atm, c, p = k, cc, pp
                break
        if not c or not p:
            continue
        cm = (c["bid"] + c["ask"]) / 2
        pm = (p["bid"] + p["ask"]) / 2
        straddle = cm + pm
        # E|move| is about 0.8 of the straddle for a lognormal; 0.85 is the
        # convention most desks quote and the difference is inside the spread.
        em = straddle * 0.85
        return {"expiry": str(exp), "dte": dte,
                "atm_strike_ndx": atm,
                "straddle": round(straddle, 1),
                "em_pts": round(em, 1),
                "em_pct": round(em / S_ndx * 100, 2),
                "upper": round(S_ndx + em + cfd_offset, 1),
                "lower": round(S_ndx - em + cfd_offset, 1),
                "iv_atm": round((c["iv"] + p["iv"]) / 2, 4)}
    return None


def bucket(rows, S_ndx, dte_max, bin_pts=50, reprice=False):
    """Aggregate $GEX and OI onto a common NDX-point grid.

    `reprice=True` recomputes gamma with Black-Scholes at the CURRENT spot
    instead of trusting CBOE's published greeks. Those greeks carry the
    timestamp of the last chain update, which outside US cash hours is the
    previous close. Measured pre-market on 2026-08-24 the market had moved 173
    points since CBOE last recomputed: the published greeks gave net GEX
    +0.46bn (positive, "pinning"), repricing at the real spot gave -5.48bn
    (negative, "amplifying"). Opposite signs, opposite trading instruction, and
    the figure was being printed beside a flip that WAS repriced.
    """
    agg = defaultdict(lambda: {"call_gex": 0.0, "put_gex": 0.0,
                               "call_oi": 0.0, "put_oi": 0.0})
    for r in rows:
        if r["dte"] > dte_max:
            continue
        if reprice:
            sc = r.get("scale", 1.0)
            s = S_ndx / sc
            T = max(r["dte"], 0.5) / 365.0
            sig = r["iv"] if r["iv"] > 0.01 else 0.20
            gamma = G.bs_gamma(s, r.get("strike_native", r["strike"]), T, sig)
        else:
            s = r["spot"]
            gamma = r["gamma"]
        g = gamma * r["oi"] * G.CONTRACT_MULT * s * s * 0.01
        k = round(r["strike"] / bin_pts) * bin_pts
        d = agg[k]
        if r["cp"] == "C":
            d["call_gex"] += g; d["call_oi"] += r["oi"]
        else:
            d["put_gex"] += g; d["put_oi"] += r["oi"]
    out = [{"strike": k, "net_gex": v["call_gex"] - v["put_gex"], **v}
           for k, v in sorted(agg.items())]
    return out


def _nq_implied_cash(cash_close):
    """Roll a stale cash close forward using the futures move.

    The NDX cash index only prints during US cash hours. Ask CBOE for _NDX at
    08:26 UTC on a Monday and you get FRIDAY'S CLOSE, with no error and no
    obvious sign it is stale. Differencing a live CFD against it produced an
    offset of -200.7 instead of the true ~+3, which would have shifted every
    single options level on the board by 200 points during exactly the
    pre-market window the brief is read in.

    NQ futures trade nearly 24h, so the cash index can be rolled forward by the
    futures' move since its own prior close.
    """
    try:
        u = ("https://query1.finance.yahoo.com/v8/finance/chart/"
             "NQ%3DF?range=1d&interval=5m")
        req = urllib.request.Request(u, headers=G.UA)
        with urllib.request.urlopen(req, timeout=20, context=ssl.create_default_context()) as r:
            m = json.loads(r.read().decode())["chart"]["result"][0]["meta"]
        now, prev = m.get("regularMarketPrice"), m.get("chartPreviousClose")
        if not now or not prev:
            return None, None
        return cash_close + (now - prev), round(now - prev, 1)
    except Exception:
        return None, None


def _cash_is_stale(quote, max_age_min=30):
    """-> (stale, age_minutes, last_trade_iso)."""
    ts = quote.get("last_trade_time")
    if not ts:
        return False, None, None
    try:
        lt = datetime.fromisoformat(ts)
        if lt.tzinfo is None:
            lt = lt.replace(tzinfo=ZoneInfo("America/New_York"))
        age = (datetime.now(timezone.utc) - lt.astimezone(timezone.utc)).total_seconds() / 60
        return age > max_age_min, round(age, 0), ts
    except Exception:
        return False, None, ts


def build(cfd_price, max_dte=45):
    rows, S_ndx, S_qqq, ratio, asof = load_combined(max_dte)

    # Guard against anchoring the whole level board to a stale cash print.
    quote = G._get(G.CBOE_QTE.format("_NDX"))["data"]
    stale, age_min, last_trade = _cash_is_stale(quote)
    basis = {"method": "live_cash", "ndx_reference": round(S_ndx, 1),
             "cash_last_trade": last_trade, "cash_age_min": age_min}
    if stale:
        implied, fut_move = _nq_implied_cash(S_ndx)
        if implied:
            basis = {"method": "nq_implied",
                     "cash_close": round(S_ndx, 1),
                     "cash_last_trade": last_trade, "cash_age_min": age_min,
                     "nq_move_since_close": fut_move,
                     "ndx_reference": round(implied, 1),
                     "note": (f"NDX cash last traded {last_trade} "
                              f"({age_min:.0f} min ago) — rolled forward by the "
                              f"NQ futures move ({fut_move:+.1f}) rather than "
                              f"differencing against a stale close")}
            S_ndx = implied
        else:
            basis["method"] = "stale_cash_UNCORRECTED"
            basis["warning"] = (f"NDX cash is {age_min:.0f} min old and the "
                                f"futures fallback failed — every level below "
                                f"may be materially wrong. Treat with caution.")
    offset = cfd_price - S_ndx

    def cfd(x):
        return None if x is None else round(x + offset, 1)

    # Use the FULL book. The flip decides which entry model the day suits, and
    # computing it from NDX alone ignored 4,117 QQQ contracts — it put the flip
    # 253 points away from the combined-book answer, which on the wrong day
    # gives the opposite trading instruction. QQQ carries the volume; excluding
    # it here while including it everywhere else was simply inconsistent.
    flip, _ = G.gamma_flip(rows, S_ndx)

    board = {"as_of": asof, "ndx_spot": round(S_ndx, 1), "qqq_spot": S_qqq,
             "basis": basis,
             "ndx_qqq_ratio": round(ratio, 3), "nas100_cfd": cfd_price,
             "cfd_offset": round(offset, 1),
             "contracts": {"ndx": sum(1 for r in rows if r["src"] == "NDX"),
                           "qqq": sum(1 for r in rows if r["src"] == "QQQ")},
             "buckets": {}}

    for label, dte in (("near_expiry_0_2dte", 2), ("this_week", 7), ("full_45dte", max_dte)):
        pack = bucket(rows, S_ndx, dte, reprice=stale)
        if not pack:
            continue
        net = sum(p["net_gex"] for p in pack)
        above = [p for p in pack if p["strike"] > S_ndx]
        below = [p for p in pack if p["strike"] < S_ndx]
        cw = max(above, key=lambda p: p["call_gex"], default=None)
        pw = max(below, key=lambda p: p["put_gex"], default=None)
        cwo = max(above, key=lambda p: p["call_oi"], default=None)
        pwo = max(below, key=lambda p: p["put_oi"], default=None)
        board["buckets"][label] = {
            "net_gex_$bn_per_1pct": round(net / 1e9, 3),
            "regime": "POSITIVE" if net > 0 else "NEGATIVE",
            "call_wall": {"ndx": cw["strike"], "nas100": cfd(cw["strike"]),
                          "gex_$bn": round(cw["call_gex"] / 1e9, 3),
                          "oi": int(cw["call_oi"])} if cw else None,
            "put_wall": {"ndx": pw["strike"], "nas100": cfd(pw["strike"]),
                         "gex_$bn": round(pw["put_gex"] / 1e9, 3),
                         "oi": int(pw["put_oi"])} if pw else None,
            "max_call_oi": {"ndx": cwo["strike"], "nas100": cfd(cwo["strike"]),
                            "oi": int(cwo["call_oi"])} if cwo else None,
            "max_put_oi": {"ndx": pwo["strike"], "nas100": cfd(pwo["strike"]),
                           "oi": int(pwo["put_oi"])} if pwo else None,
            "largest_abs_gex": [
                {"ndx": p["strike"], "nas100": cfd(p["strike"]),
                 "net_gex_$bn": round(p["net_gex"] / 1e9, 3),
                 "sign": "+" if p["net_gex"] > 0 else "-"}
                for p in sorted(pack, key=lambda p: -abs(p["net_gex"]))[:10]],
            # The board publishes ONE call wall and ONE put wall, and that
            # hides real structure. On 2026-08-25 the heaviest gamma
            # concentration within 280pts of spot — 0.94bn across 31.6k
            # contracts at 29183.5 — was neither, so it never reached the
            # reader even though price pivoted on it all afternoon.
            #
            # Note it was CALL gamma sitting BELOW spot (in-the-money calls,
            # dealers buying dips). `put_wall` takes max(below, key=put_gex)
            # and so cannot see it at all. Rank each strike by whichever side
            # actually dominates it, and carry that label.
            "walls_ranked": {
                side: [{"nas100": cfd(p["strike"]),
                        "dominant": "CALL" if p["call_gex"] >= p["put_gex"] else "PUT",
                        "gex_$bn": round(max(p["call_gex"], p["put_gex"]) / 1e9, 3),
                        "oi": int(p["call_oi"] if p["call_gex"] >= p["put_gex"]
                                  else p["put_oi"])}
                       for p in sorted(grp,
                                       key=lambda p: -max(p["call_gex"], p["put_gex"]))[:6]]
                for side, grp in (("above", above), ("below", below))
            },
        }

    board["gamma_flip"] = {"ndx": round(flip, 1) if flip else None,
                           "nas100": cfd(flip),
                           "spot_position": ("ABOVE flip — long gamma" if flip and S_ndx > flip
                                             else "BELOW flip — short gamma" if flip else None)}
    basis["greeks"] = ("repriced_bs_at_current_spot" if stale
                       else "cboe_published")
    near = [r for r in rows if r["dte"] <= 7 and r["src"] == "NDX"]
    mp = G.max_pain(near)
    board["max_pain_week"] = {"ndx": mp, "nas100": cfd(mp)}
    board["expected_move"] = expected_move(rows, S_ndx, board["cfd_offset"])
    return board


if __name__ == "__main__":
    price = float(sys.argv[1])
    b = build(price)
    if "--json" in sys.argv:
        print(json.dumps(b, indent=2)); sys.exit(0)
    print(f"NDX {b['ndx_spot']}  QQQ {b['qqq_spot']}  ratio {b['ndx_qqq_ratio']}  "
          f"| NAS100 CFD {b['nas100_cfd']}  offset {b['cfd_offset']}")
    print(f"contracts: NDX {b['contracts']['ndx']} + QQQ {b['contracts']['qqq']}")
    gf = b["gamma_flip"]
    print(f"\nGAMMA FLIP  NDX {gf['ndx']} -> NAS100 {gf['nas100']}   {gf['spot_position']}")
    print(f"MAX PAIN(wk) NDX {b['max_pain_week']['ndx']} -> NAS100 {b['max_pain_week']['nas100']}")
    for label, d in b["buckets"].items():
        print(f"\n--- {label}: net GEX {d['net_gex_$bn_per_1pct']} $bn/1%  [{d['regime']}]")
        for k in ("call_wall", "put_wall", "max_call_oi", "max_put_oi"):
            print(f"    {k:14} {d[k]}")
        print("    largest |GEX| bins:")
        for p in d["largest_abs_gex"][:6]:
            print(f"      NAS100 {p['nas100']:>10}   {p['sign']}{abs(p['net_gex_$bn']):.3f} $bn")


# ---------------------------------------------------------------------------
# Expiry-structure read.
#
# The three buckets (0-2 DTE, this week, full 45 DTE) are not three versions of
# the same number — they are near-dated vs longer-dated dealer positioning, and
# near-dated gamma DECAYS DURING THE DAY. So when they disagree, the day has a
# shape: one regime early, a different one late. That is the signal.
#
#   both negative      -> expansion, and the whole book agrees. High conviction.
#   both positive      -> pinned range all day. High conviction.
#   near +, far -      -> PINNED EARLY, EXPANDS LATE. 0DTE gamma holds price
#                         through the morning; as it decays into the afternoon
#                         the short-gamma structure underneath takes over.
#                         Be patient early, aggressive after ~13:00 ET.
#   near -, far +      -> SHARP MOVE THAT MEAN-REVERTS. Near-term instability
#                         inside a stabilising structure: fade the extremes,
#                         but only back to the middle.
#
# A deadband stops a rounding-level figure (0.002bn) being read as "positive".
# ---------------------------------------------------------------------------
DEADBAND_BN = 0.05


def _sign(v):
    if v is None:
        return 0
    return 1 if v > DEADBAND_BN else (-1 if v < -DEADBAND_BN else 0)


def expiry_structure(board):
    b = board.get("buckets", {})
    near = (b.get("near_expiry_0_2dte") or {}).get("net_gex_$bn_per_1pct")
    week = (b.get("this_week") or {}).get("net_gex_$bn_per_1pct")
    full = (b.get("full_45dte") or {}).get("net_gex_$bn_per_1pct")
    sn, sw, sf = _sign(near), _sign(week), _sign(full)
    far = sf if sf != 0 else sw

    if sn < 0 and far < 0:
        shape, conf = "COHERENT_SHORT", "high"
        what = ("Every expiry is short gamma and it deepens with tenor — the "
                "whole options book is positioned for movement, not just "
                "today's contracts.")
        do = ("Expect range expansion and trends that persist. Strategy 2. "
              "Today's ADR can be exceeded — don't cap the target too early.")
    elif sn > 0 and far > 0:
        shape, conf = "COHERENT_LONG", "high"
        what = ("Every expiry is long gamma — dealers are damping moves across "
                "the board.")
        do = ("Expect a tight, pinned range. Strategy 1 at the walls. Keep "
              "targets modest; breakouts mostly fail.")
    elif sn > 0 and far < 0:
        shape, conf = "PIN_THEN_EXPAND", "high"
        what = ("Today's expiring contracts are pinning price, but the book "
                "underneath is short gamma. That near-dated gamma decays "
                "through the session.")
        do = ("**Chop early, resolve late.** Be patient in the morning — "
              "breakouts will fail while the pin holds. From roughly 13:00 ET "
              "the pin weakens and the move that has been building gets "
              "released. Save your risk for the afternoon.")
    elif sn < 0 and far > 0:
        shape, conf = "SPIKE_THEN_REVERT", "medium"
        what = ("Near-dated is short gamma inside a longer-dated book that is "
                "long gamma — instability today wrapped in stability.")
        do = ("Expect a sharp move that then mean-reverts. Fade the extremes, "
              "but only back toward the middle — don't hold for continuation.")
    elif sn == 0 and far < 0:
        shape, conf = "FRONT_FLAT_BACK_SHORT", "medium"
        what = ("Today's expiries are gamma-neutral, so there is nothing "
                "pinning price, and the longer book is short gamma.")
        do = ("Nothing holds price in place. Moves that start tend to keep "
              "going — favour continuation over fades, but conviction is "
              "lower than a fully coherent short-gamma day.")
    elif sn == 0 and far > 0:
        shape, conf = "FRONT_FLAT_BACK_LONG", "medium"
        what = ("Today's expiries are gamma-neutral inside a longer-dated "
                "long-gamma book.")
        do = ("Mild damping, no strong pin. Normal range day; take the walls "
              "as soft boundaries rather than hard ones.")
    else:
        shape, conf = "NEUTRAL", "low"
        what = "No meaningful gamma positioning in either the front or the back book."
        do = ("Gamma is not a factor today — trade structure and levels, and "
              "ignore the dealer-flow argument entirely.")

    return {"shape": shape, "confidence": conf,
            "near_0_2dte": near, "this_week": week, "full_45dte": full,
            "signs": {"near": sn, "far": far},
            "what_it_is": what, "what_to_do": do,
            "agree": sn == far and sn != 0}
