#!/usr/bin/env python3
"""
test_news_scorer.py — regression tests for the news pre-filter.

Every FALSE case is a real misfire observed on live RSS during Phase 1. Every
TRUE case is a hard-news headline the HIGH tier must still catch, so that
tightening the gates cannot quietly reduce the scorer to "never fires".

    python3 test_news_scorer.py
"""
import sys
from news_scorer import score_item

# (headline, expected_confidence, expected_direction_or_None, why)
CASES = [
    # ---- must AUTO-SCORE: unambiguous, declarative, past-tense events -------
    ("US CPI rises 0.4%, hotter than forecast", "HIGH", -1,
     "hard inflation print, no hedging"),
    ("Core PCE cools to 2.1%, below expectations", "HIGH", +1,
     "hard disinflation print"),
    ("Nvidia beats estimates, raises guidance", "HIGH", +1,
     "declarative earnings beat"),
    ("Broadcom cuts guidance for the fourth quarter", "HIGH", -1,
     "declarative guidance cut"),
    ("White House imposes new export controls on chip sales to China", "HIGH", -1,
     "semi export controls — the highest-impact tariff variant"),
    ("Microsoft raises AI data center capex to record level", "HIGH", +1,
     "capex expansion, the core bull thesis"),

    # ---- must NOT auto-score: the observed misfires ------------------------
    ("Dow, S&P 500, Nasdaq Futures Climb After Sharp Selloff", "NEEDS_JUDGEMENT", None,
     "reversal: bearish word describes an ENDING state"),
    ("US stocks end week on up note, Nasdaq 100 snaps five-day slump", "NEEDS_JUDGEMENT", None,
     "reversal: 'snaps slump' is bullish"),
    ("Nvidia Stock May Plunge After Earnings, Even If It Beats", "NEEDS_JUDGEMENT", None,
     "modal + conditional, not an event"),
    ("US Inflation Is Cooling on Paper, but Price Pressures Have Gone Far Beyond", "NEEDS_JUDGEMENT", None,
     "contrast clause reverses the first half"),
    ("Nvidia Reportedly Warns Top Customers of 15% Price Hikes on AI Servers", "NEEDS_JUDGEMENT", None,
     "pricing power, not an earnings warning; 'Top' must not match 'tops estimates'"),

    # ---- must be DROPPED entirely ------------------------------------------
    ("If a Stock Market Crash Is Coming, Warren Buffett's Playbook Says Do This", None, None,
     "hypothetical + promo"),
    ("Analyst calls Bitcoin 'global bubble', could soar to infinity", None, None,
     "crypto subject, no macro anchor"),
    ("Klarna's stock crash shows the price of being a small fish", None, None,
     "irrelevant single small-cap"),
    ("Qatar cuts state spending at home and abroad as war shrinks economy", None, None,
     "irrelevant"),
    ("Hudson Value Partners LLC Boosts Stock Position in NVIDIA Corporation", None, None,
     "13F filing spam"),
    ("These 4 Dividend Stocks Yield Over 7%", None, None, "listicle"),
    ("Federal Reserve Board announces approval of application by NatWest Plc", None, None,
     "Fed bank-supervision boilerplate"),

    # ---- must SURFACE for the model (relevant, no clean rule) --------------
    ("Nvidia earnings and Jackson Hole: What to watch this week", "NEEDS_JUDGEMENT", None,
     "major event window must not be lost"),
    ("Federal Reserve issues FOMC statement", "NEEDS_JUDGEMENT", None,
     "real policy item, must survive the boilerplate filter"),
    ("S&P 500 positioning levels at record highs, pullback risks rise, Citi warns", "NEEDS_JUDGEMENT", None,
     "positioning warning must reach the model"),
    ("Trump's tariffs, Fed minutes, Rumble's Bitcoin buy - what's moving markets", "NEEDS_JUDGEMENT", None,
     "mentions crypto but the subject is macro — must not be dropped"),
]


def main():
    fails = []
    for title, exp_conf, exp_dir, why in CASES:
        got = score_item({"title": title, "source": "test", "age_h": 1.0})
        conf = got["confidence"] if got else None
        direction = got["direction"] if got else None
        ok = (conf == exp_conf) and (direction == exp_dir)
        print(f"{'PASS' if ok else 'FAIL'}  {str(conf):<16} "
              f"{str(direction):>5}  {title[:60]}")
        if not ok:
            fails.append((title, exp_conf, exp_dir, conf, direction, why))
    print(f"\n{len(CASES) - len(fails)}/{len(CASES)} passed")
    for t, ec, ed, gc, gd, why in fails:
        print(f"\n  FAIL: {t}\n    expected {ec}/{ed}, got {gc}/{gd}\n    ({why})")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
