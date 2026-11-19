# -*- coding: utf-8 -*-
"""Module 3 reference PDF: the trigger - order flow.

Sources: transcripts 09-12 in 01-transcripts, recorded 2024-2026 (dated from the
index levels quoted on screen). This is his current method.

Tags: HIS RULE (stated in a transcript), HIS WORDS (quoted), NOT STATED (not
specified in these videos). ReportLab's built-in fonts are WinAnsi, so the build
asserts every character is cp1252-encodable.
"""
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Image,
                                KeepTogether, Table, TableStyle)

HERE = os.path.dirname(os.path.abspath(__file__))
DIA  = os.path.join(HERE, "03-diagrams")
OUT  = os.path.join(HERE, "02-documentation", "Carmine-SD-Module3.pdf")

INK, MUTE = colors.HexColor("#1b1b1b"), colors.HexColor("#6b6b6b")
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
                           leftIndent=10, spaceBefore=3, spaceAfter=7)
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

A(P("Supply &amp; Demand - Module 3", "h1"))
A(P("The trigger: what actually makes him click the button.<br/>"
    "Method of Carmine Rosato. Compiled 19 November 2026.", "sub"))

A(P("How to read this", "h2"))
A(P("<b>HIS RULE</b> means he states it outright. <b>HIS WORDS</b> is a direct quote, "
    "lightly punctuated. <b>NOT STATED</b> flags something the method needs that he does "
    "not specify in these videos."))
A(P("<b>WHEN THIS WAS RECORDED.</b> The four videos behind this module date from "
    "<b>2024 to 2026</b>, from the index levels quoted on screen - ES at 5047, then 6595, "
    "then 6838, then 7360-7593. <b>This is his current method.</b> Where it conflicts with "
    "Modules 1 and 2, which rest on 2022-23 material, this module wins.", "gap"))

A(P("1. What order flow is actually for", "h2"))
A(P("He is explicit that this is not a different strategy. It is a layer you add to the one "
    "you already have:"))
A(P("\"Order flow trading will <b>level up any trading strategy that you use</b>. If you use "
    "ICT, trend lines, break and retest, Fibonacci, simple price and volume analysis - if "
    "you implement order flow it will level up all of these tremendously... <b>This is not "
    "changing anything. This is just adding</b> something that gives you more insights "
    "about what is driving price.\"", "quote"))
A(P("So nothing in Modules 1 and 2 is thrown away. Zones still decide <i>where</i>. This "
    "module decides <i>whether</i>, and above all <i>when</i>."))

A(P("2. The CLC rule - his own framework", "h2"))
A(P("\"these three pillars are crucial for me - <b>when all three align I know I'm going to "
    "have an A+ high-quality setup</b> - and I call these three pillars the <b>CLC "
    "rule</b>\"", "quote"))
A(KeepTogether([img("m3-01-clc-rule.png", 168*mm)]))
A(P("The sentence that makes the whole syllabus make sense:"))
A(P("\"<b>context and location</b> of the CLC rule, most of the time, not always, <b>comes "
    "from a candlestick chart</b>... in terms of <b>confirmation, I use the volume</b>\"",
    "quote"))
A(P("That is why this material splits the way it does. Module 2 is the C, Module 1 is the L, "
    "and this module is the final C. None of them is a strategy on its own."))

A(P("3. What actually moves price", "h2"))
A(P("Everything downstream rests on one mechanical claim:"))
A(P("\"the market moves up simply because there is <b>more aggressive buying than there is "
    "passive selling</b> - that's the only way the market could move up\"", "quote"))
A(KeepTogether([img("m3-02-what-moves-price.png", 168*mm)]))
A(P("Aggressive orders are market orders - they cross the spread and take. Passive orders "
    "are limit orders - they sit and get taken. A level only holds because of what is "
    "<i>resting</i> there:"))
A(P("\"<b>what proves resistance to be resistance is strong passive sellers</b> providing a "
    "ceiling to price... if the passive sellers have more quantity of sell orders than the "
    "aggressive buyers, then the market's only option is to start moving down\"", "quote"))
A(P("Which leads to the line worth pinning above the screen:"))
A(P("\"<b>candles form because of the volume. The volume doesn't form because of the "
    "candles. Do not get that twisted.</b> A candlestick chart does not tell me when to "
    "enter or exit - the tape does, the volume does, the order flow does.\"", "quote"))

