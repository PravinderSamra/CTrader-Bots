#!/usr/bin/env python3
"""
news_scorer.py — the Alpha Vantage NEWS_SENTIMENT replacement.

Why this exists instead of an API: a generic tone score is the wrong tool for
this job. "Fed holds rates steady" is tonally neutral but directionally
decisive depending on what was priced; "Nvidia beats, guides light" is tonally
positive and reliably bearish. What the brief needs is not sentiment, it is the
**headline -> NAS100 reaction mapping** already specified in
research/04-news-layer.md: direction, magnitude, half-life.

So we work domain-side over the keyless RSS feeds we already pull. No key, no
quota, no free tier that expires, nothing to renew.

IMPORTANT — what this script is and is not. The first version tried to assign a
direction to every headline by keyword. Measured on 124 live headlines it got
8 of its top 14 wrong: "Nasdaq Futures CLIMB After Sharp Selloff" scored
bearish, "Nasdaq 100 SNAPS five-day slump" scored bearish, "IF a Stock Market
Crash Is Coming" scored bearish, and Bitcoin/Qatar/Klarna headlines scored at
all. Bag-of-keywords cannot handle negation, subordinate clauses, hypotheticals
or relevance — and neither can a generic tone score, which is exactly why
swapping in another sentiment API would not have fixed this.

So the script is now a high-precision PRE-FILTER:
  - a relevance gate (US indices / mega-cap tech / US macro only),
  - reversal, hypothetical and negation detection,
  - two confidence tiers.
`HIGH` items are unambiguous enough to score deterministically and are the only
ones that touch the bias number. `NEEDS_JUDGEMENT` items are handed to the
model to read against research/04-news-layer.md, which is where negation and
context actually get handled correctly.

    python3 news_scorer.py            # human-readable
    python3 news_scorer.py --json
"""
import json, re, ssl, sys, urllib.request
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from xml.etree import ElementTree as ET

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/125.0 Safari/537.36"}
CTX = ssl.create_default_context()

FEEDS = {
    "cnbc": "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=100003114",
    "marketwatch": "https://feeds.content.dowjones.io/public/rss/mw_topstories",
    "ft_markets": "https://www.ft.com/markets?format=rss",
    "investing_econ": "https://www.investing.com/rss/news_285.rss",
    "fed_press": "https://www.federalreserve.gov/feeds/press_all.xml",
    "gnews_nasdaq": "https://news.google.com/rss/search?q=nasdaq+100+OR+%22nasdaq+composite%22+when:1d&hl=en-US&gl=US&ceid=US:en",
    "gnews_mag7": "https://news.google.com/rss/search?q=(Nvidia+OR+Apple+OR+Microsoft+OR+Amazon+OR+Meta+OR+Alphabet+OR+Tesla+OR+Broadcom)+stock+when:1d&hl=en-US&gl=US&ceid=US:en",
    "gnews_fed": "https://news.google.com/rss/search?q=(Federal+Reserve+OR+Powell+OR+inflation+OR+CPI)+when:1d&hl=en-US&gl=US&ceid=US:en",
    # per-ticker Yahoo RSS — keyless, ~20 items each, proven 2026-08-22
    "yahoo_nvda": "https://feeds.finance.yahoo.com/rss/2.0/headline?s=NVDA&region=US&lang=en-US",
    "yahoo_qqq": "https://feeds.finance.yahoo.com/rss/2.0/headline?s=QQQ&region=US&lang=en-US",
}

