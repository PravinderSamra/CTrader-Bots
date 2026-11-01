"""Parse an ORB Volume Breakout v3.2 backtest/live log into trades.

The bot does not print the H| history block the daily bots do; it logs each
trade as it happens instead:

    TRADE ENTERED: Sell US100.cash vol=6.66 entry=29396.63 SL=... TP=... riskPips=60.0
    POSITION CLOSED: <label> reason=StopLoss P/L=-404.60 pips=-60.8
    L|date|balance|risk|losing days|cut        (once per day, the risk ladder)

`reason` is the thing worth having: it says WHY each trade ended, which is the
question the whole exit discussion turns on.
"""
import re, sys, collections, statistics as st

ENT = re.compile(r"TRADE ENTERED: (\w+) (\S+) vol=([\d.]+) entry=([\d.]+) SL=([\d.]+) TP=([\d.]+)")
CLO = re.compile(r"POSITION CLOSED: (\S+) reason=(\w+) P/L=(-?[\d.]+) pips=(-?[\d.]+)")
LAD = re.compile(r"\| Info \| L\|(\S+?)\|([\d.]+)\|(\d+)\|(\d+)\|(\S*)")
ADD = re.compile(r"ADD", re.I)


def parse(path):
    trades, ladder = [], []
    for ln in open(path, encoding="utf-8", errors="replace"):
        ts = ln.split(" | ")[0].strip()
        m = ENT.search(ln)
        if m:
            trades.append({"t_in": ts, "side": m.group(1), "sym": m.group(2),
                           "vol": float(m.group(3)), "entry": float(m.group(4)),
                           "sl": float(m.group(5)), "tp": float(m.group(6)),
                           "open": True})
            continue
        m = CLO.search(ln)
        if m:
            trades.append({"t_out": ts, "label": m.group(1), "reason": m.group(2),
                           "pl": float(m.group(3)), "pips": float(m.group(4)),
                           "open": False})
            continue
        m = LAD.search(ln)
        if m:
            ladder.append({"day": m.group(1), "bal": float(m.group(2)),
                           "risk": int(m.group(3)), "losing": int(m.group(4)),
                           "cut": m.group(5)})
    return trades, ladder


if __name__ == "__main__":
    path = sys.argv[1]
    tr, lad = parse(path)
    closes = [t for t in tr if not t["open"]]
    opens = [t for t in tr if t["open"]]
    net = sum(t["pl"] for t in closes)
    print(f"{path.split('/')[-1]}")
    print(f"  entries logged {len(opens)}   closes logged {len(closes)}   net {net:+,.2f}")
    if lad:
        print(f"  ladder: balance {lad[0]['bal']:,.2f} -> {lad[-1]['bal']:,.2f}"
              f"   risk {lad[0]['risk']} -> {lad[-1]['risk']}")
    by = collections.Counter(t["reason"] for t in closes)
    print(f"\n  why trades ended:")
    for r, n in by.most_common():
        sub = [t["pl"] for t in closes if t["reason"] == r]
        print(f"    {r:<22}{n:>4}   net {sum(sub):>+11,.2f}   median {st.median(sub):>+9,.2f}")
    wins = [t for t in closes if t["pl"] > 0]
    print(f"\n  {len(wins)}/{len(closes)} profitable = {len(wins)/max(1,len(closes)):.0%}")
    if len(closes) <= 60:
        print(f"\n  {'closed':<22}{'reason':<20}{'pips':>8}{'P/L':>11}")
        for t in closes:
            print(f"  {t['t_out']:<22}{t['reason']:<20}{t['pips']:>+8.1f}{t['pl']:>+11,.2f}")
