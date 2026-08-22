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
import json, sys
from collections import defaultdict
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
        r["strike"] = round(r["strike"] * ratio, 0)
        r["src"] = "QQQ"; r["spot"] = S_qqq
    for r in ndx_rows:
        r["src"] = "NDX"; r["spot"] = S_ndx
    return ndx_rows + qqq_rows, S_ndx, S_qqq, ratio, {"ndx": ndx_asof, "qqq": qqq_asof}


def bucket(rows, S_ndx, dte_max, bin_pts=50):
    """Aggregate $GEX and OI onto a common NDX-point grid."""
    agg = defaultdict(lambda: {"call_gex": 0.0, "put_gex": 0.0,
                               "call_oi": 0.0, "put_oi": 0.0})
    for r in rows:
        if r["dte"] > dte_max:
            continue
        s = r["spot"]
        g = r["gamma"] * r["oi"] * G.CONTRACT_MULT * s * s * 0.01
        if r["src"] == "QQQ":
            g *= 1.0            # QQQ $-gamma is already in dollars; no rescale
        k = round(r["strike"] / bin_pts) * bin_pts
        d = agg[k]
        if r["cp"] == "C":
            d["call_gex"] += g; d["call_oi"] += r["oi"]
        else:
            d["put_gex"] += g; d["put_oi"] += r["oi"]
    out = [{"strike": k, "net_gex": v["call_gex"] - v["put_gex"], **v}
           for k, v in sorted(agg.items())]
    return out


def build(cfd_price, max_dte=45):
    rows, S_ndx, S_qqq, ratio, asof = load_combined(max_dte)
    offset = cfd_price - S_ndx

    def cfd(x):
        return None if x is None else round(x + offset, 1)

    flip, _ = G.gamma_flip([r for r in rows if r["src"] == "NDX"], S_ndx)

    board = {"as_of": asof, "ndx_spot": round(S_ndx, 1), "qqq_spot": S_qqq,
             "ndx_qqq_ratio": round(ratio, 3), "nas100_cfd": cfd_price,
             "cfd_offset": round(offset, 1),
             "contracts": {"ndx": sum(1 for r in rows if r["src"] == "NDX"),
                           "qqq": sum(1 for r in rows if r["src"] == "QQQ")},
             "buckets": {}}

    for label, dte in (("near_expiry_0_2dte", 2), ("this_week", 7), ("full_45dte", max_dte)):
        pack = bucket(rows, S_ndx, dte)
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
        }

    board["gamma_flip"] = {"ndx": round(flip, 1) if flip else None,
                           "nas100": cfd(flip),
                           "spot_position": ("ABOVE flip — long gamma" if flip and S_ndx > flip
                                             else "BELOW flip — short gamma" if flip else None)}
    near = [r for r in rows if r["dte"] <= 7 and r["src"] == "NDX"]
    mp = G.max_pain(near)
    board["max_pain_week"] = {"ndx": mp, "nas100": cfd(mp)}
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