A(P("4. The one signal, in both directions", "h2"))
A(P("Almost every entry in these four videos is the same observation: <b>the heaviest "
    "aggression of the session arrives, and price does not move</b>. That means the other "
    "side is sitting there passively, absorbing it."))
A(KeepTogether([img("m3-03-effort-no-reward.png", 168*mm)]))
A(P("<b>At a low</b> (his $21,000 trade): \"that negative delta of -254 has just turned into "
    "<b>-1100</b>, which means over 900 more aggressive sell contracts came in at that price "
    "in a <b>five-second period - yet the market did not move down. In fact the market "
    "moved up.</b> I view all of this selling as a potential buyer who is passively buying "
    "the market.\"", "quote"))
A(P("<b>At a high</b> (his $23,000 trade): the delta at the high builds +1024, then +1921, "
    "then +3300 as price keeps failing to take out the high. \"<b>the seller is still "
    "sitting there with his red line</b>... it's almost like a wall or a ceiling to price. "
    "When I see this, I'm short.\"", "quote"))
A(P("And stated as a general rule in the newest video: \"if the selling is the strongest "
    "that we've seen so far in the most recent range and <b>the market cannot continue to "
    "sell off, this is a very good indication that a buyer is present</b>.\""))
A(P("This is Module 1's absorption, made operational. Module 1 could tell you it had "
    "happened; this tells you the moment it is happening.", "cap"))

A(P("5. The delta outlier - and where tomorrow's level comes from", "h2"))
A(P("Module 2 listed three sources for a key level and could not do better. Here is the "
    "fourth, and it is order-flow native:"))
A(P("\"we see <b>850 contracts hit the bid</b>... which indicates aggressive selling hitting "
    "a passive buyer. And the reaction after this is the market begins to rally. So this to "
    "me sounds like <b>a passive buyer sitting at 6575</b>... <b>We call this a delta "
    "outlier.</b>\"", "quote"))
A(KeepTogether([img("m3-04-delta-outlier.png", 168*mm)]))
A(P("The part that turns a print into a level is that <b>it repeats at the same price on a "
    "different day</b>: \"keep in mind this is at 6575, <b>the same exact level where we're "
    "seeing it the following day</b>.\" That is what put 6575 in the next session's plan."))
A(P("<b>HIS RULE, and it is counter-intuitive.</b> He wants the level to break:"))
A(P("\"I wanted this level to <b>break, attract sellers</b>... For traders who have a large "
    "need to facilitate a long position, <b>they need others to sell</b>. As long as it "
    "doesn't move too far down, this could be a good indication that a passive buyer is "
    "present and <b>someone is loading the boat</b>.\"", "quote"))
A(P("Note the plan was \"<b>break under 6575 but not below 6565</b>\" - a band of tolerance, "
    "not a line. Below 6565 the thesis is simply wrong, which is also where the stop went."))

A(P("6. The trapped-participant playbook", "h2"))
A(P("His named three-step sequence, and the one he calls a favourite:"))
A(KeepTogether([img("m3-05-playbook.png", 168*mm)]))
A(P("<b>Step 1 - find strong volume in one direction.</b> Usually aggressive buying as "
    "price breaks a high, or aggressive selling as it breaks a low. Somebody has just "
    "committed."))
A(P("<b>Step 2 - wait for the opposite side to take control.</b> \"the market tried to lift "
    "up... now all of a sudden sellers are now trying to take control and <b>put brakes to "
    "this rally</b>.\""))
A(P("<b>Step 3 - find the pain point, and make it the target.</b> \"If I am a buyer above "
    "this high, <b>where am I going to place my stop loss?</b> ... these are points where "
    "the market would then likely gravitate towards.\""))
A(P("The mechanism underneath it, which is what makes the move self-feeding:"))
A(P("\"for them to stop out, <b>they're going to have to sell to exit for a loss</b> - which "
    "would then also help validate a bit more of a downside continuation\"", "quote"))

A(P("7. \"The now\" - the only timeframe he confirms on", "h2"))
A(P("\"people always hear me refer to <b>the now</b>... this is the time frame that I use. "
    "I am reading the orders coming in <b>right now, in the present moment</b>, because "
    "right now the market provides all the information that I need to click the buy or sell "
    "button. <b>And if it doesn't provide me enough information, then that is information "
    "in itself</b> for me to avoid a trade.\"", "quote"))
