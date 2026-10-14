"""Pre-FOMC announcement drift (Lucca & Moench 2015), pre-registered 15 Oct 2026. Long the index CFD from 14:00 New York
on the day before the scheduled announcement (= meeting day 1) to 14:00 New York on announcement day (just before the
statement). Scheduled meetings 2014-2026 from federalreserve.gov (2020 March cancelled; unscheduled ones excluded).
Cost 0.025% + one night of swap (5%/yr). Pass: positive after costs in 2014-20, 2021-23 and 2024-26, avg >= +0.05%."""
import csv, statistics as st
from collections import defaultdict
from datetime import datetime, timezone, date, timedelta

R0 = "/home/user/CTrader-Bots/Vanessa Algo Bots/research"
MEET = """2014-01-28 2014-03-18 2014-04-29 2014-06-17 2014-07-29 2014-09-16 2014-10-28 2014-12-16
2015-01-27 2015-03-17 2015-04-28 2015-06-16 2015-07-28 2015-09-16 2015-10-27 2015-12-15
2016-01-26 2016-03-15 2016-04-26 2016-06-14 2016-07-26 2016-09-20 2016-11-01 2016-12-13
2017-01-31 2017-03-14 2017-05-02 2017-06-13 2017-07-25 2017-09-19 2017-10-31 2017-12-12
2018-01-30 2018-03-20 2018-05-01 2018-06-12 2018-07-31 2018-09-25 2018-11-07 2018-12-18
2019-01-29 2019-03-19 2019-04-30 2019-06-18 2019-07-30 2019-09-17 2019-10-29 2019-12-10
2020-01-28 2020-04-28 2020-06-09 2020-07-28 2020-09-15 2020-11-04 2020-12-15
2021-01-26 2021-03-16 2021-04-27 2021-06-15 2021-07-27 2021-09-21 2021-11-02 2021-12-14
2022-01-25 2022-03-15 2022-05-03 2022-06-14 2022-07-26 2022-09-20 2022-11-01 2022-12-13
2023-01-31 2023-03-21 2023-05-02 2023-06-13 2023-07-25 2023-09-19 2023-10-31 2023-12-12
2024-01-30 2024-03-19 2024-04-30 2024-06-11 2024-07-30 2024-09-17 2024-11-06 2024-12-17
2025-01-28 2025-03-18 2025-05-06 2025-06-17 2025-07-29 2025-09-16 2025-10-28 2025-12-09
2026-01-27 2026-03-17 2026-04-28 2026-06-16 2026-07-28 2026-09-15""".split()   # meeting day 1


def ny_offset(d):   # hours to add to New York time to get UTC
    mar = date(d.year, 3, 1); start = mar + timedelta(days=(6 - mar.weekday()) % 7 + 7)
    nov = date(d.year, 11, 1); end = nov + timedelta(days=(6 - nov.weekday()) % 7)
    return 4 if start <= d < end else 5


def bars(m):
    b = {}
    for r in csv.DictReader(open(f"{R0}/data/factory_h1/{m}_h1.csv")):
        t = datetime.fromtimestamp(int(r["timestamp_ms"]) / 1000, timezone.utc)
        b[(t.date(), t.hour)] = (float(r["open"]), float(r["close"]))
    return b


def run(m, cost=0.00025, swap=0.05 / 365):
    b = bars(m); out = []
    for s in MEET:
        d1 = date.fromisoformat(s); d2 = d1 + timedelta(days=1)
        h1 = 14 + ny_offset(d1); h2 = 14 + ny_offset(d2)
        a = b.get((d1, h1)); z = b.get((d2, h2 - 1))
        if not a or not z: continue
        e, x = a[0], z[1]
        out.append((d1, (x - e) / e - cost - swap, m))
    return out


def report(name, T):
    by = defaultdict(list)
    for d, r, _ in T: by["2014-20" if d.year <= 2020 else "2021-23" if d.year <= 2023 else "2024-26"].append(r)
    al = [r for _, r, _ in T]
    print(f"  {name:34s} n={len(al)} avg {st.mean(al)*100:+.3f}% win {sum(r>0 for r in al)/len(al):.0%} | "
          + " | ".join(f"{p} {st.mean(v)*100:+.3f}% ({len(v)})" for p, v in sorted(by.items())))


if __name__ == "__main__":
    for net in (True, False):
        print("NET of FTMO costs" if net else "GROSS")
        for m in ("us500", "nas100", "us30"):
            report(m, run(m) if net else run(m, 0, 0))
        report("all 9 indices", [t for m in ("us500", "nas100", "us30", "ger40", "uk100", "fra40", "eustx50", "aus200", "hk50")
                                 for t in (run(m) if net else run(m, 0, 0))])