# ---------------------------------------------------------------------------
# RULES: (name, regex, direction, magnitude_pts, half_life_min, note)
# Direction is the NAS100 reaction, NOT the tone of the sentence. Ordered —
# the first match wins, so put the specific patterns above the generic ones.
# Magnitudes come from research/04-news-layer.md.
# ---------------------------------------------------------------------------
RULES = [
    # --- inflation / rates: the biggest lever -------------------------------
    ("cpi_hot", r"\b(cpi|inflation|pce|ppi)\b.{0,40}\b(hot|hotter|above|beat[s]? (?:forecast|expectation)|accelerat|surge|jump|rise[s]?|climb)",
     -1, 250, 75, "Hot inflation -> yields up, multiple compression"),
    ("cpi_cool", r"\b(cpi|inflation|pce|ppi)\b.{0,40}\b(cool|cooler|below|miss|ease[sd]?|slow|fall[s]?|drop)",
     +1, 220, 75, "Cool inflation -> Fed path softens, duration rallies"),
    ("hawkish", r"\b(hawkish|rate hike|raise rates|tighten|higher for longer|no cut|rules out (?:a )?cut)\b",
     -1, 180, 90, "Hawkish repricing -> bearish long-duration tech"),
    ("dovish", r"\b(dovish|rate cut|cut rates|easing|pivot|lower rates)\b",
     +1, 180, 90, "Dovish repricing -> bullish tech"),
    ("yields_up", r"\b(yields?|treasur\w+|10-?year)\b.{0,30}\b(spike|surge|jump|climb|rise|soar|higher)\b",
     -1, 120, 45, "Yields up -> discount rate up"),
    ("yields_down", r"\b(yields?|treasur\w+|10-?year)\b.{0,30}\b(fall|drop|slide|tumble|ease|lower)\b",
     +1, 120, 45, "Yields down -> supports duration"),
    # --- labour -------------------------------------------------------------
    ("jobs_strong", r"\b(payrolls?|jobs? report|nfp|unemployment|jobless)\b.{0,40}\b(strong|beat|surge|jump|robust|tight)",
     -1, 200, 90, "Strong jobs in a hawkish regime -> bearish (rates read dominates)"),
    ("jobs_weak", r"\b(payrolls?|jobs? report|nfp|jobless claims)\b.{0,40}\b(weak|miss|slump|fall|rise[s]? sharply|surge in claims)",
     0, 180, 90, "Weak jobs is AMBIGUOUS: dovish (bullish) vs growth scare (bearish) — needs regime context"),
    # --- tariffs / trade: currently live ------------------------------------
    ("tariff_semi", r"\b(tariffs?|export controls?|trade war|sanctions?|chip ban|entity list)\b.{0,60}\b(chip|semiconductor|tech|nvidia|taiwan|china)\b|\b(chip|semiconductor)\b.{0,60}\b(tariff|export control|ban)\b",
     -1, 220, 240, "Semi tariff/export-control -> hits the most concentrated part of the index"),
    ("tariff_general", r"\b(tariff|trade war|trade deal (?:collapse|fail)|deepen.{0,15}trade)\b",
     -1, 140, 180, "Trade-policy escalation -> risk-off"),
    ("trade_deal", r"\b(trade deal|tariff (?:relief|exemption|rollback|cut)|agreement reached)\b",
     +1, 140, 180, "Trade de-escalation -> risk-on"),
    # --- mega-cap / AI complex ----------------------------------------------
    # Specific before generic: 'Nvidia warns customers of price hikes' is
    # pricing power, and was being caught by the earnings rules below.
    ("ai_pricing_power", r"\b(nvidia|nvda|tsmc|broadcom)\b.{0,50}\b(price (?:hike|increase)|raising prices|supply (?:constraint|shortage)|sold out|allocation)\b",
     +1, 110, 1440, "AI pricing power / supply tightness -> margin support for the complex"),
    ("earnings_beat", r"\b(nvidia|nvda|microsoft|apple|amazon|meta|alphabet|google|tesla|broadcom|avgo|amd|tsmc)\b.{0,60}\b(beats?|tops (?:estimates|forecasts|expectations)|smash\w*|record (?:revenue|profit)|raises? (?:guidance|outlook))\b",
     +1, 150, 180, "Mega-cap beat -> index-weighted lift"),
    ("earnings_miss", r"\b(nvidia|nvda|microsoft|apple|amazon|meta|alphabet|google|tesla|broadcom|avgo|amd|tsmc)\b.{0,60}\b(miss(?:es)? (?:estimates|forecasts|expectations)|disappoint\w*|cuts? (?:guidance|outlook)|warns? (?:on|of|about) (?:weak|slow|lower|soft|declin)|profit warning|plunges?|slumps?|tumbl\w+)\b",
     -1, 170, 180, "Mega-cap miss/warning -> index-weighted drag"),
    ("capex_up", r"\b(ai|data ?cent(?:er|re)|hyperscaler)\b.{0,50}\b(capex|spending|investment)\b.{0,30}\b(raise|increase|boost|record|surge|expand)\b",
     +1, 130, 1440, "AI capex expanding -> the core bull thesis intact"),
    ("capex_down", r"\b(ai|data ?cent(?:er|re)|hyperscaler)\b.{0,50}\b(capex|spending)\b.{0,30}\b(cut|slow|pause|reduce|scale back|digest)\b",
     -1, 200, 1440, "AI capex slowing -> hits the whole complex, multi-day theme"),
    ("ai_bubble", r"\b(ai (?:bubble|hype|overvalued)|bubble (?:burst|fears?)|overvaluation)\b",
     -1, 120, 720, "AI-bubble narrative -> sentiment headwind for the complex"),
    # --- risk / macro regime -------------------------------------------------
    ("risk_off", r"\b(sell-?off|plunge|rout|slump|tumble|crash|panic|flight to safety)\b",
     -1, 150, 60, "Broad risk-off"),
    ("risk_on", r"\b(rally|surge|soar|jump|record high|all-?time high|rebound|snap.{0,12}slump)\b",
     +1, 130, 60, "Broad risk-on"),
    ("credit_stress", r"\b(credit (?:stress|spread|crunch)|debt crisis|default|liquidity crisis|bank failure)\b",
     -1, 200, 720, "Credit stress -> the most reliable bearish tell"),
    ("geopolitics", r"\b(war|invasion|missile|strike[sd]? (?:on|against)|escalat\w+|nuclear)\b",
     -1, 120, 240, "Geopolitical escalation -> risk-off"),
    ("shutdown", r"\b(government shutdown|debt ceiling|funding (?:deadline|lapse))\b",
     -1, 110, 720, "Fiscal brinkmanship"),
    # --- scheduled-event flags: no direction, but they gate the day ---------
    # Added after an audit found "Big week coming up with PCE, Nvidia earnings
    # and then Jackson Hole" being dropped with no rule at all.
    ("jackson_hole", r"\bjackson hole\b",
     0, 200, 240, "Jackson Hole — a policy-setting speech window. Treat like FOMC: stand aside into it, then trade the range it creates"),
    ("fomc_event", r"\b(fomc (?:statement|minutes|meeting|decision)|fed (?:minutes|decision)|rate decision|powell (?:speaks|testimony|press))\b",
     0, 200, 120, "FOMC event — the 19:00 spike is noise, the 19:30 presser sets direction. No entries before 19:50"),
    ("event_preview", r"\b(big week|week ahead|what to (?:expect|watch)|key events?)\b.{0,60}\b(pce|cpi|fomc|fed|earnings|jackson hole|payrolls?)\b",
     0, 0, 1440, "Week-ahead preview — read it for the calendar, not for direction"),
    # --- positioning / flow warnings ----------------------------------------
    ("positioning_stretched", r"\b(positioning|net long|crowded|complacen\w+)\b.{0,45}\b(record|extreme|stretched|high)\b|\b(pullback risk|correction risk)\b",
     -1, 120, 1440, "Stretched positioning -> asymmetric downside if the tape turns"),
]