A(P("The argument against waiting for a candle to close is worth reading twice:"))
A(P("\"<b>what does time have to do with validating your trading thesis? Time does not move "
    "the market - volume and price does.</b> What if a candle closes right at the level but "
    "the volume is still rejecting?\"", "quote"))

A(P("8. The entry decides the risk-to-reward", "h2"))
A(P("This is the most practical idea in the module, and he demonstrates it twice with real "
    "numbers. Same stop. Same target. Only the entry moves."))
A(KeepTogether([img("m3-06-entry-decides-r.png", 168*mm)]))
A(P("\"our stop loss is the same, our target is the same\" - entering when the order flow "
    "printed gave <b>5:1</b>; a few seconds later <b>2:1</b>; waiting for a candle to close "
    "<b>1.44:1</b>."))
A(P("His second example runs the same way: long at 5746 after a trend-line break, with the "
    "stop necessarily at the low of day, is a 7-point risk for a 7-point reward - <b>1:1</b>. "
    "Long at 5740 when the delta printed is a 2-point risk for 12 points - <b>6:1</b>."))
A(P("\"when you wait for a time-based chart to tell you when to enter, you are going to "
    "<b>maximize your risk and minimize your reward</b>, which is not good in trading\"",
    "quote"))
A(P("The implication is uncomfortable and worth sitting with: a setup you judged correctly "
    "can still be a bad trade, purely because of when you got in.", "cap"))

A(P("9. Where the stop goes", "h2"))
A(P("He gets asked constantly about his one-point stops, and the answer is not what people "
    "expect:"))
A(P("\"I have a one-point stop loss <b>because I'm trading at an area, I'm trading when the "
    "context makes sense, and I'm trading when I have great confirmation</b>. It's <b>not</b> "
    "because I have a one-point stop loss just to make my losses smaller.\"", "quote"))
A(P("<b>HIS RULE.</b> The stop goes where the thesis dies, not at a distance you chose. If "
    "the read is \"a large passive buyer is here\", the stop sits <b>under that large "
    "volume</b>. If it is \"a seller is capping this high\", the stop sits a point above the "
    "high. The tightness is a <i>consequence</i> of entering at the evidence."))

A(P("10. Targets and exits", "h2"))
A(P("\"majority of my exits come from <b>higher days, lower days, VWAP, the next supply or "
    "demand zone, or the next support resistance</b>\"", "quote"))
A(P("\"<b>I'm not going for home runs.</b> I'm simply targeting lower days, pre-market lows, "
    "support, demand, resistance, supply - I'm getting the confirmation, hitting my target, "
    "and I'm walking away.\"", "quote"))
A(P("He scales out: in the worked long, first target was the high of day, second the "
    "pre-market high. Typical size is \"10, 15, 20 point rewards because my risk is 1, 2, 3, "
    "4 points.\""))

A(P("11. The arithmetic that makes it work", "h2"))
A(P("\"let's say we have a <b>3:1</b>... we can have a <b>30% win rate</b> yet still come "
    "out profitable. If we flip that to <b>1:1</b>, we need a <b>60% win rate</b>. Or a "
    "<b>5:1</b> - we can theoretically have a <b>20% win rate</b> and still come out "
    "profitable.\"", "quote"))
A(P("\"the way I look at the market is that I need to put myself in the position to <b>lose "
    "as much as possible in terms of quantity of losses, but lose the least amount of money "
    "possible</b> in those losses\"", "quote"))
A(P("Which is the real reason the entry matters. The R multiple is not vanity - it is what "
    "buys permission to be wrong most of the time."))

A(P("12. Cumulative delta divergence", "h2"))
A(P("One specific named pattern worth knowing on its own:"))
A(P("\"the market basically puts in this <b>double top</b>, yet the <b>cumulative delta puts "
    "in a higher high</b> and is significantly higher than it was above this previous high - "
    "indicating that potentially <b>buyers are going to become trapped</b> here\"", "quote"))
A(KeepTogether([img("m3-07-cd-divergence.png", 168*mm)]))
A(P("Price made no progress while the aggression grew. Everyone who bought the second attempt "
    "is offside at the same price."))

