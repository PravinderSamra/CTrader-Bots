# -*- coding: utf-8 -*-
"""Module 4 reference PDF: the complete method, and risk.

Sources: transcripts 13-16. Three date from 2025-2026 (the masterclass, the
$30k-mistake video and the January drawdown video); 14-day-trading-strategy is
from 2022 and is marked where used.
"""
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Image, KeepTogether)

HERE = os.path.dirname(os.path.abspath(__file__))
DIA  = os.path.join(HERE, "03-diagrams")
OUT  = os.path.join(HERE, "02-documentation", "Carmine-SD-Module4.pdf")

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

F = []; A = F.append

A(P("Supply &amp; Demand - Module 4", "h1"))
A(P("The complete method, and risk.<br/>"
    "Method of Carmine Rosato. Compiled 19 November 2026.", "sub"))

A(P("How to read this", "h2"))
A(P("<b>HIS RULE</b> means he states it outright. <b>HIS WORDS</b> is a direct quote, "
    "lightly punctuated. <b>NOT STATED</b> flags something the method needs that he does "
    "not specify."))
A(P("<b>WHEN THIS WAS RECORDED.</b> Three of these four videos are <b>2025-2026</b> - a "
    "70-minute masterclass, a video about a month that cost him $30,000 in mistakes, and "
    "one recorded while climbing out of a $50,000 drawdown. The fourth is from <b>2022</b> "
    "and is marked wherever it is used.", "gap"))

A(P("1. The whole method, in order", "h2"))
A(P("Nothing in this section is new. It is Modules 1 to 3 arranged in the sequence he "
    "actually runs them, which is the thing none of the individual videos states outright."))
A(KeepTogether([img("m4-01-the-stack.png", 168*mm)]))
A(P("Two things are worth noticing about the shape of it. The first four steps are all "
    "<b>permission to trade</b>, not reasons to trade - any one of them failing ends the "
    "day's involvement. The second is that steps 1, 2 and 8 happen when the market is shut."))

A(P("2. Balanced market rules", "h2"))
A(P("He names this as the framework responsible for most of a $68,000 month, and it is the "
    "one most traders actively avoid:"))
A(P("\"a lot of traders see the market just moving like this and they're like, man, I'm "
    "done, I'm calling it a day, <b>I hate trading the market when it's choppy</b>. I love "
    "it. <b>I find my best setups come when it's like this.</b>\"", "quote"))
A(KeepTogether([img("m4-02-balance-rules.png", 168*mm)]))
A(P("<b>HIS RULE, two parts.</b> First: \"<b>trading in the middle of this range, no "
    "good</b>\" - he admits breaking this himself the week before and paying for it. "
    "Second: \"my rule of thumb is to <b>trade around the edges</b>. It is what I call "
    "<b>fade the extremes</b>.\" So when the market is balanced he is <b>first and only "
    "looking to play reversals</b>."))
A(P("And the diagnosis, which is the useful part:"))
A(P("\"<b>you get chopped because most likely you're either (a) trading in the middle, or "
    "(b) longing a breakout or selling a low when it should be the opposite</b>\"", "quote"))

A(P("3. Initiative - and why he never buys the break", "h2"))
A(P("A balance range cannot last. When it ends, somebody is <b>initiating</b> outside it, "
    "and that is where the word comes from. But he does not join at the break:"))
A(P("\"I very, very rarely - <b>95% of the time</b> - do I not play breakouts... I do not "
    "like buying or selling an <b>extended move</b>, because it does not offer a great "
    "risk-to-reward ratio.\"", "quote"))
A(KeepTogether([img("m4-03-initiative.png", 168*mm)]))
A(P("<b>HIS RULE.</b> Let it break. Watch where the aggressive buyers showed up on the "
    "break. <b>Mark that as a new level.</b> Then buy the pullback into it. Which produces "
    "the single best sentence in the whole corpus for understanding how he thinks:"))
A(P("\"even if I am playing a continuation setup, <b>I will not buy the market on a "
    "continuation. I will buy the market on a reversal.</b> ... So my entry is a reversal "
    "signal, but I'm going for a continuation setup.\"", "quote"))
A(P("That resolves what looks like a contradiction across the whole syllabus. He is always "
    "a reversal trader at the moment of entry. Whether the <i>trade</i> is a reversal or a "
    "continuation is a separate question about where the target is.", "cap"))

A(P("4. Never the first buyer, never the first seller", "h2"))
A(P("The same idea appears in three separate videos under two names, and it is one of the "
    "most portable rules he has:"))
A(P("\"I was being what I call <b>the first buyer</b> in downtrending markets. Being a "
    "first buyer is not ideal. What I did in this case was <b>I waited for the buyers to "
    "prove they are in the market</b>.\"", "quote"))
