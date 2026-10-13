"""Monte Carlo pass/fail odds for the FTMO account: Daily Systems (tick backtest daily P/L, 'P|' lines) and the NAS bot
(daily R from data/nas_bot_daily_R_2021_2026.json x risk $). Block bootstrap: random 20-trading-day blocks of real
consecutive days (keeps losing streaks and same-day pairing of the two bots), glued together until pass or fail.
Start $97,421; pass at $110,000; fail at $90,000 (static floor) or a day worse than -$5,000. 20,000 runs each."""
import json, random, re, sys, statistics as st
UP = "/root/.claude/uploads/05dd4dd7-22e7-57bf-8cec-d6a0c9610eea"
DATA = "/home/user/CTrader-Bots/Vanessa Algo Bots/research/data/nas_bot_daily_R_2021_2026.json"

ds = {}
for f in ("3e7ac88f-DS_tick_data_20-23_log.txt", "6d9a4ab0-DS_tick_data_24-26_log.txt"):
    for line in open(f"{UP}/{f}"):
        m = re.search(r"Info \| P\|(\d{4}-\d\d-\d\d)\|(-?\d+)", line)
        if m: ds[m.group(1)] = float(m.group(2))
nas = json.load(open(DATA))
if isinstance(nas, dict) and "dates" in nas: nas = dict(zip(nas["dates"], nas["R"]))
elif isinstance(nas, dict) and len(nas) == 2 and all(isinstance(v, list) for v in nas.values()): nas = dict(zip(*nas.values()))
print(f"DS days {len(ds)} ({min(ds)}..{max(ds)}), total ${sum(ds.values()):,.0f}; NAS days {len(nas)} ({min(nas)}..{max(nas)})")

START, PASS, FLOOR, DAYLIM = 97421, 110000, 90000, -5000


def sim(days, runs=20000, block=20, seed=1):
    rnd = random.Random(seed); n = len(days); res = []; t_pass = []
    for _ in range(runs):
        bal = START; t = 0; out = None
        while out is None and t < 2000:
            s = rnd.randrange(0, n - block)
            for x in days[s:s + block]:
                t += 1; bal += x
                if x <= DAYLIM or bal <= FLOOR: out = "fail"; break
                if bal >= PASS: out = "pass"; t_pass.append(t); break
        res.append(out or "neither")
    p = res.count("pass") / runs; f = res.count("fail") / runs
    return p, f, (st.median(t_pass) if t_pass else None)


if __name__ == "__main__":
    # common calendar: every weekday that appears in either series inside 2021-01..2026-10
    allk = sorted(k for k in set(ds) | set(nas) if "2021-01-01" <= k <= "2026-10-31")
    print(f"combined calendar {len(allk)} days")
    dsonly = [ds[k] for k in sorted(ds)]
    p, f, md = sim(dsonly); print(f"Daily Systems alone ($13k/position, 2020-26):  pass {p:5.1%}  fail {f:5.1%}  median {md} trading days")
    for risk in (550, 450, 350):
        days = [ds.get(k, 0.0) + nas.get(k, 0.0) * risk for k in allk]
        p, f, md = sim(days); print(f"NAS ${risk} + Daily Systems:                   pass {p:5.1%}  fail {f:5.1%}  median {md} trading days")
        days = [nas.get(k, 0.0) * risk for k in allk]
        p, f, md = sim(days); print(f"NAS ${risk} alone:                              pass {p:5.1%}  fail {f:5.1%}  median {md} trading days")
