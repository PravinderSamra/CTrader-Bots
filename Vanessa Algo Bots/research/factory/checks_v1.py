"""Reviewer checks on the v1 shortlist: (1) edge above simply being long (baseline = enter EVERY day, same exit),
(2) correlation with the live bots (Daily Systems daily P/L, NAS bot daily R)."""
import json, re, statistics as st
from collections import defaultdict
import numpy as np
import factory_d1 as F

SL = json.load(open("results_v1/shortlist.json"))
ds = {}
for f in ("3e7ac88f-DS_tick_data_20-23_log.txt", "6d9a4ab0-DS_tick_data_24-26_log.txt"):
    for line in open(f"/root/.claude/uploads/05dd4dd7-22e7-57bf-8cec-d6a0c9610eea/{f}"):
        m = re.search(r"Info \| P\|(\d{4}-\d\d-\d\d)\|(-?\d+)", line)
        if m: ds[m.group(1)] = float(m.group(2))
nas = json.load(open(F.R0 + "/data/nas_bot_daily_R_2021_2026.json"))
if isinstance(nas, dict) and len(nas) == 2 and all(isinstance(v, list) for v in nas.values()): nas = dict(zip(*nas.values()))


def parse(raw):
    ek, ep, f, xk, xp, side = raw
    ep = eval(ep) if ek in ("MAX",) or "." in ep else int(ep)
    if xk == "STOPTGT": xp = eval(xp)
    elif xk in ("MR",): xp = xp
    else: xp = int(xp)
    return (ek, ep, f, xk, xp, int(side))


def corr(d1, d2, lo="2020-11-09"):
    keys = sorted(k for k in set(d1) | set(d2) if k >= lo)
    a = [d1.get(k, 0) for k in keys]; b = [d2.get(k, 0) for k in keys]
    return st.correlation(a, b) if len(keys) > 30 else 0


if __name__ == "__main__":
    F._init("ALL")
    base_cache = {}
    for row in SL:
        spec = parse(row["raw"]); g = row["group"]
        ms = F._M[g]
        trades = []; base = []
        for m in ms:
            sig = F.entry_signal(m, spec[0], spec[1], spec[5]) & F.filt(m, spec[2], spec[5])
            trades += F.simulate(m, sig, spec[3], spec[4], spec[5])
            key = (g, m.name, spec[3], str(spec[4]), spec[5])
            if key not in base_cache:
                base_cache[key] = F.simulate(m, np.ones(len(m.c), bool), spec[3], spec[4], spec[5])
            base += base_cache[key]
        bc = [t[1] for t in trades if t[2] in "BC"]; bb = [t[1] for t in base if t[2] in "BC"]
        d = defaultdict(float)
        for t in trades: d[t[0].isoformat()] += t[1]
        print(f"{g:3s} {row['spec']:34s} strat {st.mean(bc):+.3f}R  vs always-in {st.mean(bb):+.3f}R  edge {st.mean(bc)-st.mean(bb):+.3f}R | "
              f"corr DS {corr(d, ds):+.2f}  corr NAS {corr(d, nas, '2021-01-01'):+.2f}")
