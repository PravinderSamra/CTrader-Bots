# -*- coding: utf-8 -*-
"""Module 1 reference PDF: Carmine Rosato's supply & demand method.

Sources: four transcripts in 01-transcripts (How To DRAW S&D Zones; Complete S&D
Guide; Support & Resistance the RIGHT Way; S&D Zones The RIGHT WAY).

Every claim is tagged HIS RULE (stated in a transcript), HIS WORDS (quoted), or
NOT STATED (a gap, flagged rather than filled). ReportLab's built-in fonts are
WinAnsi, so the build asserts every character is cp1252-encodable.
"""
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Image,
                                KeepTogether, Table, TableStyle)

HERE = os.path.dirname(os.path.abspath(__file__))
DIA  = os.path.join(HERE, "03-diagrams")
OUT  = os.path.join(HERE, "02-documentation", "Carmine-SD-Module1.pdf")

INK, MUTE = colors.HexColor("#1b1b1b"), colors.HexColor("#6b6b6b")
GREEN, RED = colors.HexColor("#2e8b57"), colors.HexColor("#c0392b")
BLUE = colors.HexColor("#2d6cb3")

S = {}
S["h1"]   = ParagraphStyle("h1", fontName="Helvetica-Bold", fontSize=20, leading=24,
                           textColor=INK, spaceAfter=2)
S["sub"]  = ParagraphStyle("sub", fontName="Helvetica", fontSize=10, leading=14,
                           textColor=MUTE, spaceAfter=14)
S["h2"]   = ParagraphStyle("h2", fontName="Helvetica-Bold", fontSize=13, leading=16,
                           textColor=INK, spaceBefore=14, spaceAfter=5)
S["body"] = ParagraphStyle("body", fontName="Helvetica", fontSize=9.6, leading=14,
                           textColor=INK, spaceAfter=6)
S["quote"]= ParagraphStyle("quote", fontName="Helvetica-Oblique", fontSize=9.4,
                           leading=13.5, textColor=colors.HexColor("#333333"),
                           leftIndent=10, borderPadding=0, spaceBefore=3, spaceAfter=7)
S["cap"]  = ParagraphStyle("cap", fontName="Helvetica", fontSize=8.3, leading=11,
                           textColor=MUTE, spaceBefore=3, spaceAfter=11)
S["gap"]  = ParagraphStyle("gap", fontName="Helvetica", fontSize=9.3, leading=13,
                           textColor=colors.HexColor("#8a5a00"), spaceAfter=6)

def P(t, s="body"): return Paragraph(t, S[s])
def img(name, w=168*mm):
    p = os.path.join(DIA, name)
    from PIL import Image as PILImage
    iw, ih = PILImage.open(p).size
    return Image(p, width=w, height=w*ih/iw)

F = []
A = F.append

A(P("Supply &amp; Demand - Module 1", "h1"))
A(P("The zone: what it is, how to draw it, and when it is tradable.<br/>"
    "Method of Carmine Rosato, reconstructed from four of his videos. "
    "Compiled 18 November 2026.", "sub"))

A(P("How to read this", "h2"))
A(P("<b>HIS RULE</b> means he states it outright. <b>HIS WORDS</b> is a direct quote. "
    "<b>NOT STATED</b> flags something the method needs that he does not specify <i>in the "
    "four videos behind this module</i> - a gap left open rather than filled in with "
    "textbook theory. <b>NOT IN THESE VIDEOS</b> flags something he does teach, but "
    "elsewhere, outside this module's source set."))
A(P("Both labels describe the limits of the source set, not the limits of his method. "
    "Nothing here is generic supply-and-demand material dressed up as his."))

A(P("1. What a zone actually is", "h2"))
A(P("The market has two states. <b>Balance</b> is agreement - buyers and sellers happy at "
    "the same price, so it goes sideways and chops. <b>Imbalance</b> is disagreement - one "
    "side overwhelms the other and price moves away fast."))
A(P("A zone is created by the pair, in order: a balanced area, then a violent departure "
    "from it. The logic is that institutional orders resting in that balanced area never "
    "all got filled, because price left too quickly. Those unfilled orders are still "
    "sitting there. When price comes back, they fill, and that is what turns it."))
A(P("\"Retail traders do not move the markets. Institutional traders trade with such large "
    "size that their orders will influence the market, so we have to trade with them and "
    "wait for price to then hit their orders again.\"", "quote"))
A(P("This is also why he treats everything between zones as noise - the white space has no "
    "resting orders to react to, so it produces false breakouts and chop."))

A(KeepTogether([img("01-anatomy.png"),
    P("Demand: base, then a violent move up. Supply: base, then a violent move down. "
      "The box is drawn on the base, not on the move.", "cap")]))

