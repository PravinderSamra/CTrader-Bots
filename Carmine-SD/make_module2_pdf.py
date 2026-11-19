# -*- coding: utf-8 -*-
"""Module 2 reference PDF: context - reading the day before you trade it.

Sources: the four module-2 transcripts (05-08 in 01-transcripts), plus the
context material carried over from the four module-1 videos.

Tags: HIS RULE (stated in a transcript), HIS WORDS (quoted), NOT STATED (not
specified in these videos), NOT IN THESE VIDEOS (he teaches it elsewhere).
ReportLab's built-in fonts are WinAnsi, so the build asserts every character is
cp1252-encodable.
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
OUT  = os.path.join(HERE, "02-documentation", "Carmine-SD-Module2.pdf")

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
S["key"]  = ParagraphStyle("key", fontName="Helvetica-Bold", fontSize=10.4,
                           leading=15, textColor=BLUE, spaceBefore=4, spaceAfter=8)

def P(t, s="body"): return Paragraph(t, S[s])
def img(name, w=168*mm):
    p = os.path.join(DIA, name)
    from PIL import Image as PILImage
    iw, ih = PILImage.open(p).size
    return Image(p, width=w, height=w*ih/iw)

F = []
A = F.append

A(P("Supply &amp; Demand - Module 2", "h1"))
A(P("Context: reading the day before you trade it.<br/>"
    "Method of Carmine Rosato, reconstructed from four further videos. "
    "Compiled 19 November 2026.", "sub"))

A(P("How to read this", "h2"))
A(P("<b>HIS RULE</b> means he states it outright. <b>HIS WORDS</b> is a direct quote - "
    "lightly punctuated, since the source is auto-generated captions. <b>NOT STATED</b> "
    "flags something the method needs that he does not specify in these videos. "
    "<b>NOT IN THESE VIDEOS</b> flags something he does teach, but elsewhere. Both labels "
    "describe the limits of the source set, not the limits of his method."))
A(P("<b>WHEN THIS WAS RECORDED.</b> Every video behind Modules 1 and 2 dates from "
    "<b>2022 to early 2023</b>. That is established from the dates and index levels he "
    "quotes on screen: \"Friday October 7th\" with the S&amp;P at 3675 fixes one to October "
    "2022, \"Thursday April 27th\" with the S&amp;P at 4107 fixes another to April 2023, and "
    "every weekday he names matches the calendar for those years. Modules 3 and 4 draw on "
    "much newer material. Where they conflict with this module, read it as the method "
    "having moved on - not as him contradicting himself.", "gap"))
A(P("Module 1 was about the zone - what it is and how to draw it. This module is about "
    "everything you check <i>before</i> the zone matters, and it is where most of the "
    "decision actually gets made."))

A(P("1. Context is the master variable", "h2"))
A(P("\"<b>context is one of the most important things to me</b>, because it gives me the "
    "relationship between buyers and sellers. The way I look at it is <b>the market's a "
    "storyteller</b>, and we must get context clues of the story that the market is trying "
    "to tell us. It's never going to tell us the story directly, but it's going to leave "
    "us clues.\"", "quote"))
A(P("<b>HIS RULE.</b> Context is not background colour. It is the thing that decides "
    "whether a zone is worth trading at all, and it is read from what price actually did "
    "at zones recently - not from an indicator."))

A(P("2. The governing rule - same reaction, same result", "h2"))
A(P("If you take one sentence from this module, take this one:"))
A(P("\"<b>when there is a different reaction we're going to get a different result, but "
    "when there's the same reaction the odds are we're going to get the same result</b>\"",
    "quote"))
A(P("The practical form of it is that <b>yesterday's zone performance is today's "
    "starting assumption</b>:"))
A(P("\"remember what I mentioned about all those demand zones not being reliable on "
    "Thursday - <b>what makes you think they're going to be reliable</b> with the similar "
    "or the same action that we saw the day prior?\"", "quote"))
A(KeepTogether([img("m2-06-same-reaction.png", 168*mm)]))
A(P("<b>HIS RULE.</b> The bias is not \"demand zones work.\" It is \"demand zones have "
    "been failing, so demand zones fail until something changes.\" The burden of proof sits "
    "with the side that has not been working:"))
A(P("\"because of the action yesterday, <b>I'd rather be a little defensive and let buyers "
    "really prove themselves to me</b> for me to play on the same side and be a buyer\"",
    "quote"))
A(P("This is the most testable thing in the whole method. It is a claim about yesterday "
    "predicting today, and it can be measured.", "cap"))

A(P("3. Balance and imbalance - the regime switch", "h2"))
A(P("He splits markets into two states, and they call for opposite behaviour."))
A(P("\"the idea in <b>balanced</b> markets usually is to <b>buy the lows and sell the "
    "highs</b>, because the market is in balance - every move up would get sold into and "
    "every dip down would get bought into\"", "quote"))
A(P("\"when we get an <b>imbalanced</b> market, where one side is showing aggression... "
    "<b>that's when we're going to get continuation</b>, and that's when we're going to get "
    "the large rallies or the large sell-offs\"", "quote"))
A(P("<b>HIS RULE.</b> Balance means fade the edges. Imbalance means trade continuation. "
    "Running a reversal strategy into an imbalanced market is how the zones get run over."))
A(P("Separately, and not the same point, he will not trade the empty space between zones "
    "at all:"))
A(P("\"<b>I do not trade in these balance areas</b>... I only trade imbalance periods. I "
    "do not trade in the noise, in the blank spaces\"", "quote"))

A(P("4. The pre-market plan - two scenarios, not a prediction", "h2"))
A(P("This corrects the obvious assumption. He does not decide a direction before the open. "
    "He fixes <b>one level</b> and writes <b>both branches</b> off it."))
A(P("\"the pre-market plan for today was: <b>my key level was 4107 to 4110</b> on the S&amp;P "
    "500 futures... I post these every single day in the Discord - <b>levels and setups and "
    "scenarios</b> that I'm watching. <b>Scenario number one was a bullish setup</b>...\"",
    "quote"))
A(KeepTogether([img("m2-01-two-scenarios.png", 168*mm)]))
A(P("Each branch carries its own trigger and its own target, written in advance:"))
A(P("<b>Bullish:</b> \"if we can act support once we're above it, <b>or new demand forms</b> "
    "at an area that there once was sellers, then I would focus on playing the market long "
    "<b>targeting the next supply zone</b> above that, which was 4117\"", "quote"))
A(P("<b>Bearish:</b> \"to validate this short setup <b>I want this level to reject and "
    "break below 4100</b>, and then I'm interested in playing short <b>targeting 4090</b>\"",
    "quote"))
A(P("<b>HIS RULE.</b> Note that the bearish branch needs <i>two</i> things - a rejection "
    "at the level <b>and</b> a break of the round number below it. The level alone is not "
    "the trigger. In the event he skipped the short entirely because the second condition "
    "never came."))
A(P("And the plan is live, not fixed: \"<b>I updated the Discord in the intraday commentary "
    "tab</b> - this is where I update my thoughts throughout the day.\" On the day in "
    "question he abandoned the bearish scenario mid-morning and traded the bullish one."))

A(P("5. Where the key level comes from", "h2"))
A(P("Module 1 could not answer this. These videos do, and the answer is that it is not "
    "always a supply or demand zone at all. Three distinct sources appear:"))
A(P("<b>1. Yesterday's order-flow evidence.</b> \"4107 and 4110 was a resistance level from "
    "yesterday where we actually took the market short - <b>we spotted sellers on the tape</b> "
    "the day prior... <b>it's not really supply</b>, because this level was formulated "
    "spotting sellers on the tape\"", "quote"))
A(P("<b>2. The edge of a previous balance area.</b> \"we had a support level at 12980 to "
    "13015... it's an old previous little balance range low. <b>It's not so much supply, "
    "it's not so much demand - it's just a previous balanced range low</b>\"", "quote"))
A(P("<b>3. An ordinary supply or demand zone</b>, as drawn in Module 1."))
A(P("<b>4. A delta outlier.</b> This one does not appear in the 2022-23 videos at all - it "
    "comes from the 2025 material, and Module 3 covers it properly. In short: an unusually "
    "large one-sided volume print at a single price, where price then <i>refuses to move</i> "
    "in the direction of all that aggression, implying someone is absorbing it. When the "
    "same price does it again on a later session, it goes into the next day's plan as a key "
    "level - which is exactly how his 6575 level was built."))
A(P("<b>HIS RULE.</b> A key level is <b>a price where you have evidence that size traded "
    "and mattered</b>. Where the evidence came from is secondary. Note also that both "
    "examples are given as <b>two numbers</b> - a band, never a single price."))

A(P("6. Acceptance versus rejection - the decisive read", "h2"))
A(P("This is the mechanic that tells you which scenario is live, and it is the most "
    "immediately useful idea in the module."))
A(P("\"when the market <b>consolidates</b>, it's <b>building volume at that price</b>. If "
    "you're building volume at that price you have buyers and sellers trading at that "
    "price... there's a lot of what you call <b>acceptance</b> at that level, and <b>the "
    "chance of a high being formed here is slim</b> - and this in fact is a <b>bullish "
    "indication</b>\"", "quote"))
A(KeepTogether([img("m2-05-acceptance.png", 168*mm)]))
A(P("<b>HIS RULE.</b> Price pausing at your level is not the level working. It is the "
    "level <b>failing in slow motion</b>. A level that holds turns price away quickly; a "
    "level that is about to break gets consolidated on first."))
A(P("\"if we come up into a supply zone, or a resistance level, and <b>it acts as "
    "support</b> - if we consolidate there, we fail to sell off lower, we build new "
    "demand - that is a bullish indication and <b>you should avoid taking the market "
    "short</b>\"", "quote"))
A(P("The related timing rule, same video:"))
A(P("\"there's no reason to play it short on the first downside move - <b>I call it a first "
    "seller</b> - no reason to do it. Wait for sellers to come into the market and then you "
    "could play a retest\"", "quote"))

A(P("7. The three ways he plays a level", "h2"))
A(P("From the Module 1 source set, and the clearest piece of structure he gives:"))
A(P("\"these are <b>the three ways that I play support and resistance</b>... point number "
    "one and point number three are <b>continuation</b> setups, and point number two is "
    "mainly a <b>reversal</b> setup. <b>I use point number two the most</b>.\"", "quote"))
A(KeepTogether([img("m2-02-three-ways.png", 168*mm)]))
A(P("The thread running through all three: he is never the one buying the breakout. He is "
    "waiting for it to fail, waiting for it to come back, or already positioned and selling "
    "into the people buying it."))

A(P("8. When a zone stops existing", "h2"))
A(P("\"<b>if we break above supply I will remove the zone</b>... now buyers are moving the "
    "market higher, buyers are stronger, <b>buyers are finding value at higher prices</b>, "
    "and this is a good sign of continuation to the upside\"", "quote"))
A(P("Restated in the newer set: \"since we are below these demand zones, <b>these are all "
    "invalid</b>.\""))
A(KeepTogether([img("m2-03-zone-deleted.png", 168*mm)]))
A(P("The break is not just the loss of a level. It is positive information about the other "
    "side - the same event that deletes the zone is a reason to expect continuation."))

A(P("9. Zones as magnets", "h2"))
A(P("\"one way to use supply and demand is <b>use these levels as magnets to price</b>... "
    "we just broke below demand... <b>there's no other support, there's no other demand "
    "until 3675</b>, and we can look to target that level\"", "quote"))
A(KeepTogether([img("m2-04-magnet.png", 168*mm)]))
A(P("<b>HIS RULE, emphatically.</b> The break itself is not the trade:"))
A(P("\"<b>I don't want anybody to get short just because we break below demand</b>, or get "
    "long just because we break above supply. You have to use more clues and more "
    "structure\"", "quote"))

A(P("10. Related markets - the check outside your chart", "h2"))
A(P("A whole chapter, and the part most directly useful if you trade an index."))
A(P("\"his edge is <b>knowing related markets</b>, and I think this is key even for us day "
    "traders... if he wants to trade crude oil he'll be looking at heating oil or gasoline, "
    "he'll look at the two spreads, he'll look at the net differences, and <b>without even "
    "looking at the charts he'll get a good direction</b> of the market he's looking to "
    "trade\"", "quote"))
A(KeepTogether([img("m2-07-related-markets.png", 168*mm)]))
A(P("<b>HIS RULE.</b> The instrument you trade must be confirmed by the instruments that "
    "drive it. Applied in both directions:"))
A(P("\"if Nasdaq is bouncing off the zone, <b>I want to see other equities also showing "
    "strength</b>. I don't want to see weakness in the market, because that's going to "
    "validate that <b>this bounce off demand is going to be weaker</b> and we are going to "
    "see continued selling\"", "quote"))
A(P("\"if I'm looking to trade Tesla, more than likely <b>I'm not taking this Tesla trade, "
    "because my underlying related market is not really agreeing</b> with this analysis\"",
    "quote"))
A(P("He names a tool for finding what actually drives an index: \"there's a website called "
    "<b>Slick Charts</b>... you could see the weight of each company... <b>look at it as "
    "like a bread basket</b>, and the stocks that are bread in the basket.\""))
A(P("Two more external checks appear in the same set. <b>VIX</b> as trend confirmation - "
    "\"to help with the trend, <b>keep an eye on VIX</b>... VIX was breaking below our "
    "support level, and that's just going to support and fuel a further rally\" - and a "
    "<b>pre-market events check</b>: \"different economic events, news catalysts. I do this "
    "before the market opens up - I'm aware that maybe Powell might be speaking on "
    "Wednesday, or there might be earnings for Tesla tomorrow.\""))

A(P("11. Volume is a gate, not a confirmation", "h2"))
A(P("\"<b>if I don't see volume I probably will not take the trade</b>... volume shows "
    "<b>interest</b>, and if there is no interest in the market the chances of continuation "
    "are very slim\"", "quote"))
A(P("\"<b>if I see a lack of volume in my direction I'm either getting out, or I'm not "
    "taking the trade</b>\"", "quote"))
A(P("<b>HIS RULE.</b> Note this is a veto, and it applies after entry as well - thin volume "
    "in your direction is a reason to leave a trade you are already in."))

A(P("12. If you cannot read it, do not trade it", "h2"))
A(P("\"if I could read the market properly - <b>can I read the story properly?</b> If I "
    "can't, <b>I most likely will not trade it</b>\"", "quote"))
A(P("\"members in the Discord have asked me, sometimes where there was a clean setup, "
    "perfect setup, it worked out according to our pre-market plan - and <b>sometimes I "
    "didn't take the trade because I didn't read it properly</b>... <b>I'm okay with "
    "sitting on my hands</b> and waiting for a better setup\"", "quote"))
A(P("<b>HIS RULE.</b> A setup that qualifies on paper is still skippable if the story "
    "behind it is unclear. He accepts missing winners as the cost."))

A(P("13. Two Module 1 gaps now closed", "h2"))
A(P("<b>A minimum risk-to-reward, which Module 1 recorded as never stated:</b>"))
A(P("\"ideally you want to shoot for <b>at least a two to one</b> risk to reward ratio - "
    "<b>three to one is even better</b> - so we could afford to lose a lot more times than "
    "we win yet still make money\"", "quote"))
A(P("His worked example: \"our risk in this case would be about five points, we're risking "
    "about five, <b>which means we need to make at least 15</b>.\" Module 1's gap note on "
    "this should now be read as answered."))
A(P("<b>The subjectivity is deliberate, not an omission:</b>"))
A(P("\"<b>I draw every zone manually. I do not use any indicator</b> to draw them. <b>The "
    "human eye is the best component</b> to drawing zones, because it's very subjective and "
    "it's also based off of context\"", "quote"))
A(P("So the answer to \"am I missing a rule?\" is largely no. He is claiming the "
    "discretion is the edge, because context cannot be encoded in a zone-drawing "
    "indicator."))

A(P("14. Where the videos disagree", "h2"))
A(P("Two places where the source set does not line up. Both are shown rather than "
    "resolved."))
A(P("<b>Absorption at a high.</b> In one video, heavy absorption at the high argues the "
    "high is <i>not</i> in: \"at the high, 4115, there was <b>massive absorption</b> and a "
    "massive passive seller with a high amount of volume. <b>This does not indicate a high "
    "probability of a high of day being in.</b> You want to see <b>less liquidity</b> and a "
    "lot of trapped participants.\" In another, absorption at the high is exactly the "
    "reversal signal: \"there were large aggressive buy orders at 4335 and price could not "
    "move any higher - a very large passive seller absorbing all those aggressive buy "
    "orders, and <b>it took him three different times and he failed every single time</b>, "
    "indicating a very weak tape.\""))
A(P("The variable he names in the first case is <b>acceptance</b> - volume building and "
    "price staying - and in the second it is <b>repeated failure to advance</b>. That is a "
    "plausible reconciliation, but he never states it as one.", "gap"))
A(P("<b>Freshness.</b> Module 1 section 4 records a zone as ammunition that gets spent. "
    "Here a zone working repeatedly is given as evidence of quality: \"price came back into "
    "this demand zone, bounced... the next day price came back into this demand zone and "
    "bounced at it again - <b>so this is a valid demand zone, it worked three other "
    "times</b>.\" Both readings stand.", "gap"))

A(P("15. Getting better at the discretionary part", "h2"))
A(P("He gives one concrete practice for the part that cannot be written down as a rule:"))
A(P("\"I think <b>entries are the most important thing</b>. A good way to get better at "
    "entries or confirmation is to <b>record your screen every day</b> - and then go back "
    "after the market closes, look at what you could have done, what you should have done, "
    "what you shouldn't have done, and what you did wrong\"", "quote"))
A(P("Paired with the Module 1 instruction to \"collect the journal, build a database,\" "
    "this is his answer to how the discretion is supposed to be acquired. It is not "
    "presented as optional."))

A(P("16. Still missing", "h2"))
A(P("<b>Key zones.</b> Still withheld, and he gestures at the course again in this set: "
    "\"there are videos in the course exactly about this.\" The filter that separates zones "
    "worth trading from zones worth drawing remains the biggest gap.", "gap"))
A(P("<b>How to classify an instrument</b> as mean-reverting or trending. He says it "
    "matters and that it varies by market; he never says how to decide.", "gap"))
A(P("<b>A mechanical trend definition.</b> Still eyeballed from higher-timeframe "
    "structure, as in Module 1.", "gap"))
A(P("<b>How far back context runs.</b> He uses \"the past week, the current week\" in one "
    "place and a daily chart over months in another, without a rule for which applies.",
    "gap"))

A(P("Sources: 05-identify-sd-zones, 06-trading-sd-in-a-trend, 07-why-i-love-sd-zones, "
    "08-what-i-look-for-before-entering, plus carried-over material from the four module-1 "
    "videos. Module 3 is the order-flow trigger; Module 4 the complete method and risk. "
    "Nothing in this document has been tested - it is a record of what he teaches, not a "
    "claim that it works.", "cap"))

# WinAnsi guard
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
    canvas.drawString(21*mm, 10*mm, "Supply & Demand - Module 2: Context")
    canvas.drawRightString(A4[0]-21*mm, 10*mm, "page %d" % doc.page)
    canvas.restoreState()

doc = SimpleDocTemplate(OUT, pagesize=A4,
                        leftMargin=21*mm, rightMargin=21*mm,
                        topMargin=18*mm, bottomMargin=16*mm,
                        title="Carmine Rosato Supply & Demand - Module 2",
                        author="Carmine-SD syllabus")
doc.build(F, onFirstPage=footer, onLaterPages=footer)
print("wrote", OUT, os.path.getsize(OUT), "bytes")
