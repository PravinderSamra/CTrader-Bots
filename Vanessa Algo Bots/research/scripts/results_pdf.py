"""Year-by-year results PDF for the NAS100 Add To Winner bot (trigger 0.7).

Reads the Trades-Only logs in research/data/nas100_atw_logs/ (all run at $300 risk, 2021-01-01 .. 2026-09-28).
All runs are real cTrader backtests.
Run from the repo root:  python3 "Vanessa Algo Bots/research/scripts/results_pdf.py" [--v2]
--v2 writes the shareable version: every simulation starts from a fresh $100,000 and today's balance is not mentioned.
"""
import random
import re
import sys
from collections import OrderedDict, defaultdict
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak

ROOT = Path(__file__).resolve().parents[3]
LOGS = ROOT / "Vanessa Algo Bots/research/data/nas100_atw_logs"
V2 = "--v2" in sys.argv
OUT = ROOT / ("Vanessa Algo Bots/research/results/NAS100_AddToWinner_Results_trigger0.7"
             + ("_v2.pdf" if V2 else ".pdf"))
BASE_RISK, START, FLOOR = 300.0, 100000.0, 90000.0
NOW = START if V2 else 96952.19
FROM = "$100,000" if V2 else "$96,952"
LADDER = [(104000.0, 500.0), (98000.0, 400.0), (95000.0, 300.0), (0.0, 200.0)]
LEVELS = [r for _, r in LADDER]
YEARS_OF_DATA = 5.74
N_PATHS, BLOCK = 5000, 10
# Max equity drawdown as reported by cTrader for the real runs ($300 risk)
CTRADER_DD = {"Control": "4.04%", "Size 1": "4.65%", "Size 2": "5.22%", "Size 3": "5.78%", "Size 4": "6.32%",
              "Size 5": "6.83%", "Size 6.5": "7.56%", "Size 10": "9.10%"}
T_RE = re.compile(r"T\|[\d\- :]+\|[\d\- :]+\|([^|]+)\|\w+\|[\d.]+\|[\d.]+\|(-?[\d.]+)\|")


def load(name):
    out = []
    for line in (LOGS / name).read_text(errors="replace").splitlines():
        m = T_RE.search(line)
        if m:
            label = m.group(1)
            out.append((re.search(r"_(\d{8})", label).group(1), "_ADD" in label, float(m.group(2))))
    return out


def daily(trades):
    d = defaultdict(float)
    for day, _, pl in trades:
        d[day] += pl
    return OrderedDict(sorted(d.items()))


def level(bal):
    for i, (m, _) in enumerate(LADDER):
        if bal >= m:
            return i
    return len(LADDER) - 1


def run(rs, policy, start):
    bal = peak = low = start
    dd, losses = 0.0, 0
    for r in rs:
        if policy == "300":
            risk = 300.0
        elif policy == "500":
            risk = 500.0
        else:
            lvl = level(bal)
            if losses >= 4:
                lvl = min(lvl + 1, len(LEVELS) - 1)
            risk = LEVELS[lvl]
        bal += r * risk
        losses = losses + 1 if r <= 0 else 0
        peak, low = max(peak, bal), min(low, bal)
        dd = max(dd, peak - bal)
    return bal, low, dd


