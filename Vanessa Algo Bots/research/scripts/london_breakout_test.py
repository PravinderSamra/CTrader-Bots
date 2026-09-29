"""London-open range breakout test - see ../LONDON_BREAKOUT_TEST_PLAN.md (pre-registered).

Run from the repo root:  python3 "Vanessa Algo Bots/research/scripts/london_breakout_test.py"
Standard library only.
"""
import bisect
import csv
import datetime as dt
import glob
import math
import random
import statistics as st
from collections import defaultdict
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[3]
RES = ROOT / "Vanessa Algo Bots/research/results"
UK = ZoneInfo("Europe/London")
UTC = dt.timezone.utc

TRAIN_END = dt.date(2024, 6, 30)
GRID = [(0.25, 2.0), (0.25, 3.5), (0.40, 2.0), (0.40, 3.5)]
VOL_MULT, VOL_LOOKBACK = 1.2, 20
RANGE_END = dt.time(7, 0)
SIG_FIRST_OPEN, SIG_LAST_OPEN = dt.time(8, 0), dt.time(10, 55)   # bar closes 08:05 .. 11:00
EXIT_AT = dt.time(20, 55)

INSTRUMENTS = {
    "XAUUSD": {"files": sorted(glob.glob(str(ROOT / "XAUUSD historical Pricing data/data/XAUUSD_M_1_*.csv"))),
               "fine_minutes": 1, "cost": {"base": 0.35, "stress": 0.70}, "unit": "$/oz"},
    "EURUSD": {"files": sorted(glob.glob(str(ROOT / "Vanessa Algo Bots/research/data/eurusd_m5/EURUSD_M_5_*.csv"))),
               "fine_minutes": 5, "cost": {"base": 0.00010, "stress": 0.00020}, "unit": "price"},
}


def load(files):
    """[(utc_datetime, o, h, l, c, v)] sorted."""
    rows = []
    for f in files:
        for r in csv.DictReader(open(f)):
            t = dt.datetime.fromisoformat(r["datetime"].replace("Z", "+00:00"))
            rows.append((t, float(r["open"]), float(r["high"]), float(r["low"]), float(r["close"]), float(r["volume"])))
    rows.sort(key=lambda x: x[0])
    return rows


def to_m5(fine):
    out, cur = [], None
    for t, o, h, l, c, v in fine:
        b = t.replace(minute=t.minute - t.minute % 5, second=0, microsecond=0)
        if cur and cur[0] == b:
            cur[2] = max(cur[2], h); cur[3] = min(cur[3], l); cur[4] = c; cur[5] += v
        else:
            if cur:
                out.append(tuple(cur))
            cur = [b, o, h, l, c, v]
    if cur:
        out.append(tuple(cur))
    return out


def backtest(m5, fine, stop_mult, r_target, cost):
    """Return list of trades: dict(date, side, entry_time, entry, stop, target, exit, exit_time, r_gross, r_net)."""
    by_day = defaultdict(list)
    for i, b in enumerate(m5):
        lt = b[0].astimezone(UK)
        if lt.weekday() < 5:
            by_day[lt.date()].append(i)
    fine_times = [x[0] for x in fine]

    day_ranges = {}
    for d, idx in by_day.items():
        sess = [m5[i] for i in idx if m5[i][0].astimezone(UK).time() < dt.time(21, 0)]
        if len(sess) >= 150:
            day_ranges[d] = max(b[2] for b in sess) - min(b[3] for b in sess)
    days = sorted(by_day)
    trades = []
    for k, d in enumerate(days):
        prior = [day_ranges[x] for x in days[max(0, k - 30):k] if x in day_ranges][-20:]
        if len(prior) < 20:
            continue
        idx = by_day[d]
        asia = [m5[i] for i in idx if m5[i][0].astimezone(UK).time() < RANGE_END]
        if len(asia) < 50:                                   # need most of the 84 bars
            continue
        rh, rl = max(b[2] for b in asia), min(b[3] for b in asia)
        stop_dist = stop_mult * st.median(prior)
        for i in idx:
            lt = m5[i][0].astimezone(UK).time()
            if lt < SIG_FIRST_OPEN or lt > SIG_LAST_OPEN or i < VOL_LOOKBACK or i + 1 >= len(m5):
                continue
            close, vol = m5[i][4], m5[i][5]
            side = 1 if close > rh else (-1 if close < rl else 0)
            if not side:
                continue
            avg = sum(m5[j][5] for j in range(i - VOL_LOOKBACK, i)) / VOL_LOOKBACK
            if avg <= 0 or vol < VOL_MULT * avg:
                continue
            nb = m5[i + 1]
            if nb[0].astimezone(UK).date() != d:
                break
            entry_t, entry = nb[0], nb[1]
            sl = entry - side * stop_dist
            tp = entry + side * r_target * stop_dist
            exit_px, exit_t = None, None
            j = bisect.bisect_left(fine_times, entry_t)
            while j < len(fine):
                t, o, h, l, c, v = fine[j]
                lt2 = t.astimezone(UK)
                if lt2.date() != d or lt2.time() >= EXIT_AT:
                    break
                hit_sl = (l <= sl) if side == 1 else (h >= sl)
                hit_tp = (h >= tp) if side == 1 else (l <= tp)
                if hit_sl:
                    exit_px, exit_t = sl, t
                    break
                if hit_tp:
                    exit_px, exit_t = tp, t
                    break
                j += 1
            if exit_px is None:
                last = fine[max(j - 1, 0)]
                exit_px, exit_t = last[4], last[0]
            r_gross = side * (exit_px - entry) / stop_dist
            trades.append({"date": d, "side": "long" if side == 1 else "short",
                           "entry_time": entry_t.astimezone(UK).strftime("%H:%M"), "entry": entry,
                           "stop": sl, "target": tp, "exit": exit_px,
                           "exit_time": exit_t.astimezone(UK).strftime("%H:%M"),
                           "range_high": rh, "range_low": rl, "stop_dist": stop_dist,
                           "r_gross": r_gross, "cost_r": cost / stop_dist})
            break
    return trades


