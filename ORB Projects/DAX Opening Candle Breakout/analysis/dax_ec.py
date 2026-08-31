"""5-min opening candle + 12 EMA at the Frankfurt cash open, on GER40 M5.

Signal: at the close of the 09:05 CET bar (first 5-min bar of the cash session),
go long if that bar closed above the 12-period EMA, short if below.
Stop = atr_mult * ATR14(M5) at entry. Exit = trailing stop or end of session.
"""
import csv, collections, datetime as dt, statistics as st
from zoneinfo import ZoneInfo

BERLIN = ZoneInfo("Europe/Berlin"); UTC = ZoneInfo("UTC")
bars=[]
for r in csv.DictReader(open("ger40_clean.csv")):
    t = dt.datetime.strptime(r["datetime_utc"], "%Y-%m-%d %H:%M:%S").replace(tzinfo=UTC)
    bars.append((t, t.astimezone(BERLIN), float(r["open"]), float(r["high"]),
                 float(r["low"]), float(r["close"]), float(r["volume"])))
bars.sort()
byday=collections.defaultdict(list)
for b in bars: byday[b[1].date()].append(b)

def ema(vals, n):
    k=2/(n+1); e=vals[0]
    for v in vals[1:]: e = v*k + e*(1-k)
    return e

def atr(day_bars, upto, n=14):
    """ATR over the n bars ending at index upto (inclusive), using this day's bars."""
    seg=day_bars[max(0,upto-n+1):upto+1]
    if len(seg)<2: return None
    trs=[]
    for i in range(1,len(seg)):
        h,l,pc = seg[i][3], seg[i][4], seg[i-1][5]
        trs.append(max(h-l, abs(h-pc), abs(l-pc)))
    return sum(trs)/len(trs) if trs else None

def run(atr_mult=1.0, trail=True, trail_mult=1.0, ema_len=12, close_min=(17,30)):
    trades=[]
    for d in sorted(byday):
        day=byday[d]
        if len(day)<40: continue
        # index of the 09:05 CET bar (first 5-min bar of cash session closes at 09:05)
        sig=None
        for i,b in enumerate(day):
            if b[1].hour==9 and b[1].minute==0: sig=i; break
        if sig is None or sig<ema_len or sig+2>=len(day): continue
        sig_bar=day[sig]
        closes=[x[5] for x in day[max(0,sig-ema_len*3):sig+1]]
        if len(closes)<ema_len: continue
        e=ema(closes, ema_len)
        a=atr(day, sig)
        if not a or a<=0: continue
        side = 1 if sig_bar[5] > e else -1
        entry_bar = day[sig+1]
        entry = entry_bar[2]                      # next bar open
        risk = atr_mult*a
        stop = entry - side*risk
        best = entry
        exit_px=None
        for b in day[sig+1:]:
            if b[1].hour>close_min[0] or (b[1].hour==close_min[0] and b[1].minute>=close_min[1]):
                exit_px=b[2]; break
            hit = (b[4]<=stop) if side>0 else (b[3]>=stop)
            if hit: exit_px=stop; break
            if trail:
                best = max(best,b[3]) if side>0 else min(best,b[4])
                ns = best - side*trail_mult*risk
                stop = max(stop,ns) if side>0 else min(stop,ns)
        if exit_px is None: exit_px=day[-1][5]
        trades.append(dict(date=d, side=side, entry=entry, exitp=exit_px, risk=risk,
                           r=side*(exit_px-entry)/risk))
    return trades

def summarise(tr,label):
    if not tr: print(f"{label:<30} no trades"); return
    R=[t["r"] for t in tr]; n=len(R)
    w=[x for x in R if x>0]
    peak=cum=0.0; dd=0.0
    for x in R: cum+=x; peak=max(peak,cum); dd=min(dd,cum-peak)
    e=sum(R)/n; sd=st.stdev(R) if n>1 else 0
    t=e/(sd/n**0.5) if sd else 0
    print(f"{label:<30}{n:>6}{sum(R):>9.1f}{e:>+9.4f}{100*len(w)/n:>7.1f}%"
          f"{sum(w)/len(w) if w else 0:>7.2f}{-dd:>8.1f}{t:>7.2f}")

print(f"GER40 M5: {bars[0][0]:%Y-%m-%d} -> {bars[-1][0]:%Y-%m-%d}, {len(byday)} days\n")
print(f"{'variant':<30}{'n':>6}{'totR':>9}{'expR':>9}{'win%':>8}{'avgW':>7}{'maxDD':>8}{'t':>7}")
for am in (0.5,1.0,1.5,2.0):
    summarise(run(atr_mult=am, trail=True, trail_mult=1.0), f"ATR x{am}, trail 1.0xATR")
print()
for tm in (0.5,1.5,2.0):
    summarise(run(atr_mult=1.0, trail=True, trail_mult=tm), f"ATR x1.0, trail {tm}xATR")
print()
summarise(run(atr_mult=1.0, trail=False), "ATR x1.0, no trail (EOD)")
summarise(run(atr_mult=1.5, trail=False), "ATR x1.5, no trail (EOD)")
