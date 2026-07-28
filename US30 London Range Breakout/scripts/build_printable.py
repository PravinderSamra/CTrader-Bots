"""
Build a one-page, print-ready executive summary (Letter portrait) from the
net-of-cost figures, then this file is rendered to PDF by render_pdf.py.
Static HTML (no JS) so it prints deterministically.
"""
import os, json
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
C = json.load(open(os.path.join(ROOT, "analysis", "dollar", "consolidated.json")))

REC = {"US30": "3.0", "NAS100": "3.5"}   # recommended RR per instrument (best net)
CFG_TXT = {"US30": "Range 08:00→09:30 ET · execute 10:00–13:00 ET · 75-pt stop · vol ≥1.2×",
           "NAS100": "Range 02:00→09:30 ET · execute 10:00–11:00 ET · 40-pt stop · vol ≥1.2×"}

def usd(v, s=True):
    sign = '−' if v < 0 else ('+' if s and v > 0 else '')
    return f"{sign}${abs(v):,.0f}"

def matrix_rows():
    rrs = [f"{r:.1f}" for r in C["rrs"]]
    out = []
    for inst in ["US30", "NAS100"]:
        vals = {r: C["data"][inst][r]["net"]["total_usd"] for r in rrs}
        best = max(vals, key=vals.get)
        cells = "".join(
            f'<td class="{"best" if r==best else ""}">{usd(vals[r])}</td>' for r in rrs)
        out.append(f'<tr><td class="inst">{inst}</td>{cells}<td class="rec">{best}R</td></tr>')
    return "".join(out), rrs

def yearly_rows(inst, rr):
    yb = C["data"][inst][rr]["net"]["yearly"]
    rows = ""
    tt = dict(t=0, w=0, l=0, u=0.0)
    for r in yb:
        part = ' <span class="p">part</span>' if r["year"] in (2023, 2026) else ""
        tt["t"] += r["trades"]; tt["w"] += r["wins"]; tt["l"] += r["losses"]; tt["u"] += r["usd"]
        cls = "pos" if r["usd"] >= 0 else "neg"
        rows += (f'<tr><td class="yr">{r["year"]}{part}</td><td>{r["trades"]}</td>'
                 f'<td>{r["wins"]}</td><td>{r["losses"]}</td><td>{r["win_pct"]:.0f}%</td>'
                 f'<td>{r["longest_win_streak"]}</td><td>{r["longest_loss_streak"]}</td>'
                 f'<td class="{cls}">{usd(r["usd"])}</td><td>${r["account_end"]:,.0f}</td></tr>')
    rows += (f'<tr class="tot"><td>3-yr total</td><td>{tt["t"]}</td><td>{tt["w"]}</td>'
             f'<td>{tt["l"]}</td><td>{tt["w"]/tt["t"]*100:.0f}%</td><td>—</td><td>—</td>'
             f'<td class="{"pos" if tt["u"]>=0 else "neg"}">{usd(tt["u"])}</td>'
             f'<td>${100000+tt["u"]:,.0f}</td></tr>')
    return rows

def inst_block(inst):
    rr = REC[inst]; d = C["data"][inst][rr]["net"]
    trades = d["trades"]; wins = sum(r["wins"] for r in d["yearly"])
    maxloss = max(r["longest_loss_streak"] for r in d["yearly"])
    cpt = C["data"][inst][rr]["cost_per_trade_usd"]
    head = (f'<div class="ib-head"><h3>{inst} <span class="tag">recommended · {rr}R</span></h3>'
            f'<div class="big {"pos" if d["total_usd"]>=0 else "neg"}">{usd(d["total_usd"])}'
            f'<span class="lab"> net over 3 yrs</span></div></div>'
            f'<p class="cfg">{CFG_TXT[inst]} · {trades} trades · {wins/trades*100:.0f}% win '
            f'· worst losing streak {maxloss} · cost ${cpt:.2f}/trade</p>')
    table = ('<table class="yt"><thead><tr><th>Year</th><th>Trades</th><th>Won</th><th>Lost</th>'
             '<th>Win%</th><th>Win<br>streak</th><th>Loss<br>streak</th><th>P&amp;L</th><th>Balance</th></tr></thead>'
             f'<tbody>{yearly_rows(inst, rr)}</tbody></table>')
    return f'<section class="ib">{head}{table}</section>'

mrows, rrs = matrix_rows()
mhead = "".join(f"<th>{r}R</th>" for r in rrs)
us30_net = C["data"]["US30"]["3.0"]["net"]["total_usd"]
nas_net = C["data"]["NAS100"]["3.5"]["net"]["total_usd"]