MEGACAPS = {"nvidia": "NVDA", "nvda": "NVDA", "apple": "AAPL", "microsoft": "MSFT",
            "amazon": "AMZN", "meta": "META", "alphabet": "GOOGL", "google": "GOOGL",
            "tesla": "TSLA", "broadcom": "AVGO", "avgo": "AVGO", "amd": "AMD",
            "tsmc": "TSM", "netflix": "NFLX"}
# ---------------------------------------------------------------------------
# GATES. Every one of these exists because it caught a real misfire on live
# data — the offending headline is quoted next to it.
# ---------------------------------------------------------------------------

# 1. RELEVANCE — must actually be about the US index / mega-cap tech / US macro.
RELEVANT = re.compile(
    r"\b(nasdaq|ndx|qqq|s&p ?500|spx|dow|wall street|us stocks?|stock market|"
    r"us (?:equit|futures)|treasur|yield|fed(?:eral reserve)?|fomc|powell|"
    r"inflation|cpi|pce|ppi|payrolls?|jobless|tariff|rate (?:cut|hike)|"
    r"nvidia|nvda|apple|aapl|microsoft|msft|amazon|amzn|meta|alphabet|google|"
    r"googl|tesla|tsla|broadcom|avgo|\bamd\b|tsmc|semiconductor|chip|"
    r"ai (?:capex|spending|infrastructure|bubble)|hyperscaler|mag ?7|"
    r"magnificent seven)\b", re.I)

