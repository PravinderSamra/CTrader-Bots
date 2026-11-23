# -*- coding: utf-8 -*-
"""One-page daily pre-market checklist, drawn from the four modules."""
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

HERE = os.path.dirname(os.path.abspath(__file__))
OUT  = os.path.join(HERE, "02-documentation", "Daily-Prep-Checklist.pdf")

INK, MUTE = colors.HexColor("#1b1b1b"), colors.HexColor("#6b6b6b")
BLUE, GREEN, RED = (colors.HexColor("#2d6cb3"), colors.HexColor("#2e8b57"),
                    colors.HexColor("#c0392b"))

S = {}
S["h1"]  = ParagraphStyle("h1", fontName="Helvetica-Bold", fontSize=17, leading=20,
                          textColor=INK, spaceAfter=1)
S["sub"] = ParagraphStyle("sub", fontName="Helvetica", fontSize=8.8, leading=12,
                          textColor=MUTE, spaceAfter=8)
S["band"]= ParagraphStyle("band", fontName="Helvetica-Bold", fontSize=8.4, leading=11,
                          textColor=colors.white, spaceBefore=0, spaceAfter=0)
S["h2"]  = ParagraphStyle("h2", fontName="Helvetica-Bold", fontSize=10.2, leading=13,
                          textColor=INK, spaceBefore=7, spaceAfter=2)
S["item"]= ParagraphStyle("item", fontName="Helvetica", fontSize=8.6, leading=11.6,
                          textColor=INK, leftIndent=11, firstLineIndent=-11,
                          spaceAfter=1.5)
S["note"]= ParagraphStyle("note", fontName="Helvetica-Oblique", fontSize=8.0, leading=10.5,
                          textColor=MUTE, leftIndent=11, spaceAfter=2)
S["fill"]= ParagraphStyle("fill", fontName="Helvetica", fontSize=9.2, leading=15,
                          textColor=INK, leftIndent=11, spaceAfter=1)
S["nev"] = ParagraphStyle("nev", fontName="Helvetica", fontSize=8.5, leading=11.4,
                          textColor=INK, leftIndent=11, firstLineIndent=-11,
                          spaceAfter=1.5)

def P(t, s="item"): return Paragraph(t, S[s])
def box(t): return Paragraph("[&nbsp;&nbsp;]&nbsp; " + t, S["item"])
def band(t, col):
    tb = Table([[Paragraph(t, S["band"])]], colWidths=[168*mm], rowHeights=[6.6*mm])
    tb.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,-1), col),
                            ("LEFTPADDING", (0,0), (-1,-1), 6),
                            ("VALIGN", (0,0), (-1,-1), "MIDDLE")]))
    return tb

F = []; A = F.append

A(P("Daily Prep", "h1"))
A(P("Carmine Rosato's method, in the order he runs it. Fifteen minutes before the open. "
    "If a step cannot be answered, that <i>is</i> the answer.", "sub"))

A(band("BEFORE THE OPEN", MUTE))
A(P("1 &#183; CONTEXT &#8212; what is the story today?", "h2"))
A(box("Daily and 4H: higher highs and higher lows, lower lows and lower highs, or flat?"))
A(box("<b>Balanced</b> (a range) or <b>imbalanced</b> (trending)? Balance means fade the "
      "extremes. Imbalance means trade continuation."))
A(box("How did zones behave <b>yesterday</b>? Did demand hold, or get cut through? "
      "<i>Same reaction, same result.</i>"))
A(box("Do related markets agree? For ES: the mega-cap names that drive it, NQ, and "
      "<b>VIX</b> - \"keep an eye on VIX... that's just going to support and fuel a "
      "further rally.\""))
A(box("Check <b>ForexFactory</b> for today's news - central-bank speakers, data "
      "releases, earnings. Mark the times on the chart."))
A(P("8:30am ET = 1:30pm UK, an hour before the open. 10:00am ET = 3:00pm UK, which lands "
    "<i>inside</i> your session, half an hour after it starts.", "note"))

A(P("2 &#183; LEVELS &#8212; where would I act?", "h2"))
A(box("Draw top-down: weekly, daily, 4H, 1H, 30m, 15m."))
A(box("Mark the <b>base</b> that came before the violent move, not the move itself."))
A(box("Delete any zone price has already gone through. It is not weakened, it is gone."))
A(box("Pick the <b>one key level</b> that matters today. Two numbers, a band - never a "
      "single price."))

A(P("3 &#183; THE PLAN &#8212; write both sides, before the open", "h2"))
A(P("If it holds above &nbsp;<b>______________</b>&nbsp; &#8594; long, target "
    "&nbsp;<b>______________</b>", "fill"))
A(P("If it rejects and loses &nbsp;<b>______________</b>&nbsp; &#8594; short, target "
    "&nbsp;<b>______________</b>", "fill"))
A(box("At least <b>2:1</b> on each, measured from the entry I would <i>actually</i> get - "
      "not the ideal one."))
A(box("I am not predicting which one happens. I am writing both and letting price pick."))

A(band("DURING THE SESSION", BLUE))
A(P("4 &#183; THE GATE &#8212; all three, or no trade", "h2"))
A(box("<b>CONTEXT</b> - does today's story support this side?"))
A(box("<b>LOCATION</b> - is price <i>at</i> my level, or just near it?"))
A(box("<b>CONFIRMATION</b> - is the side I want actually showing up?"))
A(P("Until you have real order-flow data: use acceptance vs rejection. Price turned away "
    "quickly = the level held. Price consolidating at the level = it is failing in slow "
    "motion, so switch to continuation.", "note"))

A(band("AFTER THE CLOSE", GREEN))
A(P("5 &#183; REVIEW &#8212; five minutes, every day", "h2"))
A(box("Did I follow the plan? (not: did I make money)"))
A(box("If I lost, was it the <b>analysis</b> or the <b>behaviour</b>?"))
A(box("Record the screen. Watch back what you would have done differently."))

A(band("THE NEVERS", RED))
A(Spacer(1, 3))
for t in [
    "Never trade the <b>middle</b> of a range.",
    "Never be the <b>first buyer or first seller</b>. Let the second test prove it.",
    "Never buy the breakout. Let it break, mark where the buyers showed up, buy the pullback.",
    "Never long above the high of day, or short below the low of day.",
    "<b>If I miss my planned entry, I do not create a trade in the opposite direction.</b> "
    "Wait for new development, or sit out.",
    "A missed move is not a loss. It is information about who is in control.",
    "Skipping the day is a valid outcome. \"Do I skip days because I don't see a setup? "
    "100%. 100%.\"",
]:
    A(Paragraph("&#8212;&nbsp; " + t, S["nev"]))

bad = set()
for f in F:
    if isinstance(f, Paragraph):
        for ch in f.text:
            try: ch.encode("cp1252")
            except UnicodeEncodeError: bad.add(ch)
if bad: raise SystemExit("non-WinAnsi: %r" % sorted(bad))

doc = SimpleDocTemplate(OUT, pagesize=A4, leftMargin=21*mm, rightMargin=21*mm,
                        topMargin=15*mm, bottomMargin=12*mm,
                        title="Daily Prep Checklist", author="Carmine-SD syllabus")
doc.build(F)
print("wrote", OUT, os.path.getsize(OUT), "bytes")
