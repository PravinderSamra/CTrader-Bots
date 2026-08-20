import re, csv, collections, datetime as dt

LOG = "us500log/US500 2022-26log.txt"

ent_re = re.compile(
    r"TRADE ENTERED: (?P<side>\w+) (?P<sym>\S+) vol=(?P<vol>[\d.]+) entry=(?P<entry>[\d.]+) "
    r"SL=(?P<sl>[\d.]+) TP=(?P<tp>[\d.]+) riskPips=(?P<riskpips>[\d.]+) label=(?P<label>\S+)")
cls_re = re.compile(
    r"CLOSE_DIAG label=(?P<label>\S+) reason=(?P<reason>\S+) net=(?P<net>-?[\d.]+) "
    r"gross=(?P<gross>-?[\d.]+) commission=(?P<comm>-?[\d.]+) swap=(?P<swap>-?[\d.]+) "
    r"pips=(?P<pips>-?[\d.]+) entry=(?P<entry>[\d.]+) balance=(?P<bal>-?[\d.]+)")
ts_re = re.compile(r"^(\d{2})/(\d{2})/(\d{4}) (\d{2}):(\d{2}):(\d{2})")

def ts(line):
    m = ts_re.match(line)
    if not m: return None
    d, mo, y, H, M, S = map(int, m.groups())
    return dt.datetime(y, mo, d, H, M, S)

entries, closes = [], []
be = rr = trail = 0
for line in open(LOG, encoding="utf-8", errors="replace"):
    if "TRADE ENTERED:" in line:
        m = ent_re.search(line)
        if m: entries.append((ts(line), m.groupdict()))
    elif "CLOSE_DIAG" in line:
        m = cls_re.search(line)
        if m: closes.append((ts(line), m.groupdict()))
    elif "BREAK EVEN" in line: be += 1
    elif "EARLY RISK REDUCTION" in line: rr += 1
    elif "TRAIL:" in line: trail += 1

print(f"entries={len(entries)} closes={len(closes)} BE_moves={be} riskReduction_moves={rr} trail={trail}")
labels_e = [e[1]["label"] for e in entries]
print(f"distinct entry labels={len(set(labels_e))}  (duplicates => multiple trades same day)")

# pair sequentially: the bot holds at most one position at a time here
assert len(entries) == len(closes), "unbalanced"
rows = []
for (et, e), (ct, c) in zip(entries, closes):
    if e["label"] != c["label"]:
        print("LABEL MISMATCH", e["label"], c["label"]); break
    vol = float(e["vol"]); riskpips = float(e["riskpips"])
    risk_usd = riskpips * vol                     # $1 per pip per unit volume
    net = float(c["net"])
    rows.append(dict(
        entry_time=et, close_time=ct, year=et.year, side=e["side"],
        vol=vol, entry=float(e["entry"]), sl=float(e["sl"]), tp=float(e["tp"]),
        riskpips=riskpips, risk_usd=risk_usd, reason=c["reason"],
        net=net, gross=float(c["gross"]), comm=float(c["comm"]),
        pips=float(c["pips"]), balance=float(c["bal"]),
        r=net / risk_usd if risk_usd else 0.0))

with open("us500_trades.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)

risks = [r["risk_usd"] for r in rows]
risks.sort()
print(f"\nrisk per trade $: min={risks[0]:.2f} median={risks[len(risks)//2]:.2f} max={risks[-1]:.2f}")

# what config is this? reward:risk implied by TP distance
rr_imp = [abs(r['tp']-r['entry'])/r['riskpips'] for r in rows]
rr_imp.sort()
print(f"implied TP in R: min={rr_imp[0]:.1f} median={rr_imp[len(rr_imp)//2]:.1f} max={rr_imp[-1]:.1f}")

print("\n=== P&L BY YEAR (net, after commission) ===")
print(f"{'year':<6}{'trades':>7}{'net $':>10}{'total R':>9}{'win%':>7}{'avgWin':>8}{'avgLoss':>9}{'expR':>7}")
by_year = collections.defaultdict(list)
for r in rows: by_year[r["year"]].append(r)
for y in sorted(by_year):
    g = by_year[y]
    wins = [x for x in g if x["net"] > 0]; losses = [x for x in g if x["net"] <= 0]
    net = sum(x["net"] for x in g); totR = sum(x["r"] for x in g)
    aw = sum(x["r"] for x in wins)/len(wins) if wins else 0
    al = sum(x["r"] for x in losses)/len(losses) if losses else 0
    print(f"{y:<6}{len(g):>7}{net:>10.0f}{totR:>9.1f}{100*len(wins)/len(g):>6.1f}%"
          f"{aw:>8.2f}{al:>9.2f}{totR/len(g):>7.3f}")
tot = sum(x['net'] for x in rows)
print(f"{'ALL':<6}{len(rows):>7}{tot:>10.0f}{sum(x['r'] for x in rows):>9.1f}")

print("\n=== EXIT REASONS ===")
for reason, n in collections.Counter(r["reason"] for r in rows).most_common():
    sub = [r for r in rows if r["reason"] == reason]
    print(f"  {reason:<18} {n:>5}  ({100*n/len(rows):4.1f}%)  avg {sum(x['r'] for x in sub)/n:>+6.2f}R  "
          f"total {sum(x['net'] for x in sub):>+8.0f}")
