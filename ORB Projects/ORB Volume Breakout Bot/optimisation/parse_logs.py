#!/usr/bin/env python3
"""
Turn the raw cTrader backtest logs into a trade ledger plus a daily decision
table, so the bot's behaviour can be analysed rather than guessed at.

The logs are ~99.9% a single repeated line - a volume-filter rejection emitted on
every M1 bar where price sits beyond the ORB threshold - so they are streamed and
aggregated rather than loaded. What survives is small.

Usage:
    python parse_logs.py "2024 log.txt" "2025 log.txt" "2026 log.txt" --outdir results
"""
import argparse
import io
import os
import re
import sys
from collections import defaultdict

import pandas as pd

# 03/01/2025 14:31:00.003 | Info | [ORBV] 2025-01-03 14:31:00 <message>
LINE = re.compile(
    r"^(?P<stamp>\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2})\.\d+ \| \w+ \| "
    r"(?:\[ORBV\] (?P<botdt>[\d-]+ [\d:]+) )?(?P<msg>.*)$")

RE_ENTER = re.compile(
    r"TRADE ENTERED: (?P<side>\w+) (?P<sym>\S+) vol=(?P<vol>[\d.]+) "
    r"entry=(?P<entry>[\d.]+) SL=(?P<sl>[\d.]+) TP=(?P<tp>[\d.]+) "
    r"riskPips=(?P<risk>[\d.]+) label=(?P<label>\S+)")
RE_CLOSED = re.compile(
    r"POSITION CLOSED: (?P<label>\S+) reason=(?P<reason>\S+) "
    r"P/L=(?P<pl>-?[\d.]+) pips=(?P<pips>-?[\d.]+)")
RE_ORB = re.compile(
    r"ORB LOCKED: High=(?P<hi>[\d.]+) Low=(?P<lo>[\d.]+) Range=(?P<rng>[\d.]+) pips")
RE_VOL = re.compile(
    r"VOLUME FILTER: (?P<side>\w+) breakout at (?P<hhmm>\d{2}:\d{2}) rejected\. "
    r"vol=(?P<vol>[\d.]+) < required [\d.]+x avg\(\d+\)=(?P<req>[\d.]+)")
RE_NOTRADE = re.compile(r"NO TRADE TODAY: (?P<why>.+)")
RE_BLOCKED = re.compile(r"ENTRY BLOCKED: \w+ signal at [\d:]+ but (?P<why>.+)")
RE_TREND = re.compile(r"Trend filter blocked (?P<side>\w+): (?P<why>.+)")
RE_BE = re.compile(r"BREAK EVEN: SL moved to")
RE_TRAIL = re.compile(r"TRAIL: SL -> [\d.]+ \(locked (?P<locked>-?[\d.]+)R")
RE_EARLY = re.compile(r"EARLY RISK REDUCTION: SL moved to")


def parse(path):
    trades, closes, days = {}, [], defaultdict(dict)
    counters = defaultdict(lambda: defaultdict(int))
    vol_gap = defaultdict(list)

    with io.open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            m = LINE.match(line)
            if not m:
                continue
            msg = m.group("msg")
            day = m.group("stamp")[:10]
            day = f"{day[6:10]}-{day[3:5]}-{day[0:2]}"  # dd/mm/yyyy -> ISO

            # --- the hot path: one rejection per bar, aggregate only ---
            v = RE_VOL.search(msg)
            if v:
                counters[day]["vol_rejects"] += 1
                req = float(v.group("req"))
                if req > 0:
                    # how close did it get? 1.0 == would have passed
                    vol_gap[day].append(float(v.group("vol")) / req)
                continue

            e = RE_ENTER.search(msg)
            if e:
                d = e.groupdict()
                d.update(date=day, entry_time=m.group("stamp")[11:])
                trades[d["label"]] = d
                continue

            c = RE_CLOSED.search(msg)
            if c:
                d = c.groupdict()
                d.update(exit_date=day, exit_time=m.group("stamp")[11:])
                closes.append(d)
                continue

            o = RE_ORB.search(msg)
            if o:
                days[day].update(orb_hi=float(o.group("hi")),
                                 orb_lo=float(o.group("lo")),
                                 orb_range=float(o.group("rng")))
                continue

            for rx, key in ((RE_NOTRADE, "no_trade"), (RE_BLOCKED, "blocked"),
                            (RE_TREND, "trend_blocked")):
                mm = rx.search(msg)
                if mm:
                    counters[day][key] += 1
                    days[day].setdefault(key + "_why", mm.group("why")[:60])
                    break
            else:
                if RE_BE.search(msg):
                    counters[day]["be"] += 1
                elif RE_EARLY.search(msg):
                    counters[day]["early"] += 1
                else:
                    t = RE_TRAIL.search(msg)
                    if t:
                        counters[day]["trail"] += 1
                        days[day]["max_locked_R"] = max(
                            days[day].get("max_locked_R", 0.0), float(t.group("locked")))

    # --- stitch entries to exits by label ---
    by_label = {c["label"]: c for c in closes}
    rows = []
    for label, t in trades.items():
        c = by_label.get(label, {})
        rows.append({
            "date": t["date"], "entry_time": t["entry_time"], "side": t["side"],
            "vol": float(t["vol"]), "entry": float(t["entry"]), "sl": float(t["sl"]),
            "risk_pts": float(t["risk"]),
            "exit_time": c.get("exit_time"), "reason": c.get("reason"),
            "pl": float(c["pl"]) if c else None,
            "pips": float(c["pips"]) if c else None,
            "be": counters[t["date"]].get("be", 0),
            "trail": counters[t["date"]].get("trail", 0),
            "early": counters[t["date"]].get("early", 0),
            "max_locked_R": days[t["date"]].get("max_locked_R"),
        })
    tdf = pd.DataFrame(rows).sort_values("date").reset_index(drop=True)

    drows = []
    for day, info in days.items():
        r = {"date": day}
        r.update(info)
        r.update(counters[day])
        g = vol_gap.get(day, [])
        if g:
            r["vol_best_ratio"] = max(g)   # closest any bar came to passing
        drows.append(r)
    ddf = pd.DataFrame(drows).sort_values("date").reset_index(drop=True)
    return tdf, ddf


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("logs", nargs="+")
    ap.add_argument("--outdir", default="results")
    a = ap.parse_args()
    os.makedirs(a.outdir, exist_ok=True)

    all_t, all_d = [], []
    for p in a.logs:
        if not os.path.isfile(p):
            sys.exit("missing: " + p)
        t, d = parse(p)
        tag = os.path.basename(p).split()[0]
        t["log"] = tag
        d["log"] = tag
        print(f"{tag}: {len(t):3d} trades, {len(d):3d} days with an ORB lock")
        all_t.append(t)
        all_d.append(d)

    T = pd.concat(all_t, ignore_index=True)
    D = pd.concat(all_d, ignore_index=True)
    T.to_csv(os.path.join(a.outdir, "trades.csv"), index=False)
    D.to_csv(os.path.join(a.outdir, "days.csv"), index=False)
    print(f"\n-> {a.outdir}/trades.csv  ({len(T)} rows)")
    print(f"-> {a.outdir}/days.csv    ({len(D)} rows)")


if __name__ == "__main__":
    main()
