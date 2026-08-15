#!/usr/bin/env python3
"""
Build the trading playbook PDF: the two things that survived testing.

Everything in here is a measured result, not a plan. The NAS100 numbers come
from 434 backtested trades across five full years on one unchanged config; the
US500 numbers from 18 live journalled trades over six weeks. Both carry their
sample size on the page, because a reader six months from now needs to know
which figures were solid and which were provisional.
"""
import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (BaseDocTemplate, Frame, PageTemplate, Paragraph,
                                Spacer, Table, TableStyle, KeepTogether)

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Trading_Playbook.pdf")

INK   = colors.HexColor("#101720")
INK2  = colors.HexColor("#3D4855")
INK3  = colors.HexColor("#6E7A88")
RULE  = colors.HexColor("#D8DDE2")
RULE2 = colors.HexColor("#EAEDF0")
LOSS  = colors.HexColor("#A32B26")
GAIN  = colors.HexColor("#1B6B57")
PANEL = colors.HexColor("#F6F7F8")

S = dict(
    h1=ParagraphStyle("h1", fontName="Times-Roman", fontSize=25, leading=29,
                      textColor=INK, spaceAfter=3),
    eyebrow=ParagraphStyle("eyebrow", fontName="Courier", fontSize=7.5, leading=11,
                           textColor=INK3, spaceAfter=8),
    h2=ParagraphStyle("h2", fontName="Times-Roman", fontSize=15.5, leading=19,
                      textColor=INK, spaceBefore=15, spaceAfter=5),
    h3=ParagraphStyle("h3", fontName="Helvetica-Bold", fontSize=9.8, leading=13,
                      textColor=INK, spaceBefore=9, spaceAfter=3),
    body=ParagraphStyle("body", fontName="Helvetica", fontSize=9.2, leading=13.4,
                        textColor=INK2, spaceAfter=5),
    lede=ParagraphStyle("lede", fontName="Helvetica", fontSize=9.6, leading=14,
                        textColor=INK2, spaceAfter=8),
    note=ParagraphStyle("note", fontName="Helvetica-Oblique", fontSize=8.4, leading=12,
                        textColor=INK3, spaceAfter=5),
    cell=ParagraphStyle("cell", fontName="Helvetica", fontSize=8.3, leading=11, textColor=INK2),
)


def para(t, s="body"):
    return Paragraph(t, S[s])


