import csv, collections
rows = list(csv.DictReader(open("us500_trades.csv")))
for r in rows:
    for k in ("net","gross","comm","r","risk_usd"): r[k] = float(r[k])
    r["year"] = int(r["year"])

sheet_20R = {2022:2851, 2023:600, 2024:932, 2025:2539, 2026:1999}
print(f"{'year':<6}{'sheet':>8}{'log gross':>11}{'log net':>10}{'commission':>12}{'gross-sheet':>13}")
tg=tn=tc=0
for y in sorted(sheet_20R):
    g = [x for x in rows if x["year"]==y]
    gross = sum(x["gross"] for x in g); net = sum(x["net"] for x in g); comm = sum(x["comm"] for x in g)
    tg+=gross; tn+=net; tc+=comm
    print(f"{y:<6}{sheet_20R[y]:>8}{gross:>11.0f}{net:>10.0f}{comm:>12.0f}{gross-sheet_20R[y]:>13.0f}")
print(f"{'ALL':<6}{sum(sheet_20R.values()):>8}{tg:>11.0f}{tn:>10.0f}{tc:>12.0f}{tg-sum(sheet_20R.values()):>13.0f}")
print(f"\ncommission per trade: ${abs(tc)/len(rows):.2f}   as % of gross profit: {100*abs(tc)/tg:.1f}%")