# 2. OFF-TOPIC — the headline's SUBJECT is something else. The first version
#    dropped anything merely *mentioning* crypto, which killed
#    "Trump's tariffs, Fed minutes, Rumble's Bitcoin buy — what's moving
#    markets" and "Bitcoin and gold surge as Bessent's intervention in the bond
#    market hits the dollar". Both are macro-relevant. So off-topic now
#    requires the subject to lead the headline AND no hard macro anchor to be
#    present anywhere in it.
OFFTOPIC_SUBJECT = re.compile(
    r"^\W*(bitcoin|btc|ethereum|crypto|dogecoin|altcoin|klarna|qatar|"
    r"rocket lab|spacex|airbnb|hut ?8)\b", re.I)
# A hard macro anchor rescues a headline from the off-topic gate.
MACRO_ANCHOR = re.compile(
    r"\b(fed(?:eral reserve)?|fomc|powell|jackson hole|cpi|pce|inflation|"
    r"tariff|treasur|yield|payrolls?|rate (?:cut|hike|decision)|"
    r"nasdaq|s&p ?500|nvidia|nvda|semiconductor|chips?|export controls?)\b", re.I)

# 3. NOISE — listicles, promos, generic advice. Says nothing about today's tape.
NOISE = re.compile(r"\b(dividend etf|motley fool|zacks|\d+ stocks?|best stocks? to|"
                   r"stockinvest|price prediction|should you buy|here'?s why that|"
                   r"\d+ [\w-]+ stocks?|dividend stocks?|yield over|"
                   r"monthly performance review|playbook says|what to know|"
                   r"how to invest|top \d+|"
                   # Fed press feed is ~90% bank-supervision boilerplate. Strip
                   # it so the genuine policy items (FOMC statement/minutes)
                   # are visible instead of buried.
                   r"announces? approval of (?:the )?application|"
                   r"enforcement action|requests? comment on a proposal|"
                   r"termination of enforcement)\b", re.I)

# 3b. CONTRAST — a "but/however/despite" clause qualifying or reversing the
#     first half of the headline.
CONTRAST = re.compile(r",?\s*\b(but|however|despite|though|although|"
                      r"yet\b|even as|while)\b", re.I)

# 3c. INSTITUTIONAL-FILING SPAM — 13F position-change churn. High volume on the
#     per-ticker feeds, zero intraday signal.
FILING_SPAM = re.compile(
    r"\b(boosts?|trims?|cuts?|raises?|lowers?|acquires?|sells?|buys?|has|takes?)\b"
    r".{0,40}\b(stock )?(position|stake|holdings?|shares?)\b.{0,30}\bin\b|"
    r"\b(13f|sec filing|institutional (?:investor|holder)s?)\b|"
    r"\b(llc|lp|ltd|inc\.?|management|advisors?|capital|partners)\b"
    r".{0,45}\b(position|stake|holdings?)\b", re.I)

# 3d. NOT-YET-HAPPENED — modal verbs, conditionals and forward-looking framing.
#     A headline about what MIGHT happen is not a tradeable event, and the
#     keyword inside it describes a hypothetical, not a fact. Added after
#     "Nvidia Stock MAY PLUNGE After Earnings, EVEN IF It BEATS" scored as a
#     clean earnings beat. This one gate retires a whole class of misfire that
#     was otherwise going to need a new regex per phrasing.
# D7 (2026-09-01) — one Fed story, four framings, three different verdicts.
# "…support rate hike if inflation doesn't ease" and "Higher Rates Needed If
# Inflation Doesn't Cool" both matched `cpi_cool` at direction +1 / confidence
# HIGH, because the rule matches the tokens ease/cool without seeing the
# negation that inverts them. Meanwhile "does not moderate" (no ease/cool
# token) correctly fell to `hawkish` at -1. Which verdict you got depended on
# the synonym a subeditor chose. Those two carried 2 x +2.2 of BULLISH weight
# on an unambiguously hawkish story, and at HIGH confidence they bypassed the
# judgement list where a human would have caught them.
#
# Handled the way this file handles every other inverted reading: do NOT guess
# the flipped sign, demote to the model. Tested against the matched span only,
# so "inflation cooled in August" still scores and "inflation doesn't cool"
# does not.
NEGATOR = re.compile(
    r"\b(?:doesn'?t|does not|do(?:n'?t| not)|didn'?t|did not|isn'?t|is not|"
    r"aren'?t|are not|wasn'?t|was not|won'?t|will not|hasn'?t|has not|"
    r"haven'?t|have not|fail(?:s|ed|ing)? to|refus(?:es|ed|ing) to|"
    r"no sign of|short of|never|not)\b", re.I)

