#!/usr/bin/env python3
"""
fred_probe.py — the FRED macro layer for the NAS100 brief.

Adds what Yahoo cannot give us: the **real** rate and liquidity picture. Nominal
yields (^TNX) tell you what rates did; real yields and breakevens tell you WHY,
and the why is what actually reprices long-duration tech.

Auth: reads FRED_API_KEY from the environment. The key is never written to the
repo — set it in your Claude Code environment settings (persists across
sessions) and as a GitHub Actions repo secret for the scheduled job.
Free key: https://fredaccount.stlouisfed.org/apikey  (120 req/min, no card)

    python3 fred_probe.py             # human-readable
    python3 fred_probe.py --json
"""
import json, os, ssl, sys, urllib.parse, urllib.request
from datetime import datetime, timezone

_KEY = next((os.environ[v].strip() for v in ("FRED_API_KEY", "FRED_KEY")
             if os.environ.get(v, "").strip()), "")
_BASE = "https://api.stlouisfed.org/fred/series/observations"
_CTX = ssl.create_default_context()
_UA = {"User-Agent": "nas100-daily-brief/1.0"}

# series_id -> (label, unit, why it matters for NAS100)
SERIES = {
    "DFII10": ("10y real yield (TIPS)", "%",
               "THE discount rate on long-duration tech. Rising real yields "
               "compress multiples directly — more predictive than nominal"),
    "DFII5":  ("5y real yield", "%", "Short-end real rate; policy-driven"),
    "T10YIE": ("10y breakeven inflation", "%",
               "Splits a nominal move into growth vs inflation. Nominal up on "
               "breakevens = inflation scare (bearish). Nominal up on real "
               "yields = tightening (also bearish, different flavour)"),
    "T5YIFR": ("5y5y forward inflation", "%",
               "Long-run inflation credibility. A break higher is the Fed "
               "losing the anchor — very bearish duration"),
    "DGS10":  ("10y nominal", "%", "Headline yield, cross-check on ^TNX"),
    "DGS2":   ("2y nominal", "%", "Fed-path expectations"),
    "T10Y2Y": ("10y-2y curve", "pp",
               "Steepening from the front end = cuts priced (risk-on). "
               "Bear-steepening from the long end = term premium (risk-off)"),
    "NFCI":   ("Chicago Fed financial conditions", "index",
               "Negative = looser than average. A weekly rise while equities "
               "are up is an early warning; conditions lead price"),
    "BAMLH0A0HYM2": ("US high-yield OAS", "%",
                     "Credit's opinion on risk. Widening HY spreads while "
                     "NAS100 rallies is the most reliable divergence there is"),
    "WALCL":  ("Fed balance sheet", "$mn",
               "Weekly. Shrinking = QT draining liquidity, a slow headwind"),
    "RRPONTSYD": ("Overnight reverse repo", "$bn",
                  "Cash parked at the Fed. Near zero means the liquidity "
                  "buffer is gone and QT starts biting reserves"),
    "SOFR":   ("SOFR", "%", "Funding stress tell; a spike is a plumbing problem"),
    "VIXCLS": ("VIX (FRED close)", "index", "Authoritative daily settle"),
    "DTWEXBGS": ("Broad dollar index", "index",
                 "Fed's trade-weighted dollar — cleaner than DXY, which is "
                 "58% EUR"),
}


def _get(series_id, limit=8):
    q = urllib.parse.urlencode({
        "series_id": series_id, "api_key": _KEY, "file_type": "json",
        "sort_order": "desc", "limit": limit})
    req = urllib.request.Request(f"{_BASE}?{q}", headers=_UA)
    with urllib.request.urlopen(req, timeout=25, context=_CTX) as r:
        return json.loads(r.read().decode())


