#!/usr/bin/env python3
"""
cboe_gex.py — Phase-1 prototype: NAS100 (NDX) gamma-exposure / open-interest engine.

Source: CBOE's public delayed-quotes JSON (no API key, ~15-min delay).
  https://cdn.cboe.com/api/global/delayed_quotes/options/_NDX.json   (index options)
  https://cdn.cboe.com/api/global/delayed_quotes/options/QQQ.json    (ETF cross-check)
  https://cdn.cboe.com/api/global/delayed_quotes/quotes/_NDX.json    (NDX cash spot)

Every contract row carries: open_interest, volume, iv, delta, gamma, theta, vega, rho.
That is everything needed for a real GEX build — no vendor, no key, no scraping.

Outputs the level set the brief needs:
  - net GEX (total + per-expiry buckets: 0DTE, this week, all)
  - gamma flip / zero-gamma level (Black-Scholes re-priced across a spot grid)
  - call wall / put wall (GEX-weighted and raw-OI)
  - top OI strikes, max pain
  - each level translated from NDX index points to the broker's NAS100 CFD price
"""
import json, math, ssl, sys, urllib.request
from datetime import datetime, timezone, date
from collections import defaultdict

CBOE_OPT = "https://cdn.cboe.com/api/global/delayed_quotes/options/{}.json"
CBOE_QTE = "https://cdn.cboe.com/api/global/delayed_quotes/quotes/{}.json"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/125.0 Safari/537.36"}
CONTRACT_MULT = 100          # NDX / QQQ options both 100x
R = 0.0425                   # risk-free proxy; refresh from ^IRX in production


def _get(url, timeout=60):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout,
                                context=ssl.create_default_context()) as r:
        return json.loads(r.read().decode())


def parse_osi(sym):
    """'NDX260821C04000000' -> (date(2026,8,21), 'C', 4000.0)"""
    i = 0
    while i < len(sym) and not sym[i].isdigit():
        i += 1
    body = sym[i:]
    yy, mm, dd = int(body[0:2]), int(body[2:4]), int(body[4:6])
    cp = body[6]
    strike = int(body[7:15]) / 1000.0
    return date(2000 + yy, mm, dd), cp, strike


# ---------- Black-Scholes gamma (for re-pricing the flip point) ----------
def _norm_pdf(x):
    return math.exp(-0.5 * x * x) / math.sqrt(2 * math.pi)


def bs_gamma(S, K, T, sigma, r=R):
    if S <= 0 or K <= 0 or T <= 0 or sigma <= 0:
        return 0.0
    d1 = (math.log(S / K) + (r + 0.5 * sigma * sigma) * T) / (sigma * math.sqrt(T))
    return _norm_pdf(d1) / (S * sigma * math.sqrt(T))


def load_chain(ticker="_NDX", max_dte=90, min_oi=1):
    raw = _get(CBOE_OPT.format(ticker))
    asof = raw.get("timestamp")
    today = datetime.now(timezone.utc).date()
    rows = []
    for o in raw["data"]["options"]:
        oi = o.get("open_interest") or 0
        if oi < min_oi:
            continue
        try:
            exp, cp, k = parse_osi(o["option"])
        except Exception:
            continue
        dte = (exp - today).days
        if dte < 0 or dte > max_dte:
            continue
        rows.append({
            "exp": exp, "dte": dte, "cp": cp, "strike": k, "oi": float(oi),
            "vol": float(o.get("volume") or 0), "gamma": float(o.get("gamma") or 0),
            "delta": float(o.get("delta") or 0), "iv": float(o.get("iv") or 0),
            # Kept for the ATM-straddle expected move. The straddle is the
            # market's own price for the next session's move, which is a
            # sharper number than scaling a 30-day vol index down to one day.
            "bid": float(o.get("bid") or 0), "ask": float(o.get("ask") or 0),
        })
    return rows, asof, raw["data"].get("close")


def spot_ndx():
    q = _get(CBOE_QTE.format("_NDX"))["data"]
    return float(q.get("current_price") or q.get("close")), q


def build_gex(rows, S, bucket_dte=None):
    """Naive dealer convention: long calls / short puts (repo-standard).
    gex_$ per strike = gamma * OI * mult * S^2 * 0.01  -> $ delta change per 1% move."""
    per_strike = defaultdict(lambda: {"call_gex": 0.0, "put_gex": 0.0,
                                      "call_oi": 0.0, "put_oi": 0.0,
                                      "call_vol": 0.0, "put_vol": 0.0})
    for r_ in rows:
        if bucket_dte is not None and r_["dte"] > bucket_dte:
            continue
        g = r_["gamma"] * r_["oi"] * CONTRACT_MULT * S * S * 0.01
        d = per_strike[r_["strike"]]
        if r_["cp"] == "C":
            d["call_gex"] += g; d["call_oi"] += r_["oi"]; d["call_vol"] += r_["vol"]
        else:
            d["put_gex"] += g; d["put_oi"] += r_["oi"]; d["put_vol"] += r_["vol"]
    out = []
    for k, d in sorted(per_strike.items()):
        out.append({"strike": k, "net_gex": d["call_gex"] - d["put_gex"], **d})
    return out