MODAL = re.compile(
    r"\b(may|might|could|would|should|will likely|expected to|set to|poised to|"
    r"on track to|forecast to|predicted to|seen as|braces? for|ahead of|"
    r"even if|unless|in case|if it|what if|risks? (?:of|to)\b|"
    r"warns? (?:that|of a possible)|fears?\b|speculation)\b", re.I)

# 4. HYPOTHETICAL / SPECULATIVE — not an event, so not tradeable.
#    "IF a Stock Market Crash Is Coming, Warren Buffett's Playbook Says Do This"
HYPOTHETICAL = re.compile(
    r"^\s*(if|what if|could|should|why|how|is |are |will )\b|"
    r"\b(if .{0,30}(comes?|coming|happens?|hits?)|could (?:soar|crash|plunge|surge)|"
    r"what (?:it )?means|analysts? (?:say|call)|forecasts? (?:for|that)|"
    r"price prediction|outlook for)\b", re.I)

# 5. REVERSAL — the sentence contains a bearish word describing a PAST state
#    that the headline says is now ENDING. This was the single biggest source
#    of wrong signs.
#    "Nasdaq Futures CLIMB After Sharp Selloff"
#    "US stocks end week on up note, Nasdaq 100 SNAPS five-day slump"
#    "US Stock Futures GAIN as Nasdaq 100 Looks to Snap Five-Day Slump"
REVERSAL_UP = re.compile(
    r"\b(climb|gain|rise|rally|rebound|recover|advance|jump|higher|up)\b"
    r".{0,45}\b(after|as|despite|following|from)\b.{0,30}"
    r"\b(sell-?off|slump|drop|fall|decline|rout|losses?|plunge)\b|"
    r"\b(snap|end|halt|break)\w*\s+(?:a\s+|the\s+)?(?:\w+[- ])?"
    r"(?:day\s+)?(?:slump|slide|losing streak|decline|sell-?off)\b", re.I)
REVERSAL_DOWN = re.compile(
    r"\b(fall|drop|slide|slump|tumble|lower|down|retreat)\b"
    r".{0,45}\b(after|as|despite|following|from)\b.{0,30}"
    r"\b(rally|gains?|surge|record|high|advance)\b|"
    r"\b(snap|end|halt|break)\w*\s+(?:a\s+|the\s+)?(?:\w+[- ])?"
    r"(?:day\s+)?(?:rally|winning streak|advance|record run)\b", re.I)

# Rules trustworthy enough to score without the model. These describe discrete,
# unambiguous events; the vague "market went up/down" rules do not qualify.
HIGH_CONFIDENCE = {
    "cpi_hot", "cpi_cool", "hawkish", "dovish", "jobs_strong",
    "tariff_semi", "tariff_general", "trade_deal",
    "earnings_beat", "earnings_miss", "capex_up", "capex_down",
    "credit_stress", "shutdown",
}


def _fetch(url, timeout=25):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout, context=CTX) as r:
        return r.read()


