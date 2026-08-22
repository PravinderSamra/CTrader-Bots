#!/usr/bin/env python3
"""
source_health.py — Phase-1 connectivity harness.

Probes every candidate data source for the NAS100 Daily Brief and reports
PASS / FAIL with latency and a content sanity-check. Run this before trusting
any source, and re-run it as a pre-flight inside the Phase-2 skill so a dead
feed degrades the brief loudly instead of silently.

    python3 source_health.py            # all probes
    python3 source_health.py --json     # machine-readable
"""
import json, ssl, sys, time, urllib.request, urllib.error
from datetime import datetime, timezone

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/125.0 Safari/537.36"}
CTX = ssl.create_default_context()

# (key, category, url, expect_substring_or_None, note)
PROBES = [
    # ---- price / structure -------------------------------------------------
    ("ndx_cash_cboe",   "price",  "https://cdn.cboe.com/api/global/delayed_quotes/quotes/_NDX.json",  "current_price", "NDX cash spot, 15-min delayed"),
    ("ndx_cash_yahoo",  "price",  "https://query1.finance.yahoo.com/v8/finance/chart/%5ENDX?range=5d&interval=1d", "chart", "NDX daily OHLC, 5d"),
    ("nq_futures_1m",   "price",  "https://query1.finance.yahoo.com/v8/finance/chart/NQ%3DF?range=1d&interval=1m", "chart", "NQ front-month 1m — overnight/Globex range"),
    ("es_futures",      "price",  "https://query1.finance.yahoo.com/v8/finance/chart/ES%3DF?range=2d&interval=15m", "chart", "ES cross-check / risk breadth"),
    # ---- options / GEX -----------------------------------------------------
    ("ndx_options",     "gex",    "https://cdn.cboe.com/api/global/delayed_quotes/options/_NDX.json", "open_interest", "NDX chain w/ OI + greeks (~7MB)"),
    ("qqq_options",     "gex",    "https://cdn.cboe.com/api/global/delayed_quotes/options/QQQ.json",  "open_interest", "QQQ chain w/ OI + greeks (~5MB)"),
    ("qqq_quote",       "gex",    "https://cdn.cboe.com/api/global/delayed_quotes/quotes/QQQ.json",   "current_price", "QQQ spot, for NDX/QQQ scaling ratio"),
    # ---- volatility regime -------------------------------------------------
    ("vix",             "vol",    "https://cdn.cboe.com/api/global/delayed_quotes/quotes/_VIX.json",  "current_price", "VIX — 30d SPX implied vol"),
    ("vxn",             "vol",    "https://query1.finance.yahoo.com/v8/finance/chart/%5EVXN?range=5d&interval=1d", "chart", "VXN — the NASDAQ-100 vol index (primary)"),
    ("vix9d",           "vol",    "https://cdn.cboe.com/api/global/delayed_quotes/quotes/_VIX9D.json","current_price", "VIX9D — 9-day; VIX9D/VIX = term-structure stress"),
    ("vvix",            "vol",    "https://cdn.cboe.com/api/global/delayed_quotes/quotes/_VVIX.json", "current_price", "VVIX — vol-of-vol, tail-hedging demand"),
    # ---- macro / rates / FX ------------------------------------------------
    ("us10y",           "macro",  "https://query1.finance.yahoo.com/v8/finance/chart/%5ETNX?range=5d&interval=1d", "chart", "US 10y yield — discount rate on long-duration tech"),
    ("us2y",            "macro",  "https://query1.finance.yahoo.com/v8/finance/chart/%5EFVX?range=5d&interval=1d", "chart", "US 5y (2y ^UST2YR unreliable on Yahoo)"),
    ("us13w",           "macro",  "https://query1.finance.yahoo.com/v8/finance/chart/%5EIRX?range=5d&interval=1d", "chart", "13-week bill — risk-free proxy for BS gamma"),
    ("dxy",             "macro",  "https://query1.finance.yahoo.com/v8/finance/chart/DX-Y.NYB?range=5d&interval=1d", "chart", "Dollar index — inverse risk appetite"),
    ("ust_curve_xml",   "macro",  "https://home.treasury.gov/resource-center/data-chart-center/interest-rates/pages/xml?data=daily_treasury_yield_curve&field_tdr_date_value=2026", "BC_10YEAR", "Official Treasury par curve (daily, authoritative)"),
    # ---- calendar ----------------------------------------------------------
    ("ff_calendar",     "calendar","https://nfs.faireconomy.media/ff_calendar_thisweek.json", "impact", "ForexFactory week calendar w/ High/Med/Low impact"),
    ("nasdaq_econ_cal", "calendar","https://api.nasdaq.com/api/calendar/economicevents?date={TODAY}", "eventName", "Nasdaq econ events for a specific date"),
    ("nasdaq_earn_cal", "calendar","https://api.nasdaq.com/api/calendar/earnings?date={TODAY}", "symbol", "Nasdaq earnings calendar — MAG7 dates"),
    ("fed_calendar",    "calendar","https://www.federalreserve.gov/newsevents/calendar.htm", "calendar", "Fed speakers / FOMC dates (HTML)"),
    # ---- news --------------------------------------------------------------
    ("cnbc_rss",        "news",   "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=100003114", "<item", "CNBC top news"),
    ("marketwatch_rss", "news",   "https://feeds.content.dowjones.io/public/rss/mw_topstories", "<item", "MarketWatch top stories"),
    ("yahoo_fin_rss",   "news",   "https://finance.yahoo.com/news/rssindex", "<item", "Yahoo Finance newsfeed"),
    ("ft_markets_rss",  "news",   "https://www.ft.com/markets?format=rss", "<item", "FT Markets"),
    ("investing_rss",   "news",   "https://www.investing.com/rss/news_285.rss", "<item", "Investing.com economic news"),
    ("fed_press_rss",   "news",   "https://www.federalreserve.gov/feeds/press_all.xml", "<item", "Fed press releases (rate/policy headlines)"),
    ("gnews_nasdaq",    "news",   "https://news.google.com/rss/search?q=nasdaq+100+when:1d&hl=en-US&gl=US&ceid=US:en", "<item", "Google News — NASDAQ, last 24h"),
    ("gnews_mag7",      "news",   "https://news.google.com/rss/search?q=(Nvidia+OR+Apple+OR+Microsoft+OR+Amazon+OR+Meta+OR+Alphabet+OR+Tesla)+stock+when:1d&hl=en-US&gl=US&ceid=US:en", "<item", "Google News — MAG7, last 24h"),
    # ---- known-dead / key-required (documented, probed to prove the verdict)
    ("cnn_fear_greed",  "dead",   "https://production.dataviz.cnn.io/index/fearandgreed/graphdata", "fear_and_greed", "418 bot-block — do not use"),
    ("stooq_ndx",       "dead",   "https://stooq.com/q/d/l/?s=%5Endq&i=d", "Date,Open", "JS challenge — do not use"),
    ("yahoo_options_v7","dead",   "https://query1.finance.yahoo.com/v7/finance/options/QQQ", "optionChain", "401 crumb-gated — CBOE covers this"),
    ("tradingeconomics","dead",   "https://api.tradingeconomics.com/calendar?c=guest:guest&f=json", "[", "guest account discontinued"),
]