A(P("\"there's no reason to play it short on the first downside move - <b>I call it a first "
    "seller</b>. Wait for sellers to come into the market and then you could play a "
    "retest.\"", "quote"))
A(P("\"I <b>don't initiate a trade on the first test</b> of the high or the low of a "
    "balance range\"", "quote"))
A(P("<b>HIS RULE.</b> The first touch is for watching. You trade the second one, once the "
    "side you want has shown itself."))

A(P("5. Order flow belongs only at your levels", "h2"))
A(P("Asked directly how to cope with a screen covered in bubbles and lines, his answer is a "
    "scoping rule rather than a technique:"))
A(P("\"I <b>only</b> like using everything I explained in this masterclass <b>at my levels "
    "of interest</b>. It's a lot of noise at random points in the market. So I only use "
    "order flow when it is at my key levels, or if the market has rejected off of my key "
    "level.\"", "quote"))
A(P("Same for single big orders: \"if an iceberg shows up at one specified price and "
    "<b>it's not at a level of interest, I do not look at it. I think it's noise</b>.\""))

A(P("6. What counts as \"large\" - the gap Module 3 could not fill", "h2"))
A(P("Module 3 recorded that he never gives a threshold for a delta outlier. In the "
    "masterclass Q&amp;A he answers it, and the answer is that there is no fixed number by "
    "design:"))
A(P("\"<b>Some days 100 is large size, some days 1000 is large size.</b> How do you know "
    "what is large size? By looking at just <b>outliers in the data</b>. If every order "
    "coming in today is 100 contracts, then something that comes in with 1000 contracts is "
    "an outlier. If every order coming in today is 1000 contracts, then 1000 is not an "
    "outlier that day - but maybe 3000 is. <b>Just look for difference in the data.</b>\"",
    "quote"))
A(P("<b>HIS RULE.</b> It is relative to the session you are in, recalibrated daily by eye. "
    "Module 3's gap note on this should now be read as answered."))

A(P("7. P-shapes and B-shapes - he does use them", "h2"))
A(P("Module 1 originally claimed he never uses volume-profile shape vocabulary. That was "
    "corrected to \"not in those four videos\" once it was pointed out that he teaches it "
    "elsewhere. The masterclass Q&amp;A settles it outright:"))
A(P("\"when looking at a delta footprint chart, am I looking for big orders or P-shape, "
    "B-shape? <b>Both. Looking for delta outliers and P-shapes, B-shapes.</b>\"", "quote"))
A(P("So both tools run side by side. The shapes themselves are still not taught in any of "
    "the sixteen videos - only named - so that remains open.", "gap"))

A(P("8. The settings he actually uses", "h2"))
A(P("Scattered through the Q&amp;A, and worth having in one place:"))
A(P("<b>Footprint:</b> a <b>20-tick range</b> chart on the S&amp;P, <b>not time-based</b>. "
    "Template is \"middle column is total volume, left column is delta, right column is a "
    "volume profile shaded for the significance of the delta side.\"<br/>"
    "<b>Heat map:</b> no time basis at all - \"it's just static as volume's coming in.\" No "
    "add-ons: \"market pulse, stop losses, I do not.\"<br/>"
    "<b>Candlestick timeframes</b>, used only for supply and demand zones: \"weekly, daily, "
    "4 hour, 3 hour, 2 hour, 1 hour, 90 minute, 30 minute and 15 minute. <b>That is the "
    "only time that I will use a timeframe chart.</b>\"<br/>"
    "<b>Gamma:</b> \"do I use gamma? I do not.\"<br/>"
    "<b>Zone lifecycle:</b> \"my levels come from price action that formed today, last week, "
    "last month. Whenever they form, I draw them until whenever they become invalidated, I "
    "remove them.\""))
A(P("On spoofing, which he refuses to worry about: \"I don't pay much attention to any "
    "resting orders that <b>show zero intention to fill</b>... whether you want to call it "
    "spoofing or pulling, I don't give a crap, because <b>that order was never filled</b>.\""))

A(P("9. Risk - the arithmetic that permits being wrong", "h2"))
A(KeepTogether([img("m4-05-win-rate.png", 168*mm)]))
A(P("\"the way I look at the market is that I need to put myself in the position to <b>lose "
    "as much as possible in terms of quantity of losses, but lose the least amount of money "
    "possible</b> in those losses\"", "quote"))
A(P("His own reported months: June, <b>$68,000</b> with a 4.17 average win-to-loss. "
    "January, after the drawdown, <b>a 20% win rate with a 5:1 average</b> - and a record "
    "three days. February, <b>+$30,000 while being wrong roughly 75% of the time</b>."))