A(P("2. How to draw one", "h2"))
A(P("<b>HIS RULE.</b> Start on a high timeframe and work down: daily, 4 hour, 3 hour, "
    "1 hour, 30 minute. He will use 15 minute only if the move out is very strong. "
    "Different timeframes reveal different zones, and the same area often looks like one "
    "candle up high and a proper consolidation lower down."))
A(P("<b>HIS RULE.</b> He marks the <b>single basing candle</b> rather than a cluster, and "
    "draws the rectangle forward in time. He is explicit that wick-versus-body does not "
    "matter much:"))
A(P("\"Some use the wick, some use the body, it is really all a preference. The areas are "
    "always going to be so close.\"", "quote"))
A(P("<b>HIS RULE.</b> Zones are drawn <b>by hand</b>, not by an indicator, and labelled "
    "with their price. He colours supply boxes red or pink and demand green."))

A(P("3. Which moves qualify - and which do not", "h2"))
A(P("<b>HIS RULE.</b> The quality of a zone is set by the <i>strength of the departure</i>, "
    "not by the base. Big decisive candles leaving the area with little overlap make a "
    "strong zone. A slow drift away makes nothing at all."))
A(P("\"I do not even pay attention to areas that look like this, because it is just more "
    "noise. You want to be focusing on clean, clear and aggressive strong initiative moves.\"",
    "quote"))
A(KeepTogether([img("02-strength.png"),
    P("If you have to squint to see the departure, there is no zone there.", "cap")]))

A(P("4. Freshness - a zone is ammunition and it gets spent", "h2"))
A(P("<b>HIS RULE.</b> Zones work best <b>untested</b>. Each time price returns, some of "
    "those resting orders get filled, so there are fewer left to turn it next time."))
A(P("\"Yesterday price rode into this area and pretty much knocked out all those sell "
    "orders. So today when we rallied into it, there is going to be less unfilled orders "
    "sitting at that area, so it is very easy for price then to break through.\"", "quote"))
A(P("<b>HIS RULE.</b> A zone that price breaks cleanly through is <b>deleted</b> - and the "
    "break itself is information, because it says the other side has taken control."))
A(KeepTogether([img("03-freshness.png"),
    P("First touch is the trade. By the second or third, the edge has largely gone.", "cap")]))

A(P("5. The two-step equation", "h2"))
A(P("This is the centre of his method and the part most people skip. A zone is never a "
    "reason to enter. It is only half of a trade."))
A(KeepTogether([img("04-equation.png", 160*mm)]))
A(P("\"Just because we are at a supply zone does not mean I have to take the market short. "
    "These are areas of interest. If the market was that easy, I do not even know what "
    "would happen.\"", "quote"))
A(P("He calls the zone his <b>advertiser</b> - like waiting for a car you want to come down "
    "to the price you are willing to pay. The advertiser tells you where to look. It does "
    "not tell you to buy."))
A(P("<b>HIS RULE.</b> He does not use limit orders resting in zones: \"it is not viable for "
    "myself, it is not reliable, and I never had success with it.\""))

A(P("6. What counts as confirmation", "h2"))
A(P("The <i>when and why</i> half. He lists these, in roughly this order of preference:"))
rows = [["Market structure break", "a trendline giving way, a higher low after a run of lower lows"],
        ["Candle / chart pattern", "wedge break, flag, rejection wicks at the zone edge"],
        ["A new opposing zone", "a fresh small zone forming inside the big one"],
        ["Order flow", "tape, level 2, footprint - aggressive versus passive participants"],
        ["Correlated markets", "NASDAQ, AAPL, AMZN agreeing with the S&amp;P read"]]
t = Table([[Paragraph("<b>%s</b>"%a, S["body"]), Paragraph(b, S["body"])] for a,b in rows],
          colWidths=[48*mm, 120*mm])
t.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"TOP"),
                       ("LINEBELOW",(0,0),(-1,-2),0.4,colors.HexColor("#dddddd")),
                       ("TOPPADDING",(0,0),(-1,-1),4),
                       ("BOTTOMPADDING",(0,0),(-1,-1),4)]))
A(t)
A(Spacer(1,8))
A(P("<b>NOT STATED.</b> He does not say in these videos how many of these he needs, or "
    "whether any single one is sufficient. In his worked example he had four lining up at "
    "once. Treat \"more is better\" as the only safe reading.", "gap"))

A(P("7. Why a level holds - two different mechanisms", "h2"))
A(P("He describes two, and they are not the same thing even though both end a move. "
    "Separating them matters, because on a footprint they look like opposites."))

A(P("7a. Absorption - effort with no reward", "h2"))
A(P("Buyers are aggressive and they keep coming. Passive sellers resting at the level take "
    "the other side of every one of them. Price cannot advance."))
A(P("\"All the aggressive buying, a plus 1200 delta, yet the market can't break out - there "
    "is a <b>passive seller sitting here absorbing</b> and the buyers are becoming "
    "exhausted.\"", "quote"))
