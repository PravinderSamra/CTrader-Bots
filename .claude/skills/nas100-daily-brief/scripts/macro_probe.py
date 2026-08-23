#!/usr/bin/env python3
"""
macro_probe.py — Phase-1 prototype: the NAS100 macro / risk / calendar layer.

Pulls only sources proven live by source_health.py. No API keys, no scraping of
JS-rendered pages. Returns one JSON blob small enough to drop straight into a
brief without burning context on raw feeds.

    python3 macro_probe.py             # human-readable
    python3 macro_probe.py --json      # machine-readable
"""
import json, re, ssl, sys, urllib.request, urllib.error
from datetime import datetime, timezone, timedelta
from xml.etree import ElementTree as ET

try:
    import fred_probe
except Exception:
    fred_probe = None
try:
    import news_scorer
except Exception:            # module missing -> degrade, never crash the brief
    news_scorer = None

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/125.0 Safari/537.36"}
CTX = ssl.create_default_context()
MAG7 = {"NVDA", "AAPL", "MSFT", "AMZN", "META", "GOOGL", "GOOG", "TSLA",
        "AVGO", "AMD", "NFLX", "COST", "TSM"}   # heaviest NDX weights + AI complex


def _fetch(url, timeout=40):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout, context=CTX) as r:
        return r.read()


def _json(url, timeout=40):
    try:
        return json.loads(_fetch(url, timeout).decode("utf-8", "ignore"))
    except Exception as e:
        return {"_error": f"{type(e).__name__}: {e}"}


def yahoo_series(sym, rng="10d", iv="1d"):
    """-> {last, prev, chg, chg_pct, high, low, series[]} or {_error}."""
    u = (f"https://query1.finance.yahoo.com/v8/finance/chart/"
         f"{urllib.request.quote(sym)}?range={rng}&interval={iv}")
    d = _json(u)
    if "_error" in d:
        return d
    try:
        res = d["chart"]["result"][0]
        meta, q = res["meta"], res["indicators"]["quote"][0]
        closes = [c for c in q["close"] if c is not None]
        highs = [c for c in q["high"] if c is not None]
        lows = [c for c in q["low"] if c is not None]
        last = meta.get("regularMarketPrice") or closes[-1]
        # NOTE: meta["chartPreviousClose"] is the close BEFORE THE WHOLE RANGE,
        # not the prior session. Using it for a 10d range reports a 10-day move
        # as if it were today's — it made AVGO print -13.9% instead of +1.2% and
        # flipped the breadth component of the bias score. Always derive the
        # prior session from the series itself.
        prev = closes[-2] if len(closes) > 1 else last
        range_start = meta.get("chartPreviousClose") or closes[0]
        return {"symbol": sym, "last": round(last, 4), "prev_close": round(prev, 4),
                "chg": round(last - prev, 4),
                "chg_pct": round((last - prev) / prev * 100, 3) if prev else None,
                "range_chg_pct": (round((last - range_start) / range_start * 100, 3)
                                  if range_start else None),
                "period_high": round(max(highs), 4), "period_low": round(min(lows), 4),
                "n": len(closes)}
    except Exception as e:
        return {"_error": f"parse: {type(e).__name__}: {e}"}


def cboe_quote(sym):
    d = _json(f"https://cdn.cboe.com/api/global/delayed_quotes/quotes/{sym}.json")
    if "_error" in d:
        return d
    q = d.get("data", {})
    return {"symbol": sym, "last": q.get("current_price"),
            "chg": q.get("price_change"), "chg_pct": q.get("price_change_percent"),
            "prev_close": q.get("prev_day_close"), "as_of": d.get("timestamp")}