A(P("And then, unusually for a trading video, the cost of that:"))
A(P("\"imagine being right 20, 30% of the time and you're wrong 70% of the time. <b>That's "
    "going to mess you up mentally despite you making money.</b> Despite me being green... "
    "me being wrong 75% of the time absolutely is damaging despite my account growing at "
    "the end of the month.\"", "quote"))
A(P("Worth sitting with before adopting a high-R system. The arithmetic works; the "
    "experience of it is a separate problem, and he is telling you it did not get easier "
    "after ten years.", "cap"))

A(P("10. The stop", "h2"))
A(P("One sentence, and it is the whole rule: \"my stop loss is <b>always based on where my "
    "analysis is incorrect</b>.\""))
A(P("Which is why his stops are small - not because small stops are the goal. \"I have a "
    "one-point stop loss <b>because I'm trading at an area, I'm trading when the context "
    "makes sense, and I'm trading when I have great confirmation</b>.\""))

A(P("11. Drawdown - the two causes, and the way out", "h2"))
A(P("Recorded while recovering from being <b>0 for 13</b> and nearly <b>$50,000</b> down in "
    "two weeks. He names two causes and only two:"))
A(P("\"number one, it's simply <b>failing to adapt to different market conditions</b>... "
    "and if it's not that, then it's simply <b>a mental barrier</b> or something going on "
    "with our emotions\"", "quote"))
A(P("His own case was the first: \"<b>I am doing the things I would do in an uptrend market "
    "in a market that is currently downtrending.</b>\" His \"line of least resistance\" "
    "setups - if X breaks there is nothing stopping it reaching Y - had simply stopped "
    "appearing, and he kept planning around them."))
A(P("<b>The recovery process, as he describes doing it:</b> acknowledge and accept the "
    "drawdown; dissect the trading data and the journal; look for <b>common similarities</b> "
    "across the losers; then - the step most people skip - <b>reverse-engineer the trades he "
    "did not take</b>: \"how could I have traded this? If I was an active participant, how "
    "could I have made money off this setup?\""))
A(P("And out of it came the closest thing in sixteen videos to a mechanical trend rule:"))
A(P("\"I've got to go in with a <b>downtrending perspective until</b> the market starts "
    "putting in <b>higher lows</b>, bounces off demand, or finds <b>acceptance to the "
    "upside</b> - that's when I'll switch. Until then I will continue in the downtrending "
    "rules.\"", "quote"))

A(P("12. The chain that cost him $30,000", "h2"))
A(P("Four losing days in one February: $9,500, $4,800, $7,700, $8,500. All four share one "
    "pattern, and it is not an analysis failure."))
A(KeepTogether([img("m4-04-the-chain.png", 168*mm)]))
A(P("\"February 3rd, perfect downtrend. That was part of my plan, but I missed the entry "
    "and <b>I took five longs instead</b>. February 26th, I wrote a bearish bias. Market "
    "sold off exactly to my plan. Guess what? I missed the short entry and <b>I took four "
    "longs in the downtrend</b>.\"", "quote"))
A(P("\"<b>This isn't an analysis problem. The analysis was right.</b> This is a "
    "psychological problem that I couldn't sit on my hands after missing an entry.\"",
    "quote"))
A(P("The line that names the whole failure mode:"))
A(P("\"<b>our job is to locate trading opportunities, not create them.</b> And I'm not "
    "locating them, I'm trying to create them... when we create these false ideas in our "
    "head, <b>our eyes see what we want to see</b>.\"", "quote"))
A(P("<b>His fix, stated as a rule:</b> \"<b>if I miss my planned entry, I do not create a "
    "new trade in the opposite direction.</b> I'll either wait for new development to form "
    "that I could create a new thesis off of, or I sit on my hands.\""))
A(P("Note also what he says about awareness, because it is the uncomfortable part: \"<b>the "
    "problem isn't awareness. I'm aware of my mistakes.</b> ... the gap is between knowing "
    "and doing.\"", "cap"))

A(P("13. Missing a move - the same event, handled two ways", "h2"))
A(P("Put the masterclass next to the $30,000 video and you get both halves of one lesson. "
    "Same situation: a level he planned for, rejected, without him on board."))
A(P("<b>The wrong response</b> is section 12 above. <b>The right one:</b>"))
A(P("\"despite me not participating, because I didn't see a good confirmation at the supply "
    "zone, <b>the rejection of the supply zone provides context</b>... Don't look at you "
    "missing a move as you missing a move. Look at it as: <b>it's providing information to "
    "me that I could use to my advantage</b> in the near future... I formulated a new plan "
    "off of it.\"", "quote"))
