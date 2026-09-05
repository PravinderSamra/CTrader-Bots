#!/usr/bin/env python3
"""
What is GexBot actually computing? Rebuild it from the free public chain.

Every gamma-exposure number in this project rests on an assumption nobody can
observe: which side of each contract the dealer is on. The near-universal
convention is *calls positive, puts negative* -- "dealers are long calls and
short puts" -- but that is an inventory guess, not a property of the greek
(see ../research/volume-vs-open-interest.md). If it is wrong, every wall in
the ladder has the wrong sign and the whole read inverts.

Rather than argue about it, this reconstructs GexBot's per-strike numbers from
data anyone can download -- Cboe's free delayed NDX chain, which carries
gamma, open interest and volume per contract -- and asks which convention
reproduces them.

Four candidates are fitted per reading:

    A   +calls  -puts     the standard convention
    B   -calls  +puts     the inverse
    C   +calls  +puts     no directional assumption at all
    D   -calls  -puts     C, inverted

The one that matches is the one GexBot uses. A high correlation under A and a
mirror-image negative under B is not ambiguity -- B is just A with the sign
flipped, and only A reproduces the levels.

Scope matters. Only `gex_one` (the next expiry) can be tested: the session's
own 0DTE contracts have already expired and dropped out of the free chain by
the time the EOD report is available, and `gex_zero`/`gex_full` both depend on
them. That limit is a property of the free data, not of the method.

Usage:
    python3 sign_convention_test.py --zip /path/eod_report_NQ_NDX_2026-09-04.zip
    python3 sign_convention_test.py --zip ... --chain ndx.json   # cached chain
"""

from __future__ import annotations

import argparse
import collections
import datetime as dt
import gzip
import io
import json
import math
import statistics
import sys
import urllib.request
import zipfile

CHAIN_URL = "https://cdn.cboe.com/api/global/delayed_quotes/options/_NDX.json"

CONVENTIONS = [
    ("A  +calls -puts   (standard: dealers long calls, short puts)", +1, -1),
    ("B  -calls +puts   (inverted)",                                 -1, +1),
    ("C  +calls +puts   (no directional assumption)",                +1, +1),
    ("D  -calls -puts   (C, inverted)",                              -1, -1),
]


def load_chain(path: str | None) -> dict:
    if path:
        return json.load(open(path))
    with urllib.request.urlopen(CHAIN_URL, timeout=120) as r:
        return json.loads(r.read())


def parse_chain(chain: dict) -> list[tuple[str, str, float, dict]]:
    """(expiry YYMMDD, 'C'|'P', strike, contract) for every listed option."""
    out = []
    for o in chain["data"]["options"]:
        body = o["option"]
        # ...YYMMDD C|P SSSSSSSS  -- strike is the last 8 digits, x1000
        out.append((body[-15:-9], body[-9], int(body[-8:]) / 1000.0, o))
    return out


def gexbot_sample(zip_bytes: bytes, scope: str) -> dict:
    z = zipfile.ZipFile(io.BytesIO(zip_bytes))
    names = [n for n in z.namelist() if scope in n and n.endswith(".json.gz")]
    if not names:
        raise SystemExit(f"no {scope} in report: {z.namelist()}")
    samples = json.loads(gzip.decompress(z.read(names[0])))
    return max(samples, key=lambda s: s["timestamp"])


def infer_basis(gb_strikes: list[float], chain_strikes: set[float],
                spot_diff: float) -> float:
    """GexBot quotes NQ-futures-adjusted strikes; the chain quotes NDX ones.

    The two differ by a single constant basis. Recovering it by voting alone
    is not enough: the NDX grid is regular, so an offset 50 points wrong still
    lands every strike on *a* valid strike and ties the vote. So take the
    offsets that align the most strikes, then among those pick the one nearest
    the observed spot difference -- the basis is a carry spread of a few
    points, not fifty.
    """
    votes: collections.Counter = collections.Counter()
    for g in gb_strikes:
        for k in chain_strikes:
            if abs(g - k) < 150:
                votes[round(g - k, 2)] += 1
    if not votes:
        raise SystemExit("no chain strike within 150 points of the ladder")
    best = max(votes.values())
    if best < 0.5 * len(gb_strikes):
        raise SystemExit(f"basis unclear: best offset aligned {best}/{len(gb_strikes)}")
    tied = [o for o, n in votes.items() if n >= 0.95 * best]
    return min(tied, key=lambda o: abs(o - spot_diff))