def summarize(rs, rng):
    n = len(rs)
    if n < 2:
        return None
    m, sd = st.mean(rs), st.stdev(rs)
    boots = sum(1 for _ in range(10000) if st.mean(rng.choices(rs, k=n)) <= 0) / 10000
    gw, gl = sum(x for x in rs if x > 0), -sum(x for x in rs if x < 0)
    top5 = sum(sorted(rs)[:-5]) if n > 5 else float("nan")
    return {"n": n, "mean": m, "t": m / (sd / math.sqrt(n)), "win": 100 * sum(x > 0 for x in rs) / n,
            "pf": gw / gl if gl else float("inf"), "p_le0": boots, "total": sum(rs), "minus_top5": top5}


def fmt(s):
    return (f"| {s['n']} | {s['mean']:+.3f} | {s['t']:+.2f} | {s['win']:.0f}% | {s['pf']:.2f} | "
            f"{s['total']:+.1f} | {s['minus_top5']:+.1f} | {s['p_le0']:.3f} |")


HDR = "| Trades | Mean R | t | Win % | PF | Total R | Total minus top 5 | P(edge <= 0) |\n|---|---|---|---|---|---|---|---|"


def main():
    out = ["# London-open range breakout - results\n",
           "Generated by `research/scripts/london_breakout_test.py`. Plan: `research/LONDON_BREAKOUT_TEST_PLAN.md`.\n"]
    P = out.append
    for name, cfg in INSTRUMENTS.items():
        if not cfg["files"]:
            P(f"## {name}: no data files found, skipped\n")
            continue
        rng = random.Random(7)
        fine = load(cfg["files"])
        m5 = to_m5(fine) if cfg["fine_minutes"] == 1 else fine
        P(f"## {name} ({fine[0][0]:%Y-%m-%d} .. {fine[-1][0]:%Y-%m-%d})\n")
        P("### Training 2021-07 .. 2024-06, base cost\n")
        P("| Stop x median day range | Target " + HDR.split("\n")[0] + "\n|---|---" + HDR.split("\n")[1])
        best, best_key = None, None
        results = {}
        for S, R in GRID:
            tr = backtest(m5, fine, S, R, cfg["cost"]["base"])
            results[(S, R)] = tr
            rs = [t["r_gross"] - t["cost_r"] for t in tr if dt.date(2021, 7, 1) <= t["date"] <= TRAIN_END]
            s = summarize(rs, rng)
            P(f"| {S} | {R} " + fmt(s))
            if s["n"] >= 150 and (best is None or s["mean"] > best["mean"] + 1e-12):
                best, best_key = s, (S, R)
        S, R = best_key
        P(f"\n**Chosen by the pre-registered rule: stop {S} x median day range, target {R}R.**\n")

        tr = results[best_key]
        test = [t for t in tr if t["date"] > TRAIN_END]
        P(f"### TEST {test[0]['date']} .. {test[-1]['date']} (run once)\n")
        P("| Cost " + HDR.split("\n")[0] + "\n|---" + HDR.split("\n")[1])
        base = [t["r_gross"] - t["cost_r"] for t in test]
        stress = [t["r_gross"] - t["cost_r"] * 2 for t in test]
        sb, ss = summarize(base, rng), summarize(stress, rng)
        P("| base " + fmt(sb))
        P("| stress " + fmt(ss))
        halves = defaultdict(list)
        for t in test:
            halves[f"{t['date'].year} H{1 if t['date'].month <= 6 else 2}"].append(t["r_gross"] - t["cost_r"])
        P("\n| Half-year | Trades | Net R |\n|---|---|---|")
        neg = 0
        for h in sorted(halves):
            neg += sum(halves[h]) < 0
            P(f"| {h} | {len(halves[h])} | {sum(halves[h]):+.2f} |")
        checks = [sb["mean"] > 0 and sb["p_le0"] < 0.05, neg <= 1, sb["minus_top5"] > 0, ss["mean"] > 0]
        P(f"\nCriteria: edge {'PASS' if checks[0] else 'FAIL'}, half-years {'PASS' if checks[1] else 'FAIL'}, "
          f"minus top 5 {'PASS' if checks[2] else 'FAIL'}, stress cost {'PASS' if checks[3] else 'FAIL'} "
          f"-> **{'PASS' if all(checks) else 'FAIL'}**\n")

        with open(RES / f"london_breakout_{name.lower()}_trades.csv", "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(tr[0].keys()) + ["period"])
            w.writeheader()
            for t in tr:
                w.writerow({**t, "period": "test" if t["date"] > TRAIN_END else "train"})
    text = "\n".join(out)
    (RES / "LONDON_BREAKOUT_RAW.md").write_text(text + "\n")
    print(text)


if __name__ == "__main__":
    main()