A(P("13. Never long above a high, never short below a low", "h2"))
A(P("\"never long above a high, or never short below a low... <b>we broke the high of day - "
    "perfect trap for retail</b>\"", "quote"))
A(P("<b>HIS RULE.</b> The break of an obvious extreme is where he looks to fade, never to "
    "join. This is Module 1's \"fading the obvious\" with a specific trigger attached."))

A(P("14. The tools he actually uses", "h2"))
A(P("\"<b>footprint charts, a heat map, a depth of market</b> - any tool which enables me to "
    "read the volume and the order flow properly will let me see what's going on behind the "
    "candlestick charts\"", "quote"))
A(P("Across the four videos he reads: the <b>footprint</b> (delta per price per bar), the "
    "<b>heat map</b> for resting liquidity - the orange and red lines he calls walls - "
    "<b>cumulative delta</b>, the <b>depth of market</b> and current order book, and "
    "<b>time and sales</b> with its aggressive-trade bubbles."))
A(P("<b>ANSWERED IN MODULE 4.</b> There is no fixed threshold for a delta outlier, by "
    "design: \"some days 100 is large size, some days 1000 is large size... if every "
    "order coming in today is 100 contracts, then something that comes in with 1000 is "
    "an outlier. <b>Just look for difference in the data.</b>\" It is recalibrated "
    "against the session you are in.", "gap"))

A(P("15. What this supersedes in Module 1", "h2"))
A(P("Module 1 section 6, <i>What counts as confirmation</i>, was built on the 2022-23 videos, "
    "where his answer was a list: \"chart patterns, candle patterns, a new supply or demand "
    "zone forming, something on the level two or time and sales, some type of flag pattern, "
    "a wedge break, some type of market structure breaking.\""))
A(P("By 2026 that list is explicitly demoted. Confirmation is order flow, and a candlestick "
    "pattern is never the reason. <b>Read Module 1 section 6 as history and this module as "
    "the live rule.</b>"))

A(P("16. Still missing", "h2"))
A(P("<b>Position sizing.</b> He gives dollar risk per trade ($1,500, $2,200, $2,500, $3,000) "
    "but never how it is set, or how it relates to account size.", "gap"))
A(P("<b>What makes a delta print an outlier.</b> Relative and eyeballed; no number.", "gap"))
A(P("<b>Key zones.</b> Still withheld to the paid course, across all twelve videos so far.",
    "gap"))
A(P("<b>A mechanical trend definition.</b> Still absent, three modules in.", "gap"))

A(P("A note on his own honesty about this, which is worth keeping in view: \"<b>do I know "
    "100% that they're here? No - but they could be here, for a high probability setup.</b> "
    "I don't want people getting in blindly... it's when everything is aligning.\" The CLC "
    "rule is a way of stacking evidence, not a way of knowing.", "cap"))

A(P("Sources: 09-orderflow-playbook, 10-better-entries, 11-orderflow-confirmation, "
    "12-orderflow-levels-up, recorded 2024-2026. Module 4 is the complete method and risk. "
    "Nothing in this document has been tested - it is a record of what he teaches, not a "
    "claim that it works.", "cap"))

def walk(fl):
    for f in fl:
        if isinstance(f, Paragraph): yield f.text
        elif isinstance(f, KeepTogether):
            for s in walk(f._content): yield s
bad = set()
for s in walk(F):
    for ch in s:
        try: ch.encode("cp1252")
        except UnicodeEncodeError: bad.add(ch)
if bad:
    raise SystemExit("non-WinAnsi characters present: %r" % sorted(bad))

def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(MUTE)
    canvas.drawString(21*mm, 10*mm, "Supply & Demand - Module 3: The Trigger")
    canvas.drawRightString(A4[0]-21*mm, 10*mm, "page %d" % doc.page)
    canvas.restoreState()

doc = SimpleDocTemplate(OUT, pagesize=A4,
                        leftMargin=21*mm, rightMargin=21*mm,
                        topMargin=18*mm, bottomMargin=16*mm,
                        title="Carmine Rosato Supply & Demand - Module 3",
                        author="Carmine-SD syllabus")
doc.build(F, onFirstPage=footer, onLaterPages=footer)
print("wrote", OUT, os.path.getsize(OUT), "bytes")