def pearson(x: list[float], y: list[float]) -> float:
    mx, my = statistics.fmean(x), statistics.fmean(y)
    sxy = sum((a - mx) * (b - my) for a, b in zip(x, y))
    sxx = sum((a - mx) ** 2 for a in x)
    syy = sum((b - my) ** 2 for b in y)
    return sxy / math.sqrt(sxx * syy) if sxx and syy else float("nan")


def fit(x: list[float], y: list[float]) -> tuple[float, float]:
    r = pearson(x, y)
    sxx = sum(a * a for a in x)
    return r, (sum(a * b for a, b in zip(x, y)) / sxx if sxx else float("nan"))


def report(gb: dict, rows, expiry: str, basis: float) -> None:
    spot = gb["spot"]
    # strike row layout: [strike, gex_vol, gex_oi, priors]
    gb_vol = {round(r[0] - basis, 2): r[1] for r in gb["strikes"]}
    gb_oi = {round(r[0] - basis, 2): r[2] for r in gb["strikes"]}

    acc: dict[str, collections.defaultdict] = {
        k: collections.defaultdict(float)
        for k in ("c_oi", "p_oi", "c_vol", "p_vol")
    }
    for e, cp, k, o in rows:
        if e != expiry:
            continue
        side = "c" if cp == "C" else "p"
        acc[f"{side}_oi"][k] += o["gamma"] * o["open_interest"]
        acc[f"{side}_vol"][k] += o["gamma"] * o["volume"]

    for reading, gbmap, ck, pk in (
        ("open interest  (gex_oi  vs  Γ × OI)", gb_oi, "c_oi", "p_oi"),
        ("volume         (gex_vol vs  Γ × traded volume)", gb_vol, "c_vol", "p_vol"),
    ):
        C, P = acc[ck], acc[pk]
        ks = [k for k in sorted(set(gbmap) & (set(C) | set(P))) if C[k] or P[k]]
        y = [gbmap[k] for k in ks]
        print(f"\n{reading}   —   {len(ks)} strikes")
        print(f"  {'convention':<62} {'r':>8} {'r²':>7} {'scale':>10}")
        for name, sc, sp in CONVENTIONS:
            r, slope = fit([sc * C[k] + sp * P[k] for k in ks], y)
            print(f"  {name:<62} {r:>+7.3f} {r*r:>7.3f} {slope:>10,.0f}")

    # A matching *shape* only shows the sign convention. The fitted scale says
    # whether the quantity itself is the textbook one: notional gamma per 1%
    # move, Γ × OI × 100 × S² × 0.01, reported in millions of dollars.
    C, P = acc["c_oi"], acc["p_oi"]
    ks = [k for k in sorted(set(gb_oi) & (set(C) | set(P))) if C[k] or P[k]]
    _, slope = fit([C[k] - P[k] for k in ks], [gb_oi[k] for k in ks])
    textbook = 100 * spot * spot * 0.01 / 1e6
    print(f"\n  fitted scale under A: {slope:,.0f}   "
          f"Γ·OI·100·S²·0.01 in $m: {textbook:,.0f}   "
          f"({100*slope/textbook:.0f}% of textbook)")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--zip", required=True, help="a GexBot EOD report zip")
    ap.add_argument("--scope", default="gex_one",
                    help="only gex_one is reconstructable — see the module docstring")
    ap.add_argument("--chain", default=None, help="cached Cboe chain JSON")
    args = ap.parse_args()

    gb = gexbot_sample(open(args.zip, "rb").read(), args.scope)
    chain = load_chain(args.chain)
    rows = parse_chain(chain)

    when = dt.datetime.fromtimestamp(gb["timestamp"], dt.timezone.utc)
    print(f"{gb['ticker']} {args.scope} @ {when:%Y-%m-%d %H:%M}Z   "
          f"spot {gb['spot']:,.2f}   chain close {chain['data']['close']:,.2f}")

    basis = infer_basis([r[0] for r in gb["strikes"]], {r[2] for r in rows},
                        gb["spot"] - chain["data"]["close"])
    print(f"strike basis (GexBot NQ strike − NDX strike): {basis:+.2f}")

    # gex_one is the next expiry after 0DTE; the report says how far away it is.
    session = dt.date(when.year, when.month, when.day)
    target = session + dt.timedelta(days=gb["sec_min_dte"])
    expiry = target.strftime("%y%m%d")
    print(f"next expiry: {target} (sec_min_dte={gb['sec_min_dte']})")
    if expiry not in {r[0] for r in rows}:
        print(f"FATAL: {target} is not in the chain — it has already expired.",
              file=sys.stderr)
        return 1

    report(gb, rows, expiry, basis)
    return 0


if __name__ == "__main__":
    sys.exit(main())
