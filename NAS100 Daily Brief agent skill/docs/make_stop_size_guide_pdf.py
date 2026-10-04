"""Build the plain-English stop-size/target guide as a printable A4 PDF.

Everything here is text and numbers from H25. No Unicode arrows, no <= or >=
glyphs: the ReportLab built-in fonts use WinAnsi, which has no glyph for them
and draws a black box instead. Words are used in their place.
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                TableStyle, KeepTogether, HRFlowable)

OUT = "NAS100-stop-size-target-guide.pdf"

INK   = colors.HexColor("#171c24")
INK2  = colors.HexColor("#4b5566")
INK3  = colors.HexColor("#7a8699")
RULE  = colors.HexColor("#d4dae3")
BAND  = colors.HexColor("#eef1f5")
ACC   = colors.HexColor("#2f5d7c")
ACCBG = colors.HexColor("#dce7ef")
POSBG = colors.HexColor("#e2f0e8")
NEGBG = colors.HexColor("#f7e3e1")
NEG   = colors.HexColor("#9c3027")
POS   = colors.HexColor("#1f6b4a")

S = {
 "h1": ParagraphStyle("h1", fontName="Helvetica-Bold", fontSize=20, leading=23,
                      textColor=INK, spaceAfter=3),
 "deck": ParagraphStyle("deck", fontName="Helvetica", fontSize=10.5, leading=15,
                        textColor=INK2, spaceAfter=0),
 "h2": ParagraphStyle("h2", fontName="Helvetica-Bold", fontSize=13, leading=16,
                      textColor=INK, spaceBefore=16, spaceAfter=5),
 "h3": ParagraphStyle("h3", fontName="Helvetica-Bold", fontSize=10.5, leading=13,
                      textColor=ACC, spaceBefore=10, spaceAfter=3),
 "p": ParagraphStyle("p", fontName="Helvetica", fontSize=10, leading=14.5,
                     textColor=INK, spaceAfter=7, alignment=TA_LEFT),
 "small": ParagraphStyle("small", fontName="Helvetica", fontSize=8.6, leading=12.2,
                         textColor=INK2, spaceAfter=5),
 "cap": ParagraphStyle("cap", fontName="Helvetica-Oblique", fontSize=8.2, leading=11,
                       textColor=INK3, spaceBefore=3, spaceAfter=9),
 "eyebrow": ParagraphStyle("eyebrow", fontName="Helvetica-Bold", fontSize=7.6,
                           leading=10, textColor=INK3, spaceAfter=5),
 "big": ParagraphStyle("big", fontName="Helvetica-Bold", fontSize=15, leading=19,
                       textColor=ACC, spaceBefore=3, spaceAfter=3),
 "cell": ParagraphStyle("cell", fontName="Helvetica", fontSize=8.6, leading=11.4,
                        textColor=INK),
}


def P(t, s="p"):
    return Paragraph(t, S[s])


def grid(data, widths, head_rows=1, align="CENTER", extra=None):
    t = Table(data, colWidths=widths, repeatRows=head_rows, hAlign="LEFT")
    cmds = [
        ("FONT", (0, 0), (-1, head_rows - 1), "Helvetica-Bold", 8.1),
        ("TEXTCOLOR", (0, 0), (-1, head_rows - 1), INK3),
        ("BACKGROUND", (0, 0), (-1, head_rows - 1), BAND),
        ("FONT", (0, head_rows), (-1, -1), "Helvetica", 9),
        ("FONT", (0, head_rows), (0, -1), "Helvetica-Bold", 9),
        ("TEXTCOLOR", (0, head_rows), (-1, -1), INK),
        ("ALIGN", (1, 0), (-1, -1), align),
        ("ALIGN", (0, 0), (0, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.4, RULE),
        ("TOPPADDING", (0, 0), (-1, -1), 4.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4.5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]
    t.setStyle(TableStyle(cmds + (extra or [])))
    return t


def callout(flowables, bg=ACCBG, bar=ACC):
    t = Table([[flowables]], colWidths=[165 * mm], hAlign="LEFT")
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), bg),
        ("LINEBEFORE", (0, 0), (0, -1), 2.2, bar),
        ("LEFTPADDING", (0, 0), (-1, -1), 11),
        ("RIGHTPADDING", (0, 0), (-1, -1), 11),
        ("TOPPADDING", (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
    ]))
    return t


story = []
A = story.append

# ---------------------------------------------------------------- page 1
A(P("NAS100 &nbsp;|&nbsp; SWEEP AND REVERSE SETUP &nbsp;|&nbsp; 822 TRADES, 19 DAYS", "eyebrow"))
A(P("How big a target to ask for", "h1"))
A(P("A plain-English guide to picking your take-profit from the size of your stop. "
    "Written 4 October 2026.", "deck"))
A(Spacer(1, 11))
A(HRFlowable(width="100%", thickness=0.7, color=RULE, spaceAfter=12))

A(P("The one thing to understand", "h2"))
A(P("You already spotted it. Here it is measured.", "p"))
A(P("When this setup works, price runs <b>about 50 to 60 points</b> in your favour. "
    "That is true whether your stop was 20 points or 130 points. The market does not "
    "know how wide your stop is and does not travel further because of it.", "p"))
A(P("So R is not a measure of distance. R is a measure of <i>your risk</i>. "
    "The same 55-point move is 2.8R if your stop is 20 points and 0.4R if your stop "
    "is 130 points. Nothing about the trade changed except your stop.", "p"))
A(Spacer(1, 3))
A(callout([
    P("The rule of thumb", "eyebrow"),
    P("Target in R = 55 divided by your stop in points", "big"),
    P("30-point stop, ask for about 1.8R. &nbsp; 55-point stop, ask for about 1R. "
      "&nbsp; 90-point stop, ask for about 0.6R.", "small"),
]))
A(Spacer(1, 6))
A(P("Your guesses were close. You said 1R on a 30-point stop and half an R on a "
    "70-point stop. The data says a shade more generous than that on both.", "p"))

A(P("The lookup table", "h2"))
A(P("Find your stop size on the left. The percentages are how often price actually "
    "got to that target before your stop was hit.", "p"))

HEAD = ["Your stop", "0.5R", "0.75R", "1R", "1.5R", "2R", "3R", "Trades"]
ROWS = [
 ["25pts or less", "85%", "79%", "72%", "66%", "56%", "49%", "87"],
 ["26 to 40",      "76%", "69%", "59%", "50%", "45%", "33%", "201"],
 ["41 to 55",      "75%", "61%", "56%", "45%", "39%", "25%", "126"],
 ["56 to 75",      "69%", "59%", "52%", "41%", "32%", "14%", "124"],
 ["76 to 100",     "67%", "57%", "44%", "21%", "15%", "4%",  "117"],
 ["Over 100",      "56%", "37%", "25%", "9%",  "6%",  "1%",  "167"],
]
W = [31*mm, 17*mm, 17*mm, 17*mm, 17*mm, 17*mm, 17*mm, 18*mm]
A(grid([HEAD] + ROWS, W, extra=[
    ("TEXTCOLOR", (7, 1), (7, -1), INK3),
    ("BACKGROUND", (3, 1), (3, 4), POSBG),
    ("BACKGROUND", (3, 5), (3, 6), NEGBG),
    ("TEXTCOLOR", (3, 5), (3, 6), NEG),
]))
A(P("Read the 1R column down the page: 72%, 59%, 56%, 52%, 44%, 25%. Same setup, "
    "same entry trigger, same market. The only thing that changed is how wide the "
    "stop was.", "cap"))

A(P("What this means in practice", "h2"))
A(P("A fixed 'I always take 1R' rule is not one rule. It is six different bets. "
    "On a tight stop you are leaving most of the move on the table. On a wide stop "
    "you are asking for something that happens a quarter of the time.", "p"))

# ---------------------------------------------------------------- page 2
A(Spacer(1, 4))
A(HRFlowable(width="100%", thickness=0.7, color=RULE, spaceAfter=10))
A(P("What to do at the desk", "h2"))
A(P("Measure entry to stop in points. Find your band. Do the thing in the last "
    "column and nothing else.", "p"))

HEAD2 = ["Your stop", "What to do", "What it pays"]
ROWS2 = [
 [P("<b>25pts or less</b>", "cell"),
  P("Set a hard 3R target and leave it alone. This is the one case where you should "
    "be greedy.", "cell"),
  P("+1.41R per trade", "cell")],
 [P("<b>26 to 40</b>", "cell"),
  P("Trail your stop 1R behind the best price once you are 1R up. Better than any "
    "fixed target here.", "cell"),
  P("+0.59R per trade", "cell")],
 [P("<b>41 to 55</b>", "cell"),
  P("Hard target at 2R or 3R. Trailing does not help in this band.", "cell"),
  P("+0.39R per trade", "cell")],
 [P("<b>56 to 75</b>", "cell"),
  P("Trail 0.5R behind the best price once you are 1R up. Tighter trail than the "
    "26 to 40 band.", "cell"),
  P("+0.41R per trade", "cell")],
 [P("<b>76 to 100</b>", "cell"),
  P("Cap it at 1R. Move the stop to breakeven at 0.5R. Do not reach past 1R here.", "cell"),
  P("+0.21R per trade", "cell")],
 [P("<b>Over 100</b>", "cell"),
  P("<b>Do not take the trade.</b> Or take it at a fraction of your normal size.", "cell"),
  P("Nothing works", "cell")],
]
A(grid([HEAD2] + ROWS2, [26*mm, 93*mm, 32*mm], align="LEFT", extra=[
    ("BACKGROUND", (0, 6), (-1, 6), NEGBG),
    ("BACKGROUND", (0, 1), (-1, 1), POSBG),
]))
A(P("'Pays' is the average result per trade in R, including the losers. Spread and "
    "commission are not in these numbers.", "cap"))

A(P("Three worked examples", "h2"))

A(P("You short at 30,800. Your stop is at 30,830.", "h3"))
A(P("That is a 30-point stop, so you are in the 26 to 40 band. Ask for roughly 1.8R, "
    "which is about 55 points, so a target around 30,745. But the better play in this "
    "band is to trail: once price reaches 30,770 (that is 1R), start dragging your stop "
    "to sit 30 points above the lowest price seen. You reach 1R about 59% of the time "
    "and 2R about 45% of the time.", "p"))

A(P("You short at 30,800. Your stop is at 30,870.", "h3"))
A(P("A 70-point stop, so the 56 to 75 band. Your instinct said half an R. The data "
    "says ask for a bit more than that but manage it tighter: trail 0.5R, which is 35 "
    "points, behind the best price once you are 70 points up. You reach 1R about 52% "
    "of the time. Reaching 3R happens 14% of the time, so do not sit there waiting "
    "for it.", "p"))

A(P("You short at 30,800. Your stop is at 30,920.", "h3"))
A(P("A 120-point stop. Walk away. Every exit rule tested on a stop this wide "
    "produces between minus 0.15R and plus 0.14R. You are risking 120 points to make "
    "nothing on average. If the stop has to be that wide, the sweep was too big and "
    "the setup is not the one you want.", "p"))

# ---------------------------------------------------------------- page 3
A(Spacer(1, 4))
A(HRFlowable(width="100%", thickness=0.7, color=RULE, spaceAfter=10))
A(P("About moving your stop to breakeven", "h2"))
A(P("Moving the stop to entry once you are 1R up is a trade, not a free lunch. "
    "You buy fewer full losses and you pay for them with fewer winners. "
    "Whether it is worth it depends entirely on your stop size.", "p"))

HEAD3 = ["Your stop", "Reach 2R, stop left alone", "Reach 2R, stop moved",
         "Full losses, left alone", "Full losses, stop moved"]
ROWS3 = [
 ["25pts or less", "62%", "60%", "32%", "20%"],
 ["26 to 40",      "48%", "39%", "46%", "25%"],
 ["41 to 55",      "42%", "30%", "51%", "35%"],
 ["56 to 75",      "36%", "31%", "46%", "34%"],
 ["76 to 100",     "17%", "16%", "58%", "38%"],
 ["Over 100",      "6%",  "6%",  "33%", "29%"],
]
A(grid([[P(f"<b>{h}</b>" if i == 0 else h, "cell") for i, h in enumerate(HEAD3)]] + ROWS3,
       [30*mm, 32*mm, 30*mm, 32*mm, 31*mm], extra=[
    ("FONT", (0, 0), (-1, 0), "Helvetica-Bold", 8.1),
    ("BACKGROUND", (4, 1), (4, -1), POSBG),
    ("TEXTCOLOR", (4, 1), (4, -1), POS),
]))
A(P("Good trade on wide stops: at 76 to 100 points it costs you one 2R winner in "
    "seventeen and removes a fifth of your full losses. Expensive in the middle: at "
    "26 to 40 points it costs nine winners per hundred.", "cap"))

A(P("The four things that would make these numbers wrong", "h2"))

A(P("1. Spread and commission are not included.", "h3"))
A(P("The cost in R is the spread divided by your stop. A 2-point spread is 0.11R on "
    "a 20-point stop but only 0.015R on a 130-point stop. So it bites the tight-stop "
    "numbers about seven times harder. The order of the table survives, but the "
    "+1.41R on tight stops is really more like +1.30R.", "p"))

A(P("2. The tight-stop row has the best numbers and the weakest evidence.", "h3"))
A(P("A 20-point stop only happens when the sweep was small, which means that row is "
    "quietly selecting for calm market conditions. 87 trades across 51 separate "
    "level-and-day combinations.", "p"))

A(P("3. The 'over 100 points' row mostly never finished.", "h3"))
A(P("Between a third and two thirds of those trades neither hit the target nor the "
    "stop before the day ended, against 1 to 8 per cent in the tight bands. Their "
    "numbers are based on where price happened to be at the close, not on a trade "
    "that resolved.", "p"))

A(P("4. One month of a market that was going up.", "h3"))
A(P("19 trading days. 822 trades but only 139 separate level-and-day combinations, "
    "because one level swept six times in a day counts six times here and really only "
    "tells you one thing. Anything that favours buying is flattered by this window.", "p"))

A(Spacer(1, 6))
A(callout([
    P("If you only remember one line", "eyebrow"),
    P("The move is about 55 points. Divide that by your stop to get your target in R. "
      "If your stop is over 100 points, there is no target that makes the trade "
      "worth taking.", "small"),
], bg=BAND, bar=INK3))

A(Spacer(1, 10))
A(P("Source: H25 in HYPOTHESES.md. Numbers from research/wall-studies/"
    "09_target_by_stop_size.py and 10_exit_rules.py in the CTrader-Bots repo. "
    "Not a backtest: no spread, no slippage, no commission, no partial fills, one "
    "position at a time. This tells you how big a target to ask for once you are in "
    "a trade. It does not tell you whether to be in one. Re-run both scripts after "
    "another 10 to 15 trading days before leaning on any single row.", "cap"))

doc = SimpleDocTemplate(OUT, pagesize=A4,
                        leftMargin=22*mm, rightMargin=22*mm,
                        topMargin=18*mm, bottomMargin=16*mm,
                        title="NAS100 stop size and target guide",
                        author="NAS100 Daily Brief")


def footer(canv, d):
    canv.saveState()
    canv.setFont("Helvetica", 7.5)
    canv.setFillColor(INK3)
    canv.drawString(22*mm, 10*mm, "NAS100 sweep-and-reverse: how big a target to ask for")
    canv.drawRightString(A4[0] - 22*mm, 10*mm, f"Page {canv.getPageNumber()}")
    canv.setStrokeColor(RULE)
    canv.setLineWidth(0.4)
    canv.line(22*mm, 13*mm, A4[0] - 22*mm, 13*mm)
    canv.restoreState()


doc.build(story, onFirstPage=footer, onLaterPages=footer)
print("wrote", OUT)
