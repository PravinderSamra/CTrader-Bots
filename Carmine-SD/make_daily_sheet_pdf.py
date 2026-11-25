# -*- coding: utf-8 -*-
"""Printable one-page daily plan & review sheet for ES, to fill in by hand."""
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

HERE = os.path.dirname(os.path.abspath(__file__))
OUT  = os.path.join(HERE, "02-documentation", "ES-Daily-Sheet.pdf")

INK  = colors.HexColor("#1b1b1b")
MUTE = colors.HexColor("#6b6b6b")
RULE = colors.HexColor("#b9bdc2")
BLUE = colors.HexColor("#2d6cb3")
GREEN= colors.HexColor("#2e8b57")
RED  = colors.HexColor("#c0392b")
W    = 174*mm

S = {
 "h1":  ParagraphStyle("h1", fontName="Helvetica-Bold", fontSize=18, leading=21,
                       textColor=INK),
 "sub": ParagraphStyle("sub", fontName="Helvetica", fontSize=8.6, leading=11,
                       textColor=MUTE),
 "band":ParagraphStyle("band", fontName="Helvetica-Bold", fontSize=8.6, leading=11,
                       textColor=colors.white),
 "lab": ParagraphStyle("lab", fontName="Helvetica-Bold", fontSize=9, leading=12,
                       textColor=INK),
 "opt": ParagraphStyle("opt", fontName="Helvetica", fontSize=9, leading=12,
                       textColor=colors.HexColor("#333333")),
 "tiny":ParagraphStyle("tiny", fontName="Helvetica-Oblique", fontSize=7.6,
                       leading=10, textColor=MUTE),
}
def P(t, s="lab"): return Paragraph(t, S[s])

def band(t, col):
    tb = Table([[Paragraph(t, S["band"])]], colWidths=[W], rowHeights=[6.4*mm])
    tb.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),col),
                            ("LEFTPADDING",(0,0),(-1,-1),6),
                            ("VALIGN",(0,0),(-1,-1),"MIDDLE")]))
    return tb

def field(label, lw=46*mm, h=8.2*mm, n=1):
    """Label on the left, ruled writing space on the right."""
    rows = [[P(label), ""]] + [["", ""] for _ in range(n-1)]
    tb = Table(rows, colWidths=[lw, W-lw], rowHeights=[h]*n)
    tb.setStyle(TableStyle([
        ("LINEBELOW",(1,0),(1,-1),0.6,RULE),
        ("VALIGN",(0,0),(-1,-1),"BOTTOM"),
        ("LEFTPADDING",(0,0),(-1,-1),0),
        ("BOTTOMPADDING",(0,0),(-1,-1),1.5),
    ]))
    return tb

def choice(label, options, lw=46*mm, h=8.2*mm):
    tb = Table([[P(label), P("&nbsp;&nbsp;&nbsp;".join(options), "opt")]],
               colWidths=[lw, W-lw], rowHeights=[h])
    tb.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"BOTTOM"),
                            ("LEFTPADDING",(0,0),(-1,-1),0),
                            ("BOTTOMPADDING",(0,0),(-1,-1),1.5)]))
    return tb

def pair(l1, l2, w1=34*mm, w2=18*mm):
    """Two ruled fields side by side with wider labels."""
    rw = (W - w1 - w2) / 2.0
    tb = Table([[P(l1), "", P(l2), ""]], colWidths=[w1, rw, w2, rw],
               rowHeights=[8.6*mm])
    tb.setStyle(TableStyle([
        ("LINEBELOW",(1,0),(1,0),0.6,RULE),
        ("LINEBELOW",(3,0),(3,0),0.6,RULE),
        ("VALIGN",(0,0),(-1,-1),"BOTTOM"),
        ("LEFTPADDING",(0,0),(-1,-1),0),
        ("LEFTPADDING",(2,0),(2,0),7),
        ("RIGHTPADDING",(1,0),(1,0),7),
        ("BOTTOMPADDING",(0,0),(-1,-1),1.5),
    ]))
    return tb