A(P("He then traded the <i>second</i> opportunity the same level created, for $14,000 in "
    "five minutes. The difference is not discipline in the abstract - it is whether the new "
    "trade came from the market or from the regret."))

A(P("14. What a mistrade actually is", "h2"))
A(P("A definition worth adopting, because it changes what you are allowed to feel bad about:"))
A(P("\"<b>a mistrade is not the market moving in a direction and you not participating.</b> "
    "If you didn't have a plan, you didn't miss the move - you did not participate in it. "
    "[A mistrade is] you have a plan for it, you have great confirmation, everything's "
    "aligning, <b>and you don't take it</b> because you're fearful of accepting the risk.\"",
    "quote"))

A(P("15. Stopping rules", "h2"))
A(P("Two appear, both lightly:"))
A(P("<b>The three-loss rule.</b> Mentioned as something he has and did not follow: \"there's "
    "rules to implement, like <b>the three loss rule</b> - which is another problem in "
    "itself that I didn't implement or follow.\" He never states it in full.", "gap"))
A(P("<b>One and done.</b> Described approvingly twice during the January recovery: \"this is "
    "the second trading day so far this week where it's <b>one and done - one setup, one "
    "win, call it a day and walk away</b>.\""))
A(P("And the blunt version: \"<b>do I skip days because I don't see a setup? 100%. "
    "100%.</b>\""))

A(P("16. Still missing after sixteen videos", "h2"))
A(P("<b>Position sizing.</b> Still the largest hole. He gives dollar risk per trade but "
    "never how it is set. He does say where it came from: \"<b>I learned my risk management "
    "through Dylan</b>... I attribute a lot of my success and my consistency to Dylan and "
    "his risk management system that he has taught me, <b>with position sizing</b>\" - a "
    "friend who works on Wall Street, whose lessons sit in the paid accelerator.", "gap"))
A(P("<b>Key zones.</b> Sixteen videos, still withheld. In 2022: \"I have a set of rules to "
    "know where to draw the zones... and within that set of rules I have a <b>subset of "
    "rules</b> that I use to make sure I'm trading high quality setups.\" Never given.",
    "gap"))
A(P("<b>The three-loss rule</b> in full, and how P-shapes and B-shapes are actually read.",
    "gap"))
A(P("<b>A fully mechanical trend definition.</b> Closer now - higher lows, a bounce off "
    "demand, or acceptance higher - but still eyeballed.", "gap"))

A(P("17. What he would say about all of this", "h2"))
A(P("From the 2022 video, and it is the right note to end a syllabus on:"))
A(P("\"<b>there is no right way to trade.</b> Somebody trading one way could make seven "
    "figures a year; someone trading a completely different way can make seven figures a "
    "year... what matters is you find a system that's going to give you a <b>positive "
    "expectancy over the long run</b>, something sustainable that you could do day after "
    "day, while <b>keeping your loser small so you live to fight another day</b>.\"", "quote"))
A(P("\"think of every trader as a <b>fingerprint</b>... we could be the same technically and "
    "take the same setups, but we are unique traders that are not identical.\"", "quote"))
A(P("And on how to actually learn it: \"if you are a beginner I recommend <b>sticking to one "
    "strategy, one style, and mastering it</b>. Don't try to become an all-around player... "
    "it's better to know one thing very well than to know five different things not very "
    "well.\""))
A(P("\"<b>stop trying to be perfect.</b> We don't have to be perfect to make money. We just "
    "have to come out at the end of the day, the week, the month following our plan, "
    "managing our risk.\"", "quote"))

A(P("Sources: 13-masterclass-reading-behind-price, 15-the-30k-mistake, 16-january-reset "
    "(2025-2026) and 14-day-trading-strategy (2022). This completes the four-module "
    "syllabus. Nothing in any of it has been tested - it is a record of what he teaches, "
    "not a claim that it works. The testing is a separate job, and worth doing before any "
    "of it is traded with real size.", "cap"))

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
    canvas.saveState(); canvas.setFont("Helvetica", 8); canvas.setFillColor(MUTE)
    canvas.drawString(21*mm, 10*mm, "Supply & Demand - Module 4: The Complete Method, and Risk")
    canvas.drawRightString(A4[0]-21*mm, 10*mm, "page %d" % doc.page)
    canvas.restoreState()

doc = SimpleDocTemplate(OUT, pagesize=A4, leftMargin=21*mm, rightMargin=21*mm,
                        topMargin=18*mm, bottomMargin=16*mm,
                        title="Carmine Rosato Supply & Demand - Module 4",
                        author="Carmine-SD syllabus")
doc.build(F, onFirstPage=footer, onLaterPages=footer)
print("wrote", OUT, os.path.getsize(OUT), "bytes")