def series(series_id, limit=10):
    """Latest value plus 1-step and 5-step changes, skipping FRED's '.' gaps.
    Keeps the full observation list so cross-series comparisons can be aligned
    on a common date — see aligned_change()."""
    if not _KEY:
        return {"_error": "FRED_API_KEY not set — see the docstring"}
    try:
        obs = _get(series_id, limit).get("observations", [])
    except Exception as e:
        return {"_error": f"{type(e).__name__}: {e}"}
    vals = [(o["date"], float(o["value"])) for o in obs if o["value"] not in (".", "")]
    if not vals:
        return {"_error": "no numeric observations"}
    label, unit, why = SERIES.get(series_id, (series_id, "", ""))
    d0, v0 = vals[0]
    out = {"id": series_id, "label": label, "unit": unit, "why": why,
           "date": d0, "value": v0, "_obs": vals}
    if len(vals) > 1:
        out["chg_1"] = round(v0 - vals[1][1], 4)
        out["prev_date"] = vals[1][0]
    if len(vals) > 5:
        out["chg_5"] = round(v0 - vals[5][1], 4)
    return out


def aligned_change(d, ids):
    """FRED series publish on different lags — DFII10 lands a day after T10YIE,
    so naively comparing each series' own chg_1 compares different days and
    produced a nonsense decomposition (nominal +4bp with real +0 and breakeven
    +0). Find the latest date present in ALL requested series, and the latest
    common date before it, then measure every change over that same interval.

    Returns (as_of, prev, {series_id: change}) or (None, None, {}) if the
    series do not share two common dates."""
    sets = []
    for sid in ids:
        v = d.get(sid) or {}
        if "_error" in v or not v.get("_obs"):
            return None, None, {}
        sets.append({dt for dt, _ in v["_obs"]})
    common = sorted(set.intersection(*sets), reverse=True)
    if len(common) < 2:
        return None, None, {}
    a, b = common[0], common[1]
    chg = {}
    for sid in ids:
        m = dict(d[sid]["_obs"])
        chg[sid] = round(m[a] - m[b], 4)
    return a, b, chg


def run(ids=None):
    ids = ids or list(SERIES)
    data = {sid: series(sid) for sid in ids}
    ok = [k for k, v in data.items() if "_error" not in v]
    read = interpret(data)
    for v in data.values():
        v.pop("_obs", None)          # raw observations are working state, not output
    return {"generated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "key_present": bool(_KEY), "series_ok": len(ok),
            "series_failed": [k for k in data if "_error" in data[k]],
            "data": data, "read": read}