F = []; A = F.append
hdr = Table([[P("ES  -  Daily Plan &amp; Review", "h1"), P("DATE", "lab"), ""]],
            colWidths=[W-52*mm, 14*mm, 38*mm], rowHeights=[11*mm])
hdr.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"BOTTOM"),
                         ("LINEBELOW",(2,0),(2,0),0.6,RULE),
                         ("LEFTPADDING",(0,0),(-1,-1),0),
                         ("BOTTOMPADDING",(0,0),(-1,-1),1.5)]))
A(hdr)
A(P("Written before 14:30 UK. If a step cannot be answered, that is the answer.", "sub"))
A(Spacer(1, 5))

A(band("BEFORE THE OPEN", MUTE)); A(Spacer(1, 3))
A(choice("Trend (D / 4H)", ["up", "/", "down", "/", "flat"]))
A(choice("Market state", ["balanced  (fade the edges)", "/", "imbalanced  (continuation)"]))
A(choice("Yesterday's zones", ["demand held", "/", "demand failed", "/",
                               "supply held", "/", "supply failed"]))
A(field("News (ForexFactory)"))
A(P("13:30 UK is an hour before the open. 15:00 UK lands inside your session.", "tiny"))
A(Spacer(1, 2))
A(pair("Key level", "to"))
A(Spacer(1, 2))
A(pair("1 &nbsp; LONG if above", "target"))
A(pair("2 &nbsp; SHORT if loses", "target"))
A(P("At least 2:1 on each, measured from the entry you would actually get.", "tiny"))
A(Spacer(1, 6))

A(band("AFTER THE CLOSE", BLUE)); A(Spacer(1, 3))
A(choice("Reached my level?", ["YES", "/", "NO"]))
A(choice("The level", ["held", "/", "broke", "/", "neither"]))
A(choice("Scenario triggered", ["1", "/", "2", "/", "neither"]))
A(choice("Traded?", ["YES", "/", "NO"]))
A(field("Strategy"))
A(choice("Plan followed?", ["YES", "/", "NO"]))
A(P("If NO, ring one:", "lab"))
A(P("&nbsp;&nbsp;chased after missing entry &nbsp;&#183;&nbsp; traded mid-range &nbsp;&#183;&nbsp; "
    "was first buyer / seller &nbsp;&#183;&nbsp; bought the breakout<br/>"
    "&nbsp;&nbsp;took it without confirmation &nbsp;&#183;&nbsp; sized wrong &nbsp;&#183;&nbsp; other",
    "opt"))
A(Spacer(1, 3))
A(field("MAX R", 46*mm))
A(field("Notes", 20*mm, 7.8*mm, n=4))
A(field("Visual evidence", 32*mm))
A(Spacer(1, 5))

A(band("THE NEVERS", RED)); A(Spacer(1, 3))
A(P("Never trade the middle of a range &nbsp;&#183;&nbsp; never be the first buyer or seller "
    "&nbsp;&#183;&nbsp; never buy the breakout<br/>"
    "Never long above the high of day, or short below the low of day &nbsp;&#183;&nbsp; "
    "miss the entry? do NOT reverse on it<br/>"
    "A missed move is information, not a loss &nbsp;&#183;&nbsp; skipping the day is a valid "
    "outcome", "opt"))

bad = set()
for f in F:
    if isinstance(f, Paragraph):
        for ch in f.text:
            try: ch.encode("cp1252")
            except UnicodeEncodeError: bad.add(ch)
if bad: raise SystemExit("non-WinAnsi: %r" % sorted(bad))

doc = SimpleDocTemplate(OUT, pagesize=A4, leftMargin=18*mm, rightMargin=18*mm,
                        topMargin=14*mm, bottomMargin=12*mm,
                        title="ES Daily Plan and Review", author="Carmine-SD syllabus")
doc.build(F)
print("wrote", OUT, os.path.getsize(OUT), "bytes")