def pull(feeds=None, per_feed=15):
    feeds = feeds or FEEDS
    now = datetime.now(timezone.utc)
    items, errors = [], {}
    for name, url in feeds.items():
        try:
            root = ET.fromstring(_fetch(url))
        except Exception as e:
            errors[name] = f"{type(e).__name__}: {e}"
            continue
        for it in root.findall(".//item")[:per_feed]:
            title = re.sub(r"\s+", " ", (it.findtext("title") or "")).strip()
            if not title:
                continue
            age_h = None
            pub = (it.findtext("pubDate") or "").strip()
            if pub:
                try:
                    age_h = round((now - parsedate_to_datetime(pub)).total_seconds() / 3600, 1)
                except Exception:
                    pass
            items.append({"source": name, "title": title, "published": pub,
                          "age_h": age_h})
    # de-duplicate across feeds on a normalised title
    seen, uniq = set(), []
    for i in items:
        k = re.sub(r"[^a-z0-9]", "", i["title"].lower())[:70]
        if k in seen:
            continue
        seen.add(k); uniq.append(i)
    return uniq, errors


def score_item(it):
    """-> scored dict, or None if the headline is filtered out.

    A returned item carries `confidence`: HIGH items are scored and feed the
    bias number; NEEDS_JUDGEMENT items are surfaced with `direction: None` for
    the model to read in context."""
    t = it["title"]
    # Only promotional/listicle noise is dropped outright. For a PRE-FILTER,
    # over-filtering is the dangerous failure — signal that never reaches the
    # model is lost, whereas an extra headline the model discards costs almost
    # nothing. So everything else that is topically relevant falls through to
    # NEEDS_JUDGEMENT rather than being binned.
    if NOISE.search(t) or FILING_SPAM.search(t):
        return None
    if OFFTOPIC_SUBJECT.search(t) and not MACRO_ANCHOR.search(t):
        return None
    if not RELEVANT.search(t):
        return None
    # Feeds mix straight and curly punctuation for the same word, and every
    # RULES pattern is written with straight apostrophes. Left un-normalised,
    # "Doesn't Cool" and "Doesn’t Cool" take different paths through the
    # scorer - which is how a curly apostrophe alone kept one framing of the
    # D7 story scoring +2.2 BULLISH after the negation guard was added.
    low = (t.lower().replace("’", "'").replace("‘", "'")
                    .replace("“", '"').replace("”", '"')
                    .replace("–", "-").replace("—", "-"))
    for name, pat, direction, mag, hl, note in RULES:
        m = re.search(pat, low, re.I)
        if not m:
            continue

        flags = []
        # D7 — a negator INSIDE the matched phrase inverts the keyword's sense.
        if NEGATOR.search(m.group(0)):
            flags.append("negation inside the matched phrase — the keyword's "
                         "sense is inverted; read it directly")
        # A reversal phrase inverts the plain-keyword reading. Rather than
        # guess the inverted sign, demote to the model — "climb after selloff"
        # is bullish, but "snaps slump" during a downtrend may just be a bounce.
        if REVERSAL_UP.search(t):
            flags.append("reversal_up: bearish words describe an ENDING state")
        if REVERSAL_DOWN.search(t):
            flags.append("reversal_down: bullish words describe an ENDING state")
        if HYPOTHETICAL.search(t):
            flags.append("hypothetical/speculative, not an event")
        # A contrast clause usually reverses or qualifies the headline's first
        # half. "US Inflation Is Cooling on Paper, BUT Price Pressures Have Gone
        # Far Beyond..." scored as a clean cool-CPI print; it is the opposite.
        if CONTRAST.search(t):
            flags.append("contrast clause (but/however/despite) qualifies the claim")
        if MODAL.search(t):
            flags.append("modal/conditional — describes what MIGHT happen, not an event")
        # Crypto-led headline that only reached us via a macro anchor: worth
        # surfacing, never worth auto-scoring.
        if OFFTOPIC_SUBJECT.search(t):
            flags.append("off-topic subject, rescued by a macro anchor — context only")

        ent = sorted({v for k, v in MEGACAPS.items() if re.search(rf"\b{k}\b", low)})
        age = it.get("age_h")
        fresh = (1.0 if age is None or age <= 4 else
                 0.6 if age <= 12 else 0.3 if age <= 24 else 0.1)

        confident = (name in HIGH_CONFIDENCE) and not flags
        return {**it, "rule": name,
                "direction": direction if confident else None,
                "magnitude_pts": mag, "half_life_min": hl,
                "entities": ent, "freshness": fresh, "note": note,
                "flags": flags,
                "confidence": "HIGH" if confident else "NEEDS_JUDGEMENT",
                "weighted": (round(direction * (mag / 100) * fresh, 2)
                             if confident else 0.0)}

    # Topically relevant but no rule matched. Previously binned — the audit
    # found "Federal Reserve issues FOMC statement" and "S&P 500 positioning at
    # record highs, Citi warns" being lost this way. Surface it for the model
    # if it carries a hard macro anchor.
    if MACRO_ANCHOR.search(t):
        age = it.get("age_h")
        return {**it, "rule": "unclassified",
                "direction": None, "magnitude_pts": None, "half_life_min": None,
                "entities": sorted({v for k, v in MEGACAPS.items()
                                    if re.search(rf"\b{k}\b", low)}),
                "freshness": (1.0 if age is None or age <= 4 else
                              0.6 if age <= 12 else 0.3 if age <= 24 else 0.1),
                "note": "no rule matched — read it directly",
                "flags": [], "confidence": "NEEDS_JUDGEMENT", "weighted": 0.0}
    return None