A(P("At the double top he shows the same thing at a single price: a positive delta of 279, "
    "then 338, printing <i>above</i> the resistance."))
A(P("\"There's buyers showing a lot of effort. If they're showing effort the market "
    "theoretically should start moving up. If there's a lot of <b>effort but no reward</b>, "
    "the market only has one option - that's to move down.\"", "quote"))
A(P("<b>Signature: heavy volume, strongly one-sided delta, price flat.</b>"))

A(P("7b. Exhaustion - the last buyer buys", "h2"))
A(P("Different mechanism. Nobody is absorbing anything; the aggression simply runs out. "
    "No one is willing to pay those prices any more and the auction finishes."))
A(P("\"What we're going to see up here is a <b>volume tail</b>, and on this volume tail we "
    "can see that there is <b>29 total volume</b> ... the market moves up until the last "
    "buyer buys. This shows that the auction has finished at these prices.\"", "quote"))
A(P("<b>Signature: thin volume at the extreme.</b> Note the contrast with absorption - "
    "1200 against 29, at the same kind of turning point."))

A(KeepTogether([img("07-absorption-exhaustion.png"),
    P("Same outcome, opposite footprint. Heavy one-sided volume going nowhere is "
      "absorption; almost no volume at all is exhaustion.", "cap")]))

A(P("The two can chain, and he says so in one breath: \"there is a passive seller sitting "
    "here absorbing <i>and</i> the buyers are becoming exhausted.\" Absorption is often the "
    "cause and exhaustion the result - the passive side quietly drains the aggressive side "
    "until it gives up. They are still worth reading separately, because absorption is "
    "visible while it is happening and exhaustion is mostly visible once it has."))

A(P("<b>NOT IN THESE VIDEOS.</b> These four transcripts describe absorption and exhaustion "
    "in footprint and delta terms only - the volume-profile shape vocabulary does not "
    "appear in them. In those terms absorption tends to print as a bulge of volume at the "
    "extreme - a <b>P</b> at a high, a <b>b</b> at a low - while exhaustion prints as the "
    "thin tail he does name. He does teach profile shapes, in videos outside this module's "
    "source set, so this is a gap in the sources rather than in the method. Flagged to be "
    "picked up in a later module once those transcripts are in.", "gap"))

A(P("7c. The mirror - what makes a level weak", "h2"))
A(P("The same logic inverted, and this is the part that reverses how most people read "
    "volume at a level. A level created by <i>aggression</i> is weak."))
A(P("\"What makes a <b>weak</b> support level is if there's a lot of aggressive buyers "
    "trying to bring the market up higher. What makes a <b>strong</b> support level is if "
    "there's a lot of aggressive sellers that can't bring the market lower.\"", "quote"))
A(P("So the question at any level is not \"how much buying is there\" but <b>which side is "
    "passive</b>. Strong means the opposite side was absorbed or exhausted. Weak means "
    "aggression alone is propping it up - and he expects that one to break."))

A(P("8. The trend filter", "h2"))
A(P("<b>HIS RULE.</b> Supply and demand is a reversal strategy, so it needs the larger trend "
    "behind it. In a downtrend, demand zones stop working - buyers simply do not show up - "
    "while supply zones become very reliable. In an uptrend it is the other way round."))
A(P("The practical consequence is that the weak-side zone becomes a <b>target</b> instead of "
    "an entry. In a downtrend he shorts supply and takes profit at demand."))
A(P("<b>WHY THAT IS.</b> A trend is <i>defined</i> by which zones keep failing. An uptrend is "
    "price repeatedly pushing up <i>through</i> supply - if supply held, the uptrend would "
    "have stopped. The same move keeps bouncing off demand. So in an uptrend the demand "
    "zones are the reliable ones and the supply zones are the ones that break. A downtrend "
    "is exactly that mirrored: demand is what keeps getting cut through.", "gap"))
A(KeepTogether([img("09-trend-on-price.png", 168*mm)]))
A(P("Read it as: <b>enter on the zone that points the same way as the trend</b> - demand in an "
    "uptrend, supply in a downtrend. The zone on the other side is still worth drawing, but "
    "only as the place you take profit.", "gap"))
A(KeepTogether([img("05-trend.png", 140*mm)]))
A(P("<b>NOT STATED.</b> He does not define the trend mechanically anywhere in these four "
    "videos - no moving average, no lookback. It is eyeballed from higher-timeframe "
    "structure.", "gap"))

A(P("9. Fading the obvious", "h2"))
A(P("Running underneath everything is a contrarian filter he applies to his own levels."))
A(P("\"If my 80-year-old grandmother could go and pull up a chart and plot a support or "
    "resistance level, then the reliability of it is going to be very minimal.\"", "quote"))