def table(data, widths, align_right_from=1, head=True, foot=False):
    t = Table(data, colWidths=widths, hAlign="LEFT")
    st = [
        ("FONT", (0, 0), (-1, -1), "Helvetica", 8.3),
        ("TEXTCOLOR", (0, 0), (-1, -1), INK2),
        ("ALIGN", (align_right_from, 0), (-1, -1), "RIGHT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 4.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4.5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("LINEBELOW", (0, 0), (-1, -2), 0.4, RULE2),
    ]
    if head:
        st += [("FONT", (0, 0), (-1, 0), "Courier", 7.2),
               ("TEXTCOLOR", (0, 0), (-1, 0), INK3),
               ("LINEBELOW", (0, 0), (-1, 0), 0.7, RULE)]
    if foot:
        st += [("FONT", (0, -1), (-1, -1), "Helvetica-Bold", 8.3),
               ("TEXTCOLOR", (0, -1), (-1, -1), INK),
               ("LINEABOVE", (0, -1), (-1, -1), 0.9, INK),
               ("LINEBELOW", (0, -1), (-1, -1), 0, colors.white)]
    t.setStyle(TableStyle(st))
    return t


def statbar(items):
    """A row of headline figures."""
    row, styles = [], []
    for i, (val, lab, col) in enumerate(items):
        row.append(Paragraph(
            f'<font name="Courier-Bold" size="15" color="{col}">{val}</font><br/>'
            f'<font name="Courier" size="6.8" color="#6E7A88">{lab.upper()}</font>',
            S["cell"]))
    t = Table([row], colWidths=[(170 * mm) / len(items)] * len(items), hAlign="LEFT")
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), PANEL),
        ("BOX", (0, 0), (-1, -1), 0.5, RULE),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, RULE),
        ("TOPPADDING", (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    return t


def rule():
    t = Table([[""]], colWidths=[170 * mm], rowHeights=[0.1])
    t.setStyle(TableStyle([("LINEABOVE", (0, 0), (-1, 0), 0.6, RULE)]))
    return t


def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Courier", 6.8)
    canvas.setFillColor(INK3)
    canvas.drawString(20 * mm, 12 * mm, "Trading Playbook  ·  compiled 15 August 2026")
    canvas.drawRightString(190 * mm, 12 * mm, f"{doc.page}")
    canvas.setStrokeColor(RULE)
    canvas.setLineWidth(0.5)
    canvas.line(20 * mm, 16 * mm, 190 * mm, 16 * mm)
    canvas.restoreState()


def build():
    doc = BaseDocTemplate(OUT, pagesize=A4,
                          leftMargin=20 * mm, rightMargin=20 * mm,
                          topMargin=18 * mm, bottomMargin=20 * mm,
                          title="Trading Playbook", author="Trading research")
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="f")
    doc.addPageTemplates([PageTemplate(id="p", frames=[frame], onPage=footer)])
    E = []

    # ---------------------------------------------------------------- cover
    E += [para("TRADING PLAYBOOK &nbsp;·&nbsp; WHAT SURVIVED TESTING", "eyebrow"),
          Paragraph("Two strategies worth keeping", S["h1"]),
          para("Everything below is a measured result rather than a plan. One is a bot "
               "validated over five years of backtests; the other is your own discretionary "
               "trading, measured over six weeks of real fills. Sample sizes are printed "
               "beside every figure, because in six months you will need to know which of "
               "these numbers were solid and which were provisional.", "lede"),
          Spacer(1, 6)]

    E += [statbar([("+0.204R", "NAS100 bot, per trade", "#1B6B57"),
                   ("+0.403R", "US500 by hand, per trade", "#1B6B57"),
                   ("434 / 18", "trades behind each", "#101720")]),
          Spacer(1, 4),
          para("The discretionary trading is running at roughly twice the bot's edge. It is "
               "also measured on 18 trades against 434, so expect it to come down.", "note")]

    # ------------------------------------------------------------- strategy 1
    E += [Paragraph("1 &nbsp;·&nbsp; NAS100 opening-range bot", S["h2"]),
          para("A wide overnight range, a short late window, a plain stop and target. No "
               "breakeven, no trailing, no risk reduction — every attempt to add those made "
               "it worse. Profitable in all five full years tested on one unchanged "
               "configuration.", "lede")]

    E += [Paragraph("The configuration", S["h3"]),
          table([
              ["Setting", "Value"],
              ["Instrument", "US100.cash  (NAS100)"],
              ["Range window", "02:00 – 09:30 New York"],
              ["Entry window", "10:00 – 11:00 New York"],
              ["Range time zone", "America/New_York"],
              ["Trading time zone", "America/New_York"],
              ["Stop", "60 points, fixed"],
              ["Target", "4R (rarely reached; most exits are on the clock)"],
              ["Volume filter", "1.2x the trailing 20-bar average"],
              ["Direction", "Long and short"],
              ["Breakeven / trailing / risk reduction", "All OFF"],
              ["Max trades per day", "1"],
          ], [58 * mm, 112 * mm])]

    E += [Paragraph("Five-year record", S["h3"]),
          table([
              ["Year", "Trades", "Net", "Per trade", "PF", "Minus top 5"],
              ["2022", "105", "+$2,914", "+$27.75", "1.44", "+$922"],
              ["2023", "106", "+$1,671", "+$15.77", "1.29", "-$234"],
              ["2024  (tuned)", "85", "+$2,352", "+$27.67", "1.52", "+$359"],
              ["2025", "88", "+$1,368", "+$15.55", "1.25", "-$622"],
              ["2026  (to Aug)", "50", "+$553", "+$11.07", "1.16", "-$1,434"],
              ["Total", "434", "+$8,859", "+$20.41", "1.34", "+$6,859"],
          ], [34 * mm, 22 * mm, 28 * mm, 26 * mm, 20 * mm, 40 * mm], foot=True)]

    E += [Spacer(1, 5),
          para("<b>Why this one is trusted.</b> Removing the ten best trades from 434 still "
               "leaves +$4,867. The equivalent test on the US30 version turned five years "
               "negative by removing a single trade. Worst drawdown was -$1,109, about 11R, "
               "and 70% of months finished positive. Only 2024 is fitted — the 60pt stop was "
               "chosen there. The other four years ran afterwards on that same setting and "
               "all four are positive.")]

    E += [Paragraph("What was tested and rejected", S["h3"]),
          table([
              ["Change", "Result", "Verdict"],
              ["Stop = 50% of the day's range", "+$3,567 vs +$8,859", "rejected"],
              ["Risk reduction, 1R / 50%", "3 of 5 years positive", "rejected"],
              ["Risk reduction, 0.75R / 75%", "+$1,281 over six years", "unproven"],
          ], [62 * mm, 62 * mm, 46 * mm])]

    E += [Spacer(1, 4),
          para("The 50% stop failed for a reason worth remembering: it raised the win rate "
               "from 38.5% to 47.2%, exactly as intended, but the average win fell from $209 "
               "to $111. Risk is fixed in dollars, so a wider stop buys a smaller position "
               "and the same move earns less. Fewer losses did not pay for smaller wins."),
          para("The 0.75R / 75% variant is the one open question. It showed a proper "
               "dose-response — 25% of risk left on gave -$263, 50% gave -$25, 75% gave "
               "+$437, and no intervention is zero by definition, so there is a peak rather "
               "than a slide. That is what a real effect looks like. It is still only "
               "+$2.53 a trade against a base of +$20.41, and it goes to demo beside the "
               "baseline rather than into production.")]

    E += [Paragraph("Sizing it for a prop account", S["h3"]),
          table([
              ["Risk per trade", "Return / yr", "Worst drawdown", "Survives a 10% limit?"],
              ["0.50%", "9.6%", "5.5%", "yes"],
              ["0.75%", "14.4%", "8.3%", "yes"],
              ["1.00%", "19.3%", "11.1%", "NO"],
              ["1.50%", "28.9%", "16.6%", "NO"],
          ], [36 * mm, 34 * mm, 42 * mm, 58 * mm])]

    E += [Spacer(1, 4),
          para("<b>Size differently for the challenge and the funded account.</b> A failed "
               "challenge costs a fee; a failed funded account costs the account and months "
               "of work. Higher risk gets you funded faster even after retries — 1.5% takes "
               "about 3 months against 12 at 0.5% — but the historical drawdown at 1% would "
               "breach a 10% limit. Pass at 1–1.5%, then drop to 0.5–0.75% once funded.")]

    # ------------------------------------------------------------- strategy 2
    E += [Paragraph("2 &nbsp;·&nbsp; US500 discretionary, afternoons", S["h2"]),
          para("Your own trading, measured over six weeks of live fills at a fixed $300 risk. "
               "It is the strongest thing in this document, and the smallest sample.", "lede")]

    E += [table([
              ["", "Trades", "Net", "Profit factor"],
              ["US500", "18", "+$2,238.94", "2.04"],
              ["Everything else", "32", "-$4,426.00", "—"],
              ["The account", "50", "-$2,187.06", "0.77"],
          ], [52 * mm, 26 * mm, 44 * mm, 48 * mm], foot=True)]

    E += [Spacer(1, 5),
          para("US500 made <b>+$124.39 a trade</b>; everything else lost <b>-$138.31</b>. A "
               "permutation test over the 50 trades puts that difference at <b>p = 0.035</b> "
               "— real, not noise. Trading US500 alone over those six weeks would have "
               "turned -$2,187 into +$2,239.")]

    E += [Paragraph("In R terms, at $300 = 1R", S["h3"]),
          table([
              ["Measure", "Value"],
              ["Trades", "15"],
              ["Win rate", "60%"],
              ["Average win", "+1.43R"],
              ["Average loss", "-1.13R"],
              ["Expectancy", "+0.403R per trade"],
              ["Strongest cut", "ORB US500 short: 6 trades, +$1,754, 83% win"],
          ], [58 * mm, 112 * mm])]

    E += [Spacer(1, 4),
          para("<b>The rules that follow from this.</b> Trade US500 in the afternoon only. "
               "Keep risk fixed — the journal shows a median loss of $318 against a $300 "
               "target, which is exactly what controlled risk looks like. No news trades: "
               "the one in the record lost $1,531 on a $600 intended risk, 2.6x, because a "
               "stop does not hold when it is most needed. No UK100, EU50, GER40 or JP225 "
               "until something changes.")]

    E += [Paragraph("Why the other instruments were dropped", S["h3"]),
          table([
              ["Instrument", "Trades", "Net", "Win rate"],
              ["UK100", "15", "-$2,163", "27%"],
              ["JP225", "9", "-$759", "22%"],
              ["EU50", "3", "-$719", "33%"],
              ["GER40", "1", "-$444", "0%"],
              ["US100  (news)", "3", "-$336", "67%"],
          ], [50 * mm, 26 * mm, 44 * mm, 50 * mm])]

    E += [Spacer(1, 4),
          para("UK100 was checked for a profitable subset and has none: long loses, short "
               "loses, ORB loses, inverse ORB loses, and the median trade is -$315. The "
               "worst week of the six was the week six instruments were traded; the best was "
               "five trades across three."),
          para("<b>The escalation episode.</b> Risk was raised from $300 to $450 at around "
               "$102,500 on the challenge. During that window US500 made +$1,146 at the "
               "larger size while everything else lost $3,406. The sizing decision cost an "
               "extra $1,072; the instrument selection cost three times that. The lesson is "
               "not that raising risk was wrong — it is that raising risk magnifies whatever "
               "you are actually doing, and four of the five things being done had no edge.")]

    # -------------------------------------------------------------- the method
    E += [Paragraph("3 &nbsp;·&nbsp; The method that found all this", S["h2"]),
          para("Twenty-plus bots were built before this, and all of them looked profitable "
               "in backtest. The difference was not better strategies — it was these rules.", "lede")]

    for h, b in [
        ("Reserve a year and spend it once",
         "Choose settings on some years, then test on a year you have never looked at. "
         "The moment you adjust anything after seeing that year, it is spent and can never "
         "be evidence again. The measured cost of ignoring this on US30 was +$55.60 a trade "
         "in-sample against -$23.21 out — a swing of $78.81 that existed only on paper."),
        ("Judge on the median trade, not the total",
         "A total can be one lucky trade. The median tells you what a typical trade does. "
         "US30 had a median of -$105 in every year it was tested, which was the tell long "
         "before the totals admitted it."),
        ("Strip out the best five trades",
         "If a five-year result turns negative when its top five trades are removed, the "
         "edge lives in a tail you cannot rely on. US30 turned negative on removing one "
         "trade from 432. NAS100 survives losing ten from 434."),
        ("Change one thing at a time, across every year",
         "A change that helps in one year and hurts in two is noise wearing a disguise. "
         "Decide the pass criteria before running it, and write them down — otherwise the "
         "criteria move to fit the result."),
        ("Count how many variants you tried",
         "The best of five attempts looks good whether or not anything is real. If a winner "
         "has no coherent pattern around it — neighbouring settings performing like "
         "neighbours — it is probably selection rather than an effect."),
    ]:
        E.append(KeepTogether([Paragraph(h, S["h3"]), para(b)]))

    E += [Spacer(1, 10), rule(), Spacer(1, 6),
          para("<b>What comes next.</b> Run the NAS100 bot on two demo accounts, baseline "
               "against the 0.75R / 75% variant, and let live fills settle the open question. "
               "Keep trading US500 in the afternoons at fixed risk. Re-check the US500 edge "
               "after another 50 trades — not to optimise it, only to confirm it holds on a "
               "larger sample. Leave the mornings empty until something earns the slot."),
          para("Every figure here is a backtest or a six-week journal. Neither is a promise. "
               "The point of the method in section 3 is that when something stops working, "
               "you will find out from the data rather than from the account balance.", "note")]

    doc.build(E)
    print("wrote", OUT, f"({os.path.getsize(OUT)/1024:.0f} KB)")


if __name__ == "__main__":
    build()