def run():
    items, errors = pull()
    scored = [s for s in (score_item(i) for i in items) if s]
    scored.sort(key=lambda s: (-abs(s["weighted"]), s.get("age_h") or 99))
    high = [s for s in scored if s["confidence"] == "HIGH"]
    judge = [s for s in scored if s["confidence"] == "NEEDS_JUDGEMENT"]
    total = round(sum(s["weighted"] for s in high), 2)
    bull = [s for s in high if s["direction"] and s["direction"] > 0]
    bear = [s for s in high if s["direction"] and s["direction"] < 0]
    amb = [s for s in high if s["direction"] == 0]
    # map the raw sum onto the bias engine's +/-4 band
    capped = max(-4, min(4, round(total / 2)))
    label = ("BULLISH" if capped >= 2 else "MILDLY BULLISH" if capped == 1 else
             "BEARISH" if capped <= -2 else "MILDLY BEARISH" if capped == -1 else
             "NEUTRAL")
    return {"generated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "feeds_ok": len(FEEDS) - len(errors), "feeds_total": len(FEEDS),
            "feed_errors": errors,
            "headlines_pulled": len(items),
            "passed_relevance": len(scored),
            "scored_high_confidence": len(high),
            "needs_model_judgement": len(judge),
            "raw_score": total, "bias_points": capped, "label": label,
            "counts": {"bullish": len(bull), "bearish": len(bear),
                       "ambiguous": len(amb)},
            "high_confidence": high[:10],
            "for_model_judgement": judge[:10]}


if __name__ == "__main__":
    r = run()
    if "--json" in sys.argv:
        print(json.dumps(r, indent=2)); sys.exit(0)
    print(f"feeds {r['feeds_ok']}/{r['feeds_total']}  |  "
          f"{r['headlines_pulled']} pulled -> {r['passed_relevance']} relevant "
          f"-> {r['scored_high_confidence']} auto-scored, "
          f"{r['needs_model_judgement']} for model judgement")
    if r["feed_errors"]:
        print("  feed errors:", r["feed_errors"])
    print(f"\nNEWS SCORE {r['raw_score']:+.2f} -> bias {r['bias_points']:+d} "
          f"[{r['label']}]  ({r['counts']})")
    print("\n--- HIGH CONFIDENCE (these move the bias number) ---")
    for s in r["high_confidence"] or []:
        d = "+" if s["direction"] > 0 else ("-" if s["direction"] < 0 else "?")
        print(f" [{d}] {s['weighted']:+5.2f} {s['rule']:<15} "
              f"{','.join(s['entities']) or '-':<8} "
              f"{(str(s['age_h'])+'h') if s['age_h'] is not None else '?':>5}  "
              f"{s['title'][:70]}")
        print(f"       -> {s['note']} | ~{s['magnitude_pts']}pts, "
              f"half-life {s['half_life_min']}min")
    if not r["high_confidence"]:
        print("  (none)")
    print("\n--- NEEDS MODEL JUDGEMENT (read against 04-news-layer.md) ---")
    for s in r["for_model_judgement"] or []:
        print(f"  ~ {s['rule']:<15} "
              f"{(str(s['age_h'])+'h') if s['age_h'] is not None else '?':>5}  "
              f"{s['title'][:72]}")
        if s["flags"]:
            print(f"       flags: {'; '.join(s['flags'])}")