HTML = f"""<!doctype html><html><head><meta charset="utf-8"><title>LRB Exec Summary</title>
<style>
@page {{ size: Letter portrait; margin: 13mm 14mm; }}
*{{box-sizing:border-box}}
html,body{{margin:0;padding:0;color:#16181d;background:#fff;
  font-family:-apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;font-size:9.4px;line-height:1.4}}
.mono,td,th,.big,.matrix td{{font-variant-numeric:tabular-nums}}
.serif{{font-family:"Iowan Old Style",Georgia,"Times New Roman",serif}}
h1{{font-family:"Iowan Old Style",Georgia,serif;font-size:21px;margin:0;letter-spacing:-.01em;font-weight:600}}
.eyebrow{{font-size:8px;letter-spacing:.16em;text-transform:uppercase;color:#a9761f;font-weight:700;margin:0 0 4px}}
.sub{{color:#5c6675;font-size:9.2px;margin:4px 0 0;max-width:118ch}}
header{{border-bottom:2px solid #16181d;padding-bottom:9px;margin-bottom:10px;
  display:flex;justify-content:space-between;align-items:flex-end;gap:16px}}
.hl{{text-align:right;white-space:nowrap}}
.hl .k{{font-size:8px;text-transform:uppercase;letter-spacing:.08em;color:#5c6675}}
.hl .v{{font-family:"Iowan Old Style",Georgia,serif;font-size:16px;font-weight:600;color:#16794c}}
.assump{{display:flex;flex-wrap:wrap;gap:0;border:1px solid #e2e6ec;border-radius:6px;overflow:hidden;margin-bottom:11px}}
.assump div{{flex:1 1 auto;padding:6px 10px;border-right:1px solid #eef1f5}}
.assump div:last-child{{border-right:0}}
.assump .k{{font-size:7.5px;text-transform:uppercase;letter-spacing:.06em;color:#5c6675}}
.assump .v{{font-family:ui-monospace,Menlo,monospace;font-size:9.6px;font-weight:600;margin-top:1px}}
h2{{font-family:"Iowan Old Style",Georgia,serif;font-size:12.5px;margin:12px 0 5px;font-weight:600}}
h2 .n{{color:#a9761f;font-family:ui-monospace,monospace;font-size:10px;margin-right:6px}}
table{{border-collapse:collapse;width:100%}}
.matrix{{border:1px solid #e2e6ec;border-radius:6px;overflow:hidden}}
.matrix th,.matrix td{{padding:6px 10px;text-align:right;border-bottom:1px solid #eef1f5;font-size:9.4px}}
.matrix th:first-child,.matrix td:first-child{{text-align:left}}
.matrix thead th{{background:#f7f8fa;font-size:8px;text-transform:uppercase;letter-spacing:.05em;color:#5c6675}}
.matrix tbody tr:last-child td{{border-bottom:0}}
.matrix .inst{{font-weight:700}}
.matrix td.best{{background:#f2e6cd;font-weight:700}}
.matrix .rec{{font-family:ui-monospace,monospace;color:#a9761f;font-weight:700}}
.note{{background:#f7f8fa;border-left:3px solid #a9761f;border-radius:0 5px 5px 0;padding:7px 10px;
  font-size:8.8px;color:#3d4451;margin:7px 0 0}}
.grid2{{display:grid;grid-template-columns:1fr;gap:9px;margin-top:4px}}
.ib{{border:1px solid #e2e6ec;border-radius:6px;padding:9px 11px}}
.ib-head{{display:flex;justify-content:space-between;align-items:baseline}}
.ib h3{{font-family:"Iowan Old Style",Georgia,serif;font-size:12px;margin:0;font-weight:600}}
.ib .tag{{font-family:-apple-system,sans-serif;font-size:8px;font-weight:600;color:#a9761f;
  background:#f2e6cd;padding:1px 6px;border-radius:20px;margin-left:5px;letter-spacing:.02em}}
.big{{font-family:ui-monospace,monospace;font-size:15px;font-weight:700}}
.big .lab{{font-family:-apple-system,sans-serif;font-size:8px;font-weight:400;color:#5c6675}}
.cfg{{color:#5c6675;font-size:8.4px;margin:2px 0 6px;font-family:ui-monospace,monospace}}
.yt th,.yt td{{padding:3.5px 6px;text-align:right;border-bottom:1px solid #eef1f5;font-size:9px;
  font-family:ui-monospace,Menlo,monospace}}
.yt th{{font-family:-apple-system,sans-serif;font-size:7.6px;text-transform:uppercase;letter-spacing:.04em;
  color:#5c6675;font-weight:600;background:#fafbfc;line-height:1.15}}
.yt th:first-child,.yt td:first-child{{text-align:left;font-family:-apple-system,sans-serif}}
.yt .yr{{font-weight:600}} .yt .p{{color:#8b95a4;font-size:7px;font-family:-apple-system,sans-serif}}
.yt tr.tot td{{font-weight:700;border-top:1.5px solid #cfd6df;background:#fafbfc}}
.pos{{color:#16794c}} .neg{{color:#c0433d}}
.takeaways{{display:grid;grid-template-columns:repeat(3,1fr);gap:9px;margin-top:9px}}
.tk{{border:1px solid #e2e6ec;border-radius:6px;padding:8px 10px}}
.tk .h{{font-weight:700;font-size:9.2px;margin-bottom:2px}}
.tk .b{{color:#3d4451;font-size:8.6px}}
.foot{{margin-top:10px;padding-top:7px;border-top:1px solid #e2e6ec;color:#5c6675;font-size:7.8px}}
.foot code{{font-family:ui-monospace,monospace}}
</style></head><body>
<header>
  <div>
    <p class="eyebrow">Strategy Performance · Management Brief · {C['config']['US30']['stop_pts']}pt / {C['config']['NAS100']['stop_pts']}pt</p>
    <h1>London Range Breakout — P&amp;L in Dollars</h1>
    <p class="sub">Three-year backtest (Jul 2023 – Jul 2026) of the refined US30 &amp; NAS100 London-range breakout.
      $100,000 account, flat $100 risk per trade (1R = $100). <b>All figures net of dealing spread.</b></p>
  </div>
  <div class="hl"><div class="k">Best net result (3 yrs)</div><div class="v">{usd(us30_net)}</div>
    <div class="k" style="margin-top:2px">US30 · 3.0R</div></div>
</header>

<div class="assump">
  <div><div class="k">Account</div><div class="v">$100,000</div></div>
  <div><div class="k">Risk / trade</div><div class="v">$100 (1R)</div></div>
  <div><div class="k">Entry</div><div class="v">1st hi-vol break</div></div>
  <div><div class="k">No-trade</div><div class="v">09:30–10:00 ET</div></div>
  <div><div class="k">US30 spread</div><div class="v">2.0 pt · $2.67</div></div>
  <div><div class="k">NAS100 spread</div><div class="v">1.5 pt · $3.75</div></div>
  <div><div class="k">Costs</div><div class="v">modelled</div></div>
</div>

<h2><span class="n">01</span>3-year net profit — instrument × reward target</h2>
<table class="matrix"><thead><tr><th>Instrument (net of costs)</th>{mhead}<th>Best</th></tr></thead>
<tbody>{mrows}</tbody></table>
<div class="note"><b>Decision:</b> US30 at 3.0R delivers the highest net total ({usd(us30_net)}). NAS100
  (best {usd(nas_net)} at 3.5R) earns comparable dollars in ~35% fewer trades with roughly half the drawdown and
  is profitable every year — the preferred vehicle on risk-adjusted terms. Higher targets help up to ~3R, then plateau.</div>

<h2><span class="n">02</span>Recommended configuration — yearly detail (net)</h2>
<div class="grid2">{inst_block('US30')}{inst_block('NAS100')}</div>

<div class="takeaways">
  <div class="tk"><div class="h">The edge survives costs</div><div class="b">After spread, US30 3.0R nets
    {usd(us30_net)} and NAS100 3.5R nets {usd(nas_net)} — profitable in all four calendar years.</div></div>
  <div class="tk"><div class="h">Plan for losing streaks</div><div class="b">Win rates are 20–43%; runs of
    7–9 consecutive losers occur every year. Sizing and psychology must absorb this.</div></div>
  <div class="tk"><div class="h">Next step</div><div class="b">Forward-test NAS100 (balanced 60pt/2.0R and 3.5R)
    on demo for 4–8 weeks before committing capital.</div></div>
</div>

<div class="foot"><b>Method.</b> Dollars = R × $100 (stop-size independent). Wins/losses = trades closed in
  profit/loss; streaks are consecutive in date order. Dealing cost = one bid/ask spread per trade (spread-bet
  indices carry no separate commission); slippage on stops not modelled. First qualifying high-volume breakout
  per day. Backtest on cTrader M5 data, not live results; 2023 &amp; 2026 are part-years. Source: <code>scripts/dollar_report.py</code>.
</div>
</body></html>"""

out = os.path.join(ROOT, "printable_summary.html")
open(out, "w").write(HTML)
print("wrote", out, len(HTML), "bytes")