def interpret(d):
    """The lines the brief actually prints — signed for NAS100."""
    out = []

    def g(sid, field="chg_1"):
        v = d.get(sid, {})
        return None if "_error" in v else v.get(field)

    # --- real yields: the single most important macro read for tech ---------
    r10, r10v = g("DFII10"), (d.get("DFII10") or {}).get("value")
    r10_5 = g("DFII10", "chg_5")
    if r10 is not None:
        bp = round(r10 * 100)
        out.append({
            "tag": "real_yields", "signal": -1 if r10 > 0.01 else (1 if r10 < -0.01 else 0),
            "text": f"10y REAL yield {r10v}% ({bp:+d}bp d/d, "
                    f"{(r10_5 or 0)*100:+.0f}bp 5d) — "
                    + ("rising real rates compress tech multiples directly: BEARISH"
                       if r10 > 0.01 else
                       "falling real rates support duration: BULLISH" if r10 < -0.01
                       else "flat day-on-day; watch the 5-day trend")})

    # --- decompose a nominal move into real vs breakeven --------------------
    # Measured over a date interval common to all three series, never over each
    # series' own latest step (their publication lags differ).
    as_of, prev, ch = aligned_change(d, ["DGS10", "DFII10", "T10YIE"])
    if as_of and abs(ch["DGS10"]) > 0.005:
        nom, rr, be = ch["DGS10"], ch["DFII10"], ch["T10YIE"]
        driver = ("breakeven / inflation expectations" if abs(be) > abs(rr)
                  else "real rate / tightening")
        out.append({"tag": "yield_decomp", "signal": -1 if nom > 0 else 1,
                    "text": f"10y nominal {nom*100:+.0f}bp over {prev}->{as_of}, "
                            f"driven by {driver} (real {rr*100:+.0f}bp, "
                            f"breakeven {be*100:+.0f}bp) — "
                            + ("rising yields on real rates is the most direct "
                               "multiple compression for tech" if nom > 0 and abs(rr) > abs(be)
                               else "an inflation-expectation move; hits tech via the "
                                    "Fed-path repricing that follows" if nom > 0
                               else "falling yields support duration")})
    elif as_of:
        out.append({"tag": "yield_decomp", "signal": 0,
                    "text": f"10y nominal unchanged {prev}->{as_of} — no rate impulse"})

    # --- credit: the most reliable divergence -------------------------------
    hy, hyv = g("BAMLH0A0HYM2"), (d.get("BAMLH0A0HYM2") or {}).get("value")
    hy5 = g("BAMLH0A0HYM2", "chg_5")
    if hyv is not None:
        wide = (hy5 or 0) > 0.15
        out.append({"tag": "credit", "signal": -2 if wide else (1 if hyv < 3.0 else 0),
                    "text": f"HY OAS {hyv}% ({(hy5 or 0)*100:+.0f}bp/5d) — "
                            + ("WIDENING: credit is refusing the equity rally, "
                               "strong bearish divergence" if wide else
                               "tight, credit is comfortable with risk" if hyv < 3.0
                               else "neutral")})

    # --- financial conditions ------------------------------------------------
    nf, nfv = g("NFCI"), (d.get("NFCI") or {}).get("value")
    if nfv is not None:
        out.append({"tag": "fin_conditions",
                    "signal": -1 if (nf or 0) > 0.01 else (1 if (nf or 0) < -0.01 else 0),
                    "text": f"NFCI {nfv} ({nf:+.3f} w/w) — conditions "
                            + ("looser than average" if nfv < 0 else "tighter than average")
                            + ("; TIGHTENING week-on-week, a leading headwind"
                               if (nf or 0) > 0.01 else "")})

    # --- liquidity -----------------------------------------------------------
    bs, bsv = g("WALCL"), (d.get("WALCL") or {}).get("value")
    rrp = (d.get("RRPONTSYD") or {}).get("value")
    if bsv is not None:
        out.append({"tag": "liquidity", "signal": -1 if (bs or 0) < -5000 else 0,
                    "text": f"Fed balance sheet ${bsv/1e6:.2f}tn ({(bs or 0)/1e3:+.1f}bn w/w)"
                            + (f", ON RRP ${rrp}bn" if rrp is not None else "")
                            + (" — QT draining, slow headwind" if (bs or 0) < -5000 else "")})

    # --- curve ----------------------------------------------------------------
    cv, cvv = g("T10Y2Y"), (d.get("T10Y2Y") or {}).get("value")
    if cvv is not None:
        out.append({"tag": "curve", "signal": 0,
                    "text": f"10y-2y {cvv:+.2f}pp ({(cv or 0)*100:+.0f}bp) — "
                            + ("bear-steepening on the long end: term premium, risk-off"
                               if (cv or 0) > 0.02 and (g('DGS10') or 0) > 0 else
                               "bull-steepening: cuts being priced, risk-on"
                               if (cv or 0) > 0.02 else "little change")})
    return out


if __name__ == "__main__":
    r = run()
    if "--json" in sys.argv:
        print(json.dumps(r, indent=2)); sys.exit(0)
    if not r["key_present"]:
        print("FRED_API_KEY not set."); sys.exit(1)
    print(f"FRED  {r['series_ok']}/{len(SERIES)} series OK"
          + (f"  FAILED: {r['series_failed']}" if r["series_failed"] else ""))
    for sid, v in r["data"].items():
        if "_error" in v:
            print(f"  !! {sid}: {v['_error']}"); continue
        c = f"{v.get('chg_1', 0):+.4g}" if "chg_1" in v else "  n/a"
        print(f"  {sid:14} {v['date']}  {v['value']:>14,.4g} {v['unit']:<6} d1 {c:>10}  {v['label']}")
    print("\nRead:")
    for x in r["read"]:
        print(f"  [{x['signal']:+d}] {x['text']}")
