import sys, statistics as st, html
sys.path.insert(0, "/home/user/CTrader-Bots/Vanessa Algo Bots/research/scripts/screens")
from vlib import nas_daily
from datetime import date
d = nas_daily(); C = [x[4] for x in d]; D = [x[0].date() for x in d]
def sma(i, n): return sum(C[i-n+1:i+1]) / n
R = [None]*len(C); g = l = 0
for i in range(1, len(C)):
    x = C[i]-C[i-1]; up, dn = max(x, 0), max(-x, 0)
    if i <= 2: g += up/2; l += dn/2
    else: g = (g+up)/2; l = (l+dn)/2
    if i >= 2: R[i] = 100 if l == 0 else 100-100/(1+g/l)
ev = []; pos = {}
for i in range(210, len(C)):
    dev = abs(C[i]-sma(i, 5)); avg = st.mean(abs(C[k]-sma(k, 5)) for k in range(i-20, i))
    for s in "AD":
        if s in pos:
            e = pos[s]; ex = (C[i] > sma(i, 5) or i-e >= 4) if s == "A" else R[i] > 70
            if ex: ev.append((i, s, "Sell", C[i])); del pos[s]
            continue
        sig = (C[i] < sma(i, 5) and dev > 2.5*avg and C[i] > sma(i, 200)) if s == "A" else (C[i] > sma(i, 200) and R[i] < 20)
        if sig: ev.append((i, s, "Buy", C[i])); pos[s] = i
a = next(i for i in range(len(D)) if D[i] >= date(2024, 7, 8)); b = next(i for i in range(len(D)) if D[i] >= date(2024, 9, 20))
idx = list(range(a, b+1))
W, Hh, ml, mr, mt, mb = 760, 300, 64, 92, 16, 34

def xs(i): return ml + (i-a)/(b-a)*(W-ml-mr)

def price_chart(sys, lines):
    vals = [C[i] for i in idx] + [v for _, f, _l in lines for v in (f(i) for i in idx)]
    lo, hi = min(vals), max(vals); pad = (hi-lo)*0.08; lo -= pad; hi += pad
    ys = lambda v: mt + (hi-v)/(hi-lo)*(Hh-mt-mb)
    o = [f'<svg viewBox="0 0 {W} {Hh}" role="img" aria-label="NAS100 daily closes with strategy {sys} trades">']
    step = 500 if hi-lo > 2000 else 250
    v = (int(lo)//step+1)*step
    while v < hi:
        o.append(f'<line class="grid" x1="{ml}" x2="{W-mr}" y1="{ys(v):.1f}" y2="{ys(v):.1f}"/><text class="ax" x="{ml-6}" y="{ys(v)+4:.1f}" text-anchor="end">{v:,}</text>'); v += step
    for i in idx:
        if D[i].day <= 7 and D[i].weekday() == 0 or i == a:
            o.append(f'<text class="ax" x="{xs(i):.1f}" y="{Hh-12}" text-anchor="middle">{D[i]:%d %b}</text>')
    o.append('<polyline class="price" points="' + " ".join(f"{xs(i):.1f},{ys(C[i]):.1f}" for i in idx) + '"/>')
    for cls, f, lab in lines:
        o.append(f'<polyline class="{cls}" points="' + " ".join(f"{xs(i):.1f},{ys(f(i)):.1f}" for i in idx) + '"/>')
        o.append(f'<text class="lab {cls}-t" x="{W-mr+6}" y="{ys(f(b))+4:.1f}">{lab}</text>')
    o.append(f'<text class="lab" x="{W-mr+6}" y="{ys(C[b])+4:.1f}">Close</text>')
    for i in idx:
        o.append(f'<circle class="hit" cx="{xs(i):.1f}" cy="{ys(C[i]):.1f}" r="7"><title>{D[i]:%a %d %b %Y}  close {C[i]:,.0f}</title></circle>')
    for i, s, kind, p in ev:
        if s != sys or not a <= i <= b: continue
        x, y = xs(i), ys(p)
        if kind == "Buy":
            o.append(f'<path class="buy" d="M{x:.1f},{y+8:.1f} l7,12 h-14 z"><title>Buy ({sys}) {D[i]:%d %b} at the close {p:,.0f}</title></path>')
            o.append(f'<text class="tag" x="{x:.1f}" y="{y+32:.1f}" text-anchor="middle">Buy</text>')
        else:
            o.append(f'<path class="sell" d="M{x:.1f},{y-8:.1f} l7,-12 h-14 z"><title>Sell ({sys}) {D[i]:%d %b} at the close {p:,.0f}</title></path>')
            o.append(f'<text class="tag" x="{x:.1f}" y="{y-24:.1f}" text-anchor="middle">Sell</text>')
    o.append('</svg>'); return "\n".join(o)

def rsi_chart():
    H2 = 170; ys = lambda v: mt + (100-v)/100*(H2-mt-mb)
    o = [f'<svg viewBox="0 0 {W} {H2}" role="img" aria-label="RSI(2) with the 20 buy and 70 sell lines">']
    for v in (0, 20, 70, 100):
        cls = "ref" if v in (20, 70) else "grid"
        o.append(f'<line class="{cls}" x1="{ml}" x2="{W-mr}" y1="{ys(v):.1f}" y2="{ys(v):.1f}"/><text class="ax" x="{ml-6}" y="{ys(v)+4:.1f}" text-anchor="end">{v}</text>')
    o.append(f'<text class="lab" x="{W-mr+6}" y="{ys(70)+4:.1f}">70 = sell</text><text class="lab" x="{W-mr+6}" y="{ys(20)+4:.1f}">20 = buy</text>')
    for i in idx:
        if D[i].day <= 7 and D[i].weekday() == 0 or i == a:
            o.append(f'<text class="ax" x="{xs(i):.1f}" y="{H2-12}" text-anchor="middle">{D[i]:%d %b}</text>')
    o.append('<polyline class="ma5" points="' + " ".join(f"{xs(i):.1f},{ys(R[i]):.1f}" for i in idx) + '"/>')
    for i in idx:
        o.append(f'<circle class="hit" cx="{xs(i):.1f}" cy="{ys(R[i]):.1f}" r="7"><title>{D[i]:%a %d %b}  RSI(2) {R[i]:.0f}</title></circle>')
    o.append('</svg>'); return "\n".join(o)

chartA = price_chart("A", [("ma5", lambda i: sma(i, 5), "5-day avg"), ("ma200", lambda i: sma(i, 200), "200-day avg")])
chartD = price_chart("D", [("ma200", lambda i: sma(i, 200), "200-day avg")])
rows = "".join(f"<tr><td>{D[i]:%d %b %Y}</td><td>{s}</td><td>{k}</td><td>{p:,.0f}</td></tr>" for i, s, k, p in ev if a <= i <= b)
page = open(sys.argv[1]).read().replace("{{A}}", chartA).replace("{{D}}", chartD).replace("{{RSI}}", rsi_chart()).replace("{{ROWS}}", rows)
open(sys.argv[2], "w").write(page)
print("ok")