# --------------------------------------------------------------------------- #
def overnight_futures():
    """Globex NQ session: the overnight range IS the Asia/London high-low the
    NAS100 CFD gaps around. Split into Asia (21:00-06:00 UK) and London
    (06:00-13:30 UK) windows for the sweep-level list."""
    d = _json("https://query1.finance.yahoo.com/v8/finance/chart/NQ%3DF?range=2d&interval=5m")
    if "_error" in d:
        return d
    try:
        res = d["chart"]["result"][0]
        ts = res["timestamp"]; q = res["indicators"]["quote"][0]
        bars = [{"t": datetime.fromtimestamp(t, timezone.utc),
                 "h": h, "l": l, "c": c, "v": v or 0}
                for t, h, l, c, v in zip(ts, q["high"], q["low"], q["close"], q["volume"])
                if h is not None and l is not None]
        if not bars:
            return {"_error": "no bars"}
        last_t = bars[-1]["t"]
        # walk back to the most recent 21:00 UTC futures re-open
        anchor = last_t.replace(hour=21, minute=0, second=0, microsecond=0)
        if last_t.hour < 21:
            anchor -= timedelta(days=1)
        sess = [b for b in bars if b["t"] >= anchor]
        def win(h0, h1):
            w = [b for b in sess if h0 <= ((b["t"] - anchor).total_seconds() / 3600) < h1]
            return ({"high": round(max(b["h"] for b in w), 1),
                     "low": round(min(b["l"] for b in w), 1),
                     "bars": len(w)} if w else None)
        return {
            "session_open_utc": anchor.isoformat(),
            "last_bar_utc": last_t.isoformat(),
            "last": round(bars[-1]["c"], 1),
            "globex_high": round(max(b["h"] for b in sess), 1) if sess else None,
            "globex_low": round(min(b["l"] for b in sess), 1) if sess else None,
            "asia_window_21_06utc": win(0, 9),
            "london_window_06_1230utc": win(9, 15.5),
            "note": "NQ futures points; convert to the NAS100 CFD with the cash/CFD offset",
        }
    except Exception as e:
        return {"_error": f"parse: {type(e).__name__}: {e}"}


def calendar_today_and_week():
    out = {}
    ff = _json("https://nfs.faireconomy.media/ff_calendar_thisweek.json")
    if isinstance(ff, list):
        now = datetime.now(timezone.utc)
        ev = []
        for e in ff:
            if e.get("country") not in ("USD",):
                continue
            if e.get("impact") not in ("High", "Medium"):
                continue
            try:
                dt = datetime.fromisoformat(e["date"]).astimezone(timezone.utc)
            except Exception:
                continue
            ev.append({"utc": dt.isoformat(), "impact": e["impact"],
                       "title": e["title"], "forecast": e.get("forecast"),
                       "previous": e.get("previous"),
                       "hours_away": round((dt - now).total_seconds() / 3600, 1)})
        out["us_events_this_week"] = sorted(ev, key=lambda x: x["utc"])
        out["upcoming_next_24h"] = [e for e in out["us_events_this_week"]
                                    if 0 <= e["hours_away"] <= 24]
    else:
        out["_ff_error"] = ff.get("_error")

    # earnings for the next 5 sessions, filtered to NDX heavyweights
    hits = []
    for i in range(6):
        d = (datetime.now(timezone.utc) + timedelta(days=i)).strftime("%Y-%m-%d")
        j = _json(f"https://api.nasdaq.com/api/calendar/earnings?date={d}", timeout=30)
        rows = ((j.get("data") or {}) or {}).get("rows") or []
        for r in rows:
            if (r.get("symbol") or "").upper() in MAG7:
                hits.append({"date": d, "symbol": r["symbol"],
                             "when": r.get("time"), "eps_forecast": r.get("epsForecast"),
                             "market_cap": r.get("marketCap")})
    out["heavyweight_earnings_next_5d"] = hits
    return out


def rss_headlines(url, limit=8):
    try:
        raw = _fetch(url, timeout=30)
        root = ET.fromstring(raw)
        items = root.findall(".//item")[:limit]
        out = []
        for it in items:
            title = (it.findtext("title") or "").strip()
            pub = (it.findtext("pubDate") or "").strip()
            title = re.sub(r"\s+", " ", title)
            out.append({"title": title[:180], "published": pub[:31]})
        return out
    except Exception as e:
        return [{"_error": f"{type(e).__name__}: {e}"}]


def news_layer():
    return {
        "cnbc": rss_headlines("https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=100003114", 8),
        "marketwatch": rss_headlines("https://feeds.content.dowjones.io/public/rss/mw_topstories", 6),
        "fed_press": rss_headlines("https://www.federalreserve.gov/feeds/press_all.xml", 4),
        "nasdaq_24h": rss_headlines("https://news.google.com/rss/search?q=nasdaq+100+when:1d&hl=en-US&gl=US&ceid=US:en", 8),
        "mag7_24h": rss_headlines("https://news.google.com/rss/search?q=(Nvidia+OR+Apple+OR+Microsoft+OR+Amazon+OR+Meta+OR+Alphabet+OR+Tesla)+stock+when:1d&hl=en-US&gl=US&ceid=US:en", 8),
    }


