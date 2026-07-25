# FTMO Instrument Universe — Equities CFD

**Researched:** 2026-07-23 (Fable 5). **Source:** FTMO's public symbols API (`https://ftmo.com/wp-json/ftmo/symbols`, the data behind [ftmo.com/en/symbols](https://ftmo.com/en/symbols/)). Machine-readable snapshot: `data/ftmo-universe.json`.
**Authority note:** this is the *published* FTMO universe. The live FTMO cTrader account's `get_symbols` (Phase 2 audit) is the final authority — symbols must match before the skill goes live, and this file gets re-verified/refreshed then.

## Headline

FTMO offers **167 instruments** total; **59 are Equities CFD**. Of those:

- **45 US-listed stocks** → the ORB scan universe (full universe, scanned every day — no sampling, no watchlist cap needed at this size)
- 1 excluded: **SPCX** ("SpaceX, Spot CFD") — synthetic pricing of a private company, no exchange, no real opening-range volume → not scannable
- **13 EU-listed stocks** (EUR-quoted, Xetra/Euronext session 07:05–15:30 UTC) → out of scope for the US ORB strategy; possible future extension with a separate 08:05 UTC London/EU scan

### The 45-stock US scan universe

AAPL, AMD, AMZN, ARM, ASML, AVGO, AZN, BA, BABA, BAC, BRK.B, CSCO, CVX, DIS, FDX, GE, GM, GME, GOOG, IBM, INTC, JNJ, JPM, KO, LMT, MCD, META, MSFT, MSTR, NFLX, NKE, NVDA, PFE, PLTR, QCOM, RACE, RTX, SBUX, SNOW, T, TSLA, V, WMT, XOM, ZM

### EU list (not scanned initially)

ADSGn (Adidas), AIRF (Air France-KLM), ALVG (Allianz), BAYGn (Bayer), BMW, DBKGn (Deutsche Bank), IBE (Iberdrola), LVMH, MBG (Mercedes), SAN (Santander), SIEGn (Siemens), TTE (TotalEnergies), VOWG_p (VW pref)

## Contract specs (uniform across the equity class)

| Spec | Value |
|---|---|
| Contract size | 1 share per unit |
| Leverage | Standard account 1 : 3.33 — **Swing account 1 : 1 (this project's account: $100k Swing → 1:1 binds)** |
| Commission | 0.004 %-type per the API (cheap; exact per-side basis to confirm in audit) |
| Price digits | 2 (SAN: 4) |
| Max trade volume | per-symbol field in the JSON |
| US session (UTC, summer) | **13:35 – 20:00** |
| EU session (UTC, summer) | 07:05 – 15:30 |

## ⚠️ Critical finding: the 13:35 UTC open

FTMO's US stock CFDs open at **13:35 UTC = 09:35 ET — five minutes after the cash open**. The CFD session starts exactly when the 5-minute opening range *ends*. Consequences:

1. **The 09:30–09:35 OR bar (price AND volume) almost certainly does not exist in the FTMO cTrader feed.** (Phase 2 audit must confirm by pulling M_5 trendbars for AAPL — but plan for absence.)
2. Therefore the scanner **must source opening-range OHLCV from an external US equity data feed** (TradingView MCP / Alpha Vantage / aktools — audit picks the most reliable 5-min source), while **cTrader/FTMO remains the execution/pricing venue** for live quotes, entry levels and (later) order placement.
3. RelVol computed from real exchange share volume is actually a **fidelity upgrade** over CFD tick-volume proxies — closer to the paper.
4. Silver lining: entries can't trigger before 09:35 anyway (the breakout order goes live after the OR completes), so the tradable mechanics are unaffected. Only the *measurement* window needs external data.
5. cTrader spot prices from 13:35Z can diverge a few cents from the ORH/ORL measured on exchange data; the report must quote both (exchange OR level + current cTrader bid/ask) so the user places orders on broker prices.

## FTMO account rules that bind the strategy

| Rule | Impact on ORB |
|---|---|
| Max daily loss 5% ($5,000 on the $100k account) | Nominal top-3 at 1% risk each = 3% worst-case day — compliant. In practice the 1:1 leverage cap (below) keeps realised risk far lower. Skill states aggregate open risk on every report. |
| Max overall loss 10% ($10,000) | Same monitoring; advisory note only (we don't place orders yet). |
| **Equities leverage 1:1 on Swing accounts** (confirmed for all 59 equities in FTMO's symbol data; Standard would be 3.33) | **The binding constraint.** Margin = 100% of notional, so total notional across open positions ≤ ~equity. The paper's 1%-risk sizing (`shares = 0.01E / 0.1ATR`, notional ≈ `0.1×E×price/ATR`) needs 3–6× equity of notional on typical mega-caps → unreachable. Realised per-trade risk under the cap ≈ `0.1×ATR/price × marginBudget`: e.g. AAPL ($220, ATR $4) ~0.18% per 1×E; TSLA ($250, ATR $12) ~0.48%; GME ($25, ATR $2) ~0.8%. Volatile, cheaper names get closest to full risk — conveniently the same names most likely to be in play. Engine sizes under a per-pick margin budget (default E/3) and reports which bound binds. |
| News-trading restriction | **Exempt — Swing account.** No ±2-min rule. Skill notes macro-event days as context only, not compliance. |
| Weekend holding ban | Exempt on Swing anyway; irrelevant — strategy is flat by 16:00 ET daily. |

## Strategic fit of this universe (honest assessment)

- **Overlap with the paper's winners:** NVDA (+309R), AMD (+184R), TSLA (+183R) are all in the paper's top-25 for the 5-minute ORB — and all in the FTMO universe. NFLX and ASML appear in the 15-minute top-25. **None of the FTMO 45 appear in the paper's 5-minute worst-25 list.** GM, INTC, NKE appear in worst lists only on the 30/60-minute variants we don't trade.
- **Mega-cap skew caveat:** the paper's biggest RVOL explosions (10–30×) come disproportionately from mid-caps with binary news (FDA, short squeezes). A 45-name mega/large-cap universe will produce fewer extreme-RVOL days and more days with **zero qualifying stocks**. The skill must be comfortable reporting "no Stocks in Play today — no trade" — that is correct behaviour, not failure. Names like GME, MSTR, PLTR, SNOW, ZM, ARM, TSLA remain capable of true in-play days.
- The universe filters (price > $5, liquidity, ATR > $0.50) still run daily: nearly all 45 pass price/liquidity permanently, but ATR > $0.50 genuinely filters low-priced/low-vol names (T, PFE, SAN-style) on quiet regimes — keep it.
- Small universe = the full-universe requirement is trivially satisfied: **all 45 stocks are evaluated every single day, no shortlisting, no sampling.**

## Sources

- [FTMO Symbols page](https://ftmo.com/en/symbols/) / public symbols API (snapshot in `data/ftmo-universe.json`)
- [FTMO FAQ — Which instruments can I trade?](https://ftmo.com/en/faq/which-instruments-can-i-trade-and-what-strategies-am-i-allowed-to-use/)
- [FTMO FAQ — Can I trade news?](https://ftmo.com/en/faq/can-i-trade-news/)