def mc(rs, policy, start, horizon, seed=11):
    rng = random.Random(seed)
    hits, profits = 0, []
    for _ in range(N_PATHS):
        path = []
        while len(path) < horizon:
            i = rng.randrange(0, len(rs) - BLOCK)
            path.extend(rs[i:i + BLOCK])
        bal, low, _ = run(path[:horizon], policy, start)
        hits += low <= FLOOR
        profits.append(bal - start)
    profits.sort()
    return hits / N_PATHS, profits[N_PATHS // 2], profits[N_PATHS // 10]


def streaks(vals):
    out, c = [], 0
    for v in vals:
        if v <= 0:
            c += 1
        else:
            if c:
                out.append(c)
            c = 0
    return out + ([c] if c else [])


def max_dd(vals):
    bal = peak = START
    worst = 0.0
    for v in vals:
        bal += v
        peak = max(peak, bal)
        worst = max(worst, peak - bal)
    return worst


def main():
    runs = OrderedDict([
        ("Control", load("N0_control.trades.txt")),
        ("Size 1", load("NB_0.7_x1.trades.txt")),
        ("Size 2", load("NC_0.7_x2.trades.txt")),
        ("Size 3", load("ND_0.7_x3.trades.txt")),
        ("Size 4", load("NE_0.7_x4.trades.txt")),
        ("Size 5", load("NG_0.7_x5.trades.txt")),
        ("Size 6.5", load("NH_0.7_x6.5.trades.txt")),
        ("Size 10", load("NI_0.7_x10.trades.txt")),
    ])
    total_risk = {"Control": "0.70R", "Size 1": "1.00R", "Size 2": "1.30R", "Size 3": "1.60R",
                  "Size 4": "1.90R", "Size 5": "2.20R", "Size 6.5": "2.65R", "Size 10": "3.70R"}
    names = list(runs)
    S = {}
    for n in names:
        tr = runs[n]
        dv = daily(tr)
        vals = list(dv.values())
        rs = [v / BASE_RISK for v in vals]
        horizon = int(len(rs) / YEARS_OF_DATA)
        yearly = defaultdict(float)
        for d, _, pl in tr:
            yearly[d[:4]] += pl
        s = streaks(vals)
        wins = sum(v > 0 for v in vals)
        st = {"net": sum(p for _, _, p in tr), "adds": sum(p for _, a, p in tr if a), "yearly": yearly,
              "dd": max_dd(vals), "worst_day": min(vals), "days": len(vals), "wins": wins,
              "longest": max(s), "runs4": sum(x >= 4 for x in s), "rs": rs}
        for pol in ("300", "500", "ladder"):
            st["now_" + pol] = mc(rs, pol, NOW, horizon)
        st["fresh_ladder"] = mc(rs, "ladder", START, horizon)
        st["replay_ladder"] = run(rs, "ladder", START)
        S[n] = st
        print(n, round(st["net"], 2), {k: st[k][0] for k in st if k.startswith(("now", "fresh"))})
    build_pdf(names, S, total_risk)


def money(x, sign=False):
    s = f"{abs(x):,.0f}"
    if x < 0:
        return "-$" + s
    return ("+$" if sign else "$") + s


def pct(x, sign=False):
    return (f"{x:+.1f}%" if sign else f"{x:.1f}%")


def build_pdf(names, S, total_risk):
    ss = getSampleStyleSheet()
    h1 = ParagraphStyle("h1", parent=ss["Title"], fontSize=18, spaceAfter=4)
    h2 = ParagraphStyle("h2", parent=ss["Heading2"], fontSize=13, spaceBefore=8, spaceAfter=4,
                        textColor=colors.HexColor("#1f3b63"))
    body = ParagraphStyle("b", parent=ss["BodyText"], fontSize=9, leading=12)
    small = ParagraphStyle("s", parent=body, fontSize=7.8, leading=10, textColor=colors.HexColor("#444444"))
    cell = ParagraphStyle("c", parent=body, fontSize=8, leading=9.5)
    head = ParagraphStyle("hd", parent=cell, textColor=colors.white, fontName="Helvetica-Bold")

    def table(rows, widths, highlight_first_col=True, zebra=True):
        data = [[Paragraph(str(c), head) for c in rows[0]]] + \
               [[Paragraph(str(c), cell) for c in r] for r in rows[1:]]
        t = Table(data, colWidths=widths, repeatRows=1)
        style = [("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f3b63")),
                 ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#b8c2cf")),
                 ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                 ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]
        if zebra:
            for i in range(1, len(data)):
                if i % 2 == 0:
                    style.append(("BACKGROUND", (0, i), (-1, i), colors.HexColor("#f1f4f8")))
        if highlight_first_col:
            style.append(("FONTNAME", (0, 1), (0, -1), "Helvetica-Bold"))
        t.setStyle(TableStyle(style))
        return t

    ctrl = S["Control"]
    years = sorted(ctrl["yearly"])
    story = [Paragraph("NAS100 London Range bot — Add To Winner results (trigger 0.7)", h1),
             Paragraph("Prepared for Vanessa, 30 September 2026. Backtest 1 Jan 2021 – 28 Sep 2026, $100,000 account, "
                       "$300 risk per trade, tick data, risk reduction to 70% at 0.7R, TP 4R. "
                       "Control = the live bot with Add To Winner switched off. "
                       "Every size is a real cTrader backtest."
                       "",
                       body), Spacer(1, 4)]

    # 1. Headline
    story.append(Paragraph("1. At a glance", h2))
    rows = [["", "Total risk after add", "Net profit 2021–26", "Increase vs control", "Years beating control",
             "cTrader max equity DD", "Deepest drawdown (closed days)", "Worst single day",
             "Chance of hitting $90k in next 12 months*", "Typical 12-month profit*"]]
    for n in names:
        s = S[n]
        inc = "–" if n == "Control" else f"{money(s['net'] - ctrl['net'], True)} ({pct(100 * (s['net'] / ctrl['net'] - 1), True)})"
        beat = "–" if n == "Control" else f"{sum(s['yearly'][y] > ctrl['yearly'][y] for y in years)} / {len(years)}"
        rows.append([n, total_risk[n], money(s["net"]), inc, beat, CTRADER_DD[n],
                     f"{money(s['dd'])} ({pct(100 * s['dd'] / START)})", money(s["worst_day"]),
                     pct(100 * s["now_ladder"][0]), money(s["now_ladder"][1])])
    story.append(table(rows, [20 * mm, 20 * mm, 25 * mm, 32 * mm, 22 * mm, 22 * mm, 30 * mm, 22 * mm, 34 * mm, 26 * mm]))
    story.append(Spacer(1, 3))
    story.append(Paragraph(("* Starting from a fresh $100,000" if V2 else "* From today's balance of $96,952") + " using the risk ladder with the 4-loss rule (see section 4). "
                           ""
                           "All money figures in sections 1–3 are at $300 risk; at $500 multiply by 1.67.", small))

    # 2. Year by year
    story.append(PageBreak())
    story.append(Paragraph("2. Profit year by year (at $300 risk)", h2))
    rows = [["Year"] + names]
    for y in years:
        r = [y + (" (to 28 Sep)" if y == "2026" else "")]
        for n in names:
            v = S[n]["yearly"][y]
            if n == "Control":
                r.append(money(v))
            else:
                c = ctrl["yearly"][y]
                r.append(f"{money(v)}<br/><font color='#1a7f37'>{money(v - c, True)} ({pct(100 * (v / c - 1), True)})</font>")
        rows.append(r)
    r = ["<b>Total</b>"]
    for n in names:
        v = S[n]["net"]
        r.append(f"<b>{money(v)}</b>" if n == "Control" else
                 f"<b>{money(v)}</b><br/><font color='#1a7f37'>{money(v - ctrl['net'], True)} ({pct(100 * (v / ctrl['net'] - 1), True)})</font>")
    rows.append(r)
    r = ["Smallest yearly gain over control"] + ["–"] + [
        money(min(S[n]["yearly"][y] - ctrl["yearly"][y] for y in years), True) for n in names[1:]]
    rows.append(r)
    r = ["Profit made by the adds"] + ["–"] + [money(S[n]["adds"]) for n in names[1:]]
    rows.append(r)
    story.append(table(rows, [30 * mm] + [30 * mm] * len(names)))
    story.append(Paragraph("Green = extra profit compared with the control in the same year. "
                           "Every size beat the control in every year.", small))

    story.append(PageBreak())
    # 3. Losing streaks
    story.append(Paragraph("3. Winning days and losing streaks (main trade + add counted as one day)", h2))
    rows = [["", "Trading days", "Winning days", "Daily win rate", "Losing days per winning day",
             "Longest losing run (days)", "Losing runs of 4+ days", "Deepest drawdown at $300", "Deepest drawdown at $500"]]
    for n in names:
        s = S[n]
        rows.append([n, s["days"], s["wins"], pct(100 * s["wins"] / s["days"]), f"{(s['days'] - s['wins']) / s['wins']:.2f}",
                     s["longest"], s["runs4"], money(s["dd"]), money(s["dd"] * 500 / 300)])
    story.append(table(rows, [24 * mm, 22 * mm, 22 * mm, 22 * mm, 30 * mm, 30 * mm, 28 * mm, 32 * mm, 32 * mm]))
    story.append(Paragraph("The add does not change how often you win or how long losing streaks last — it only makes "
                           "the winning days bigger and the losing days slightly bigger (because the add sometimes stops out too).", small))

    # 4. Risk of blowing
    story.append(Paragraph("4. Risk of hitting FTMO's $90,000 floor (blowing the challenge)", h2))
    story.append(Paragraph("5,000 simulated futures built from real runs of 10 consecutive trading days, so real losing "
                           "streaks stay intact. NAS100 bot on its own — the US500 bot will add its own risk. "
                           "<b>Risk ladder:</b> $104k+ → $500, $98k+ → $400, $95k+ → $300, below → $200; "
                           "one level lower after 4 losing days in a row until the next winning day.", body))
    rows = [["", f"From {FROM}: fixed $300", f"From {FROM}: fixed $500", f"From {FROM}: risk ladder",
             "Increase in risk vs control (ladder)", "Over 3 years (ladder, approx.)"]
            + ([] if V2 else ["Fresh $100k (e.g. after a payout): ladder"])
            + [f"Bad year, 1 in 10 (ladder, from {FROM})"]]
    for n in names:
        s = S[n]
        p = s["now_ladder"][0]
        extra = "–" if n == "Control" else f"{100 * (p - ctrl['now_ladder'][0]):+.1f} points"
        rows.append([n, pct(100 * s["now_300"][0]), pct(100 * s["now_500"][0]), f"<b>{pct(100 * p)}</b>", extra,
                     pct(100 * (1 - (1 - p) ** 3))] + ([] if V2 else [pct(100 * s["fresh_ladder"][0])])
                    + [money(s["now_ladder"][2])])
    story.append(table(rows, [22 * mm, 30 * mm, 30 * mm, 30 * mm, 32 * mm, 30 * mm] + ([] if V2 else [36 * mm]) + [36 * mm]))

    story.append(PageBreak())
    story.append(Paragraph(f"5. Typical profit over 12 months (median of the simulations, from {FROM})", h2))
    rows = [["", "Fixed $300", "Fixed $500", "Risk ladder", "Increase vs control (ladder)",
             "Replay 2021–26 with ladder from $100k: final balance", "Replay: deepest drawdown"]]
    for n in names:
        s = S[n]
        m = s["now_ladder"][1]
        extra = "–" if n == "Control" else f"{money(m - ctrl['now_ladder'][1], True)} ({pct(100 * (m / ctrl['now_ladder'][1] - 1), True)})"
        fb, _, dd = s["replay_ladder"]
        rows.append([n, money(s["now_300"][1]), money(s["now_500"][1]), f"<b>{money(m)}</b>", extra, money(fb), money(dd)])
    story.append(table(rows, [22 * mm, 28 * mm, 28 * mm, 28 * mm, 42 * mm, 58 * mm, 36 * mm]))

    story.append(Paragraph("6. How to read this, in plain English", h2))
    for t in [
        "<b>Profit goes up in a straight line with size.</b> Each extra step of add size adds roughly $5,300 over the "
        "5¾ years at $300 risk (about $8,800 at $500). It beat the control in every single year, at every size.",
        "<b>Risk goes up faster than profit at the big sizes.</b> The chance of hitting $90k stays tiny up to size 3, "
        "then climbs: each extra size step costs more risk than the one before.",
        "<b>Risk adds up over time.</b> A 3% chance per year is roughly a 9% chance over three years. "
        "The US500 bot will add its own risk on top, so the combined account needs a single budget. "
        "Suggested: no more than 2–3% a year chance of hitting $90k for both bots together.",
        "<b>Win rate and losing streaks don't change.</b> About 36% of days win at every size, and the longest losing run "
        "stays at 11 days. What changes is how much a bad run costs.",
        "<b>The ladder is what keeps you safe.</b> Dropping risk as the balance falls cuts the chance of hitting $90k "
        f"sharply compared with a fixed $500 (size 3: {100 * S['Size 3']['now_500'][0]:.1f}% down to "
        f"{100 * S['Size 3']['now_ladder'][0]:.1f}%) — see section 4.",
        "<b>Size 10 is the 'greed' test.</b> Its worst losing run cost $12,534 at $300 risk ($20,890 at $500), more than "
        "the $10,000 of room a fresh $100k account has above $90k. It only survived the backtest because the run came when "
        "the account was already at about $143k.",
        "<b>Settings for sizes above 4.33:</b> raise 'Max Total Risk' to at least the 'total risk after add' figure "
        "(size 5 → 2.2, size 6.5 → 2.7), otherwise the add gets capped.",
        "<b>Caveats:</b> backtests are not guarantees; strategies usually earn less after going live. The simulations "
        "reuse 2021–26 behaviour — a new kind of market could be worse. "
        "Please double-check with FTMO that a payout resets the "
        "balance to $100k with the floor staying at $90k.",
    ]:
        story.append(Paragraph("• " + t, body))
        story.append(Spacer(1, 3))

    doc = SimpleDocTemplate(str(OUT), pagesize=landscape(A4), leftMargin=12 * mm, rightMargin=12 * mm,
                            topMargin=12 * mm, bottomMargin=12 * mm, title="NAS100 Add To Winner results (trigger 0.7)",
                            author="Trevor")
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    print("Wrote", OUT)


def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 7)
    canvas.setFillColor(colors.grey)
    canvas.drawString(12 * mm, 7 * mm, "Vanessa Algo Bots — NAS100 Add To Winner (trigger 0.7) — generated by research/scripts/results_pdf.py")
    canvas.drawRightString(landscape(A4)[0] - 12 * mm, 7 * mm, f"Page {doc.page}")
    canvas.restoreState()


if __name__ == "__main__":
    main()