def run():
    vix = cboe_quote("_VIX"); vix9d = cboe_quote("_VIX9D"); vvix = cboe_quote("_VVIX")
    vxn = yahoo_series("^VXN")
    term = None
    try:
        term = round(vix9d["last"] / vix["last"], 3)
    except Exception:
        pass
    return {
        "generated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "index": {
            "ndx_cash": cboe_quote("_NDX"),
            "ndx_daily": yahoo_series("^NDX"),
            "qqq": cboe_quote("QQQ"),
        },
        "futures": overnight_futures(),
        "volatility": {
            "vxn_nasdaq_ivol": vxn, "vix": vix, "vix9d": vix9d, "vvix": vvix,
            "vix9d_over_vix": term,
            "term_read": (None if term is None else
                          "BACKWARDATED — near-term stress, expect range expansion" if term > 1.0
                          else "CONTANGO — calm, mean-reversion favoured" if term < 0.92
                          else "FLAT — neutral"),
        },
        "rates_fx": {
            "us10y": yahoo_series("^TNX"), "us5y": yahoo_series("^FVX"),
            "us13w": yahoo_series("^IRX"), "dxy": yahoo_series("DX-Y.NYB"),
        },
        "breadth_proxy": {
            "es_sp500": yahoo_series("ES=F", "5d", "1d"),
            "nvda": yahoo_series("NVDA"), "msft": yahoo_series("MSFT"),
            "aapl": yahoo_series("AAPL"), "avgo": yahoo_series("AVGO"),
        },
        "fred": (fred_probe.run() if fred_probe else
                 {"key_present": False, "read": [],
                  "_error": "fred_probe unavailable"}),
        "calendar": calendar_today_and_week(),
        "news": news_layer(),
        "news_scored": (news_scorer.run() if news_scorer else
                        {"_error": "news_scorer unavailable"}),
    }


if __name__ == "__main__":
    data = run()
    if "--json" in sys.argv:
        print(json.dumps(data, indent=2, default=str))
    else:
        v = data["volatility"]; r = data["rates_fx"]
        print(f"as of {data['generated_utc']}")
        print(f"NDX cash   {data['index']['ndx_cash'].get('last')}  "
              f"({data['index']['ndx_cash'].get('chg_pct')}%)")
        f = data["futures"]
        print(f"NQ globex  last {f.get('last')}  H {f.get('globex_high')}  L {f.get('globex_low')}")
        print(f"  asia   {f.get('asia_window_21_06utc')}")
        print(f"  london {f.get('london_window_06_1230utc')}")
        print(f"VXN {v['vxn_nasdaq_ivol'].get('last')}  VIX {v['vix'].get('last')}  "
              f"VIX9D {v['vix9d'].get('last')}  VVIX {v['vvix'].get('last')}  "
              f"9D/30D {v['vix9d_over_vix']} -> {v['term_read']}")
        print(f"US10y {r['us10y'].get('last')} ({r['us10y'].get('chg_pct')}%)  "
              f"DXY {r['dxy'].get('last')} ({r['dxy'].get('chg_pct')}%)")
        fr = data.get("fred") or {}
        if fr.get("key_present"):
            print(f"\nFRED ({fr.get('series_ok')} series):")
            for x in fr.get("read", []):
                print(f"  [{x['signal']:+d}] {x['text']}")
        else:
            print("\nFRED: no key set (FRED_API_KEY) — real-yield layer skipped")
        print("\nUS events next 24h:")
        for e in data["calendar"].get("upcoming_next_24h", []) or ["  (none)"]:
            print("  ", e)
        print("\nHeavyweight earnings next 5d:")
        for e in data["calendar"].get("heavyweight_earnings_next_5d", []):
            print("  ", e)
        print("\nTop headlines:")
        for src in ("cnbc", "nasdaq_24h", "mag7_24h"):
            for h in data["news"][src][:4]:
                print(f"  [{src}] {h.get('title', h)}")