def gamma_flip(rows, S, lo_pct=0.92, hi_pct=1.08, steps=81):
    """Re-price total net GEX across a grid of hypothetical spots using BS gamma
    (contract IV held fixed). The spot where net GEX crosses zero is the flip."""
    grid = [S * (lo_pct + (hi_pct - lo_pct) * i / (steps - 1)) for i in range(steps)]
    curve = []
    for s in grid:
        tot = 0.0
        for r_ in rows:
            T = max(r_["dte"], 0.5) / 365.0
            sig = r_["iv"] if r_["iv"] > 0.01 else 0.20
            # Rows may come from chains quoted in different price spaces (NDX
            # index points vs QQQ dollars). `scale` maps this row's native
            # space onto the NDX grid: price the contract where it actually
            # lives, then combine the dollar results.
            scale = r_.get("scale", 1.0)
            k = r_.get("strike_native", r_["strike"])
            s_native = s / scale
            g = bs_gamma(s_native, k, T, sig)
            v = g * r_["oi"] * CONTRACT_MULT * s_native * s_native * 0.01
            tot += v if r_["cp"] == "C" else -v
        curve.append((s, tot))
    flip = None
    for (s0, v0), (s1, v1) in zip(curve, curve[1:]):
        if v0 == 0:
            flip = s0; break
        if v0 * v1 < 0:
            flip = s0 + (s1 - s0) * (-v0) / (v1 - v0); break
    return flip, curve


def max_pain(rows):
    strikes = sorted({r_["strike"] for r_ in rows})
    best, best_pain = None, None
    for s in strikes:
        pain = 0.0
        for r_ in rows:
            if r_["cp"] == "C":
                pain += max(0.0, s - r_["strike"]) * r_["oi"]
            else:
                pain += max(0.0, r_["strike"] - s) * r_["oi"]
        if best_pain is None or pain < best_pain:
            best, best_pain = s, pain
    return best


def summarise(ticker="_NDX", cfd_price=None, max_dte=45):
    rows, asof, close = load_chain(ticker, max_dte=max_dte)
    S, q = spot_ndx()
    offset = (cfd_price - S) if cfd_price else 0.0

    def cfd(x):
        return None if x is None else round(x + offset, 1)

    res = {"source": "cboe_delayed_quotes", "as_of": asof, "ndx_spot": S,
           "cfd_price": cfd_price, "cfd_offset": round(offset, 1),
           "contracts_loaded": len(rows),
           "expiries": sorted({str(r_["exp"]) for r_ in rows})[:8]}

    for label, dte in (("0dte", 0), ("week", 7), ("all", max_dte)):
        pack = build_gex(rows, S, bucket_dte=dte)
        if not pack:
            continue
        net = sum(p["net_gex"] for p in pack)
        above = [p for p in pack if p["strike"] > S]
        below = [p for p in pack if p["strike"] < S]
        cw = max(above, key=lambda p: p["call_gex"], default=None)
        pw = max(below, key=lambda p: p["put_gex"], default=None)
        cw_oi = max(above, key=lambda p: p["call_oi"], default=None)
        pw_oi = max(below, key=lambda p: p["put_oi"], default=None)
        res[label] = {
            "net_gex_$bn_per_1pct": round(net / 1e9, 3),
            "regime": "POSITIVE (pinning/mean-revert)" if net > 0 else "NEGATIVE (amplifying/trending)",
            "call_wall_gex": {"ndx": cw["strike"], "nas100": cfd(cw["strike"]),
                              "gex_$bn": round(cw["call_gex"] / 1e9, 3)} if cw else None,
            "put_wall_gex": {"ndx": pw["strike"], "nas100": cfd(pw["strike"]),
                             "gex_$bn": round(pw["put_gex"] / 1e9, 3)} if pw else None,
            "call_wall_oi": {"ndx": cw_oi["strike"], "nas100": cfd(cw_oi["strike"]),
                             "oi": int(cw_oi["call_oi"])} if cw_oi else None,
            "put_wall_oi": {"ndx": pw_oi["strike"], "nas100": cfd(pw_oi["strike"]),
                            "oi": int(pw_oi["put_oi"])} if pw_oi else None,
            "top_abs_gex_strikes": [
                {"ndx": p["strike"], "nas100": cfd(p["strike"]),
                 "net_gex_$bn": round(p["net_gex"] / 1e9, 3)}
                for p in sorted(pack, key=lambda p: -abs(p["net_gex"]))[:8]],
        }

    flip, curve = gamma_flip(rows, S)
    res["gamma_flip"] = {"ndx": round(flip, 1) if flip else None, "nas100": cfd(flip),
                         "spot_vs_flip": ("ABOVE — long-gamma/pinned"
                                          if flip and S > flip else
                                          "BELOW — short-gamma/volatile" if flip else None)}
    res["max_pain"] = {"ndx": max_pain([r_ for r_ in rows if r_["dte"] <= 7]),
                       "note": "nearest-week expiries"}
    res["max_pain"]["nas100"] = cfd(res["max_pain"]["ndx"])
    return res


if __name__ == "__main__":
    cfd = float(sys.argv[1]) if len(sys.argv) > 1 else None
    print(json.dumps(summarise(cfd_price=cfd), indent=2, default=str))