A(P("He uses obvious levels as places where other traders get <b>trapped</b>, not as "
    "breakout signals. A supply zone sitting just above an obvious previous high is his "
    "favourite setup, because breakout buyers get long into it and their stops fuel the "
    "reversal."))
A(KeepTogether([img("08-trap.png"),
    P("He calls this \"where there is pain, there is gain\" - the stops of trapped traders "
      "are the fuel for the move he is trading.", "cap")]))
A(P("He gives three ways to play an obvious level: fade the breakout (his favourite), trade "
    "the break-and-retest, or enter <i>before</i> the level and use the break as his target."))

A(P("10. Entry, stop and target", "h2"))
A(KeepTogether([img("06-entry.png")]))
A(P("<b>HIS RULE.</b> The stop goes below the swing low that produced the turn - the "
    "structure he is trading - <b>not</b> at the far edge of the zone. He only widens it to "
    "the zone edge if the resulting reward-to-risk still justifies the trade."))
A(P("<b>HIS RULE.</b> Targets are the opposing zone, recent swing structure, or the next "
    "zone treated as a magnet. In his worked example he risked about 8 points on the S&amp;P "
    "against a target roughly 60 points away."))
A(P("<b>NOT STATED.</b> No minimum reward-to-risk, scaling rule or time stop appears in "
    "these videos. He does admit to exiting a runner too early and says only that he "
    "\"followed the plan\".", "gap"))

A(P("11. His daily routine", "h2"))
A(P("He publishes a pre-market plan every day containing the zones he is watching, which he "
    "frames as <b>if-then scenarios</b> rather than predictions. His 28 June example ran: "
    "supply at 3949, demand at 3890-3875, next demand 3828. Scenario one, the market holds "
    "between them. Scenario two, it loses 3890 and he targets 3828."))
A(P("That is the shape worth copying - levels marked in advance, each with a stated "
    "consequence, so the decision is made before the session rather than during it."))

A(P("12. The one-page version", "h2"))
rules = [
 ("Draw", "Base, then a violent departure. Mark the base. High timeframe down to 30 minutes."),
 ("Filter", "Strong departure or no zone. Fresh only. Delete a zone once it breaks."),
 ("Never", "Enter just because price is in a zone. Rest a limit order in one."),
 ("Wait", "Structure break, pattern, order flow, or correlated markets - the validator."),
 ("Align", "Trade the zone that agrees with the higher-timeframe trend. The other one is a target."),
 ("Prefer", "Levels where the obvious crowd is trapped on the wrong side."),
 ("Risk", "Stop below the turn, not the zone edge. Target the opposing zone."),
 ("Record", "Journal every setup - he is explicit that the edge comes from your own database."),
]
t = Table([[Paragraph("<b>%s</b>"%a, S["body"]), Paragraph(b, S["body"])] for a,b in rules],
          colWidths=[26*mm, 142*mm])
t.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"TOP"),
                       ("LINEBELOW",(0,0),(-1,-2),0.4,colors.HexColor("#dddddd")),
                       ("TOPPADDING",(0,0),(-1,-1),4),
                       ("BOTTOMPADDING",(0,0),(-1,-1),4)]))
A(t)
A(Spacer(1,12))
A(P("Module 1 of 4. Next: context and zone selection, then the order-flow trigger, then the "
    "complete method and risk. Nothing in this document has been tested - it is a faithful "
    "record of what he teaches, not a claim that it works.", "cap"))

# WinAnsi guard
def walk(fl):
    for f in fl:
        if isinstance(f, Paragraph): yield f.text
        elif isinstance(f, KeepTogether):
            for s in walk(f._content): yield s
        elif isinstance(f, Table):
            for row in f._cellvalues:
                for c in row:
                    if isinstance(c, Paragraph): yield c.text
bad = set()
for s in walk(F):
    for ch in s:
        try: ch.encode("cp1252")
        except UnicodeEncodeError: bad.add(ch)
if bad:
    raise SystemExit("non-WinAnsi characters present: %r" % sorted(bad))

doc = SimpleDocTemplate(OUT, pagesize=A4,
                        leftMargin=21*mm, rightMargin=21*mm,
                        topMargin=18*mm, bottomMargin=16*mm,
                        title="Carmine Rosato - Supply & Demand, Module 1",
                        author="Compiled for Vanessa")
def page(canv, d):
    canv.saveState()
    canv.setFont("Helvetica", 7.6); canv.setFillColor(MUTE)
    canv.drawString(21*mm, 10*mm, "Supply & Demand - Module 1: The Zone")
    canv.drawRightString(A4[0]-21*mm, 10*mm, "page %d" % d.page)
    canv.restoreState()
doc.build(F, onFirstPage=page, onLaterPages=page)
print("wrote", OUT, os.path.getsize(OUT), "bytes")