def probe(url, expect, timeout=60):
    t0 = time.time()
    try:
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=timeout, context=CTX) as r:
            body = r.read()
            ms = int((time.time() - t0) * 1000)
            head = body[:400000].decode("utf-8", "ignore")
            ok = (expect is None) or (expect in head)
            return {"status": r.status, "ms": ms, "bytes": len(body),
                    "content_ok": ok,
                    "verdict": "PASS" if (r.status == 200 and ok) else "CONTENT_FAIL"}
    except urllib.error.HTTPError as e:
        return {"status": e.code, "ms": int((time.time() - t0) * 1000),
                "bytes": 0, "content_ok": False, "verdict": f"HTTP_{e.code}"}
    except Exception as e:
        return {"status": None, "ms": int((time.time() - t0) * 1000), "bytes": 0,
                "content_ok": False, "verdict": f"ERR_{type(e).__name__}"}


def main():
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    results = {}
    for key, cat, url, expect, note in PROBES:
        r = probe(url.replace("{TODAY}", today), expect)
        r.update(category=cat, note=note, url=url)
        results[key] = r
        if "--json" not in sys.argv:
            mark = "PASS" if r["verdict"] == "PASS" else "FAIL"
            print(f"[{mark:4}] {cat:8} {key:18} {str(r['status']):>4} "
                  f"{r['ms']:>6}ms {r['bytes']:>9,}B  {note}")
    live = [k for k, v in results.items()
            if v["verdict"] == "PASS" and v["category"] != "dead"]
    broken = [k for k, v in results.items()
              if v["verdict"] != "PASS" and v["category"] != "dead"]
    if "--json" in sys.argv:
        print(json.dumps({"as_of": today, "results": results,
                          "live": live, "broken": broken}, indent=2))
    else:
        print(f"\nLIVE  ({len(live)}): {', '.join(live)}")
        print(f"BROKEN({len(broken)}): {', '.join(broken) or 'none'}")
    return 0 if not broken else 1


if __name__ == "__main__":
    sys.exit(main())
