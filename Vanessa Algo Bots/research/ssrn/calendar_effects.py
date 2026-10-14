"""SSRN / academic calendar effects on FTMO index CFDs. Pre-registered 15 Oct 2026: rules taken from the papers,
no tuning. Costs: spread+commission 0.025% of price per round trip, swap 5%/yr per night held (as the factory).
Results split: 2014-2020 / 2021-2023 / 2024-2026. Pass: positive after costs in all three periods,
average >= +0.05% per trade, and positive on most indices.
1. TURN OF THE MONTH (Lakonishok & Smidt 1988; McConnell & Xu 2008; Carchano & Pardo): long from the close of
   the second-to-last trading day of the month to the close of the 3rd trading day of the next month.
2. OPTION-EXPIRY WEEK (opex week, US monthly options expire on the 3rd Friday): long from the close of the Friday
   before to the close of expiry Friday. US indices only (US500, US100, US30).
3. EUROPEAN-OPEN HOUR (Bondarenko & Muravyev, 'Market Return Around the Clock'): long the US index CFD over the
   hour(s) around the European cash open; tested 06:00-08:00 and 07:00-08:00 UTC (London 07:00/08:00 local in
   winter/summer is ~07:00-08:00 UTC) on 1-hour bars, every trading day. No swap (intraday)."""
import csv, sys
from collections import defaultdict
from datetime import datetime, timezone, date, timedelta
import statistics as st

R0 = "/home/user/CTrader-Bots/Vanessa Algo Bots/research"
COST, SWAP = 0.00025, 0.05 / 365
IDX = ["us500", "nas100", "us30", "ger40", "uk100", "fra40", "eustx50", "aus200", "hk50"]
sys.path.insert(0, R0 + "/factory")
import factory_d1 as F1


def period(d): return "2014-20" if d.year <= 2020 else ("2021-23" if d.year <= 2023 else "2024-26")


def report(name, trades):
    by = defaultdict(list); mk = defaultdict(list)
    for d, r, m in trades: by[period(d)].append(r); mk[m].append(r)
    alls = [r for _, r, _ in trades]
    pos_m = sum(st.mean(v) > 0 for v in mk.values())
    s = " | ".join(f"{p} {st.mean(by[p]) * 100:+.3f}% ({len(by[p])})" for p in ("2014-20", "2021-23", "2024-26") if by[p])
    ok = all(st.mean(by[p]) > 0 for p in ("2014-20", "2021-23", "2024-26") if by[p]) and st.mean(alls) >= 0.0005 and pos_m > len(mk) / 2
    print(f"  {name:44s} n={len(alls):4d} avg {st.mean(alls) * 100:+.3f}% win {sum(r > 0 for r in alls) / len(alls):.0%} | {s} | "
          f"markets+ {pos_m}/{len(mk)} | {'PASS' if ok else 'fail'}")


def daily(m):
    dates, o, h, l, c = F1.load(m)
    return dates, c


def tom(m):
    dates, c = daily(m); out = []
    months = defaultdict(list)
    for i, d in enumerate(dates): months[(d.year, d.month)].append(i)
    keys = sorted(months)
    for k0, k1 in zip(keys, keys[1:]):
        a, b = months[k0], months[k1]
        if len(a) < 3 or len(b) < 3: continue
        i0, i1 = a[-2], b[2]
        e, x = c[i0], c[i1]; nights = (dates[i1] - dates[i0]).days
        if dates[i0].year >= 2014:
            out.append((dates[i0], (x - e) / e - COST - SWAP * nights, m))
    return out


def opex(m):
    dates, c = daily(m); idx = {d: i for i, d in enumerate(dates)}; out = []
    for y in range(2014, 2027):
        for mo in range(1, 13):
            d = date(y, mo, 1); fr = [d + timedelta(days=k) for k in range(31) if (d + timedelta(days=k)).month == mo and (d + timedelta(days=k)).weekday() == 4]
            if len(fr) < 3: continue
            exp, before = fr[2], fr[2] - timedelta(days=7)
            if exp in idx and before in idx:
                i0, i1 = idx[before], idx[exp]; e, x = c[i0], c[i1]
                out.append((before, (x - e) / e - COST - SWAP * 7, m))
    return out


def eu_open(m, h0, h1):
    rows = list(csv.DictReader(open(f"{R0}/data/factory_h1/{m}_h1.csv")))
    bars = {}
    for r in rows:
        t = datetime.fromtimestamp(int(r["timestamp_ms"]) / 1000, timezone.utc)
        bars[(t.date(), t.hour)] = (float(r["open"]), float(r["close"]))
    out = []
    for (d, hr), (o, c) in bars.items():
        if hr != h0 or d.weekday() > 4: continue
        end = bars.get((d, h1 - 1))
        if end is None: continue
        out.append((d, (end[1] - o) / o - COST, m))
    return sorted(out)


if __name__ == "__main__":
    print("1. Turn of the month (9 indices)")
    T = [t for m in IDX for t in tom(m)]; report("TOM: close day -2 -> close day +3", T)
    print("2. Option-expiry week (US indices)")
    T = [t for m in ("us500", "nas100", "us30") for t in opex(m)]; report("Opex week: Fri before -> expiry Fri", T)
    print("3. European-open hours, US indices (1-hour bars, 2014-2026)")
    for h0, h1 in ((6, 8), (7, 8), (6, 9)):
        T = [t for m in ("us500", "nas100", "us30") for t in eu_open(m, h0, h1)]
        report(f"EU open {h0:02d}:00-{h1:02d}:00 UTC long", T)
