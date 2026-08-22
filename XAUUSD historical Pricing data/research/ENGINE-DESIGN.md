# Multi-Strategy Scalping Engine — Research & Design Document

**Goal:** one always-on bot that watches the market all day for a library of recurring, well-defined events, and trades each with its own identification → confirmation → execution → exit logic, under a shared risk book.

**Method:** before designing anything, every candidate module was backtested on the 5-year 1-minute dataset (scripts `10_engine_modules.py`, `11_orb_trail.py`, plus everything from scripts 03–09). Only modules with demonstrated positive expectancy net of $0.40/oz costs earn a slot. This document records both the survivors and the failures — the failures are design constraints, not footnotes.

---

## Part 1 — The research: what the bot should and should NOT monitor for

### 1.1 The two modules you proposed — tested honestly

**Trend following ("detect trend start, confirm, enter, ratchet the stop up until stopped out"):**
Implemented exactly as described: Donchian(24) 5m breakout as ignition, expansion-bar confirmation variant, chandelier trail (highest close − k×ATR) ratcheting behind price. Result across 5 variants, 12,224 trades:

| Variant | Trades | avgR | Verdict |
|---|---|---|---|
| All-day, 2.5 ATR trail | 12,224 | **−0.127** | loses every year |
| NY-only, 2.5 ATR trail | 3,749 | −0.091 | loses every year |
| NY-only, tight 1.5 trail | 4,742 | −0.137 | worse (tighter = worse, again) |
| NY-only, wide 3.0 trail | 3,464 | −0.075 | loses every year |
| NY-only + expansion confirmation | 2,319 | −0.073 | loses 5 of 6 years |

**Mean reversion ("detect when a trend has reversed, enter that direction"):**
Two implementations: (a) enter opposite after a ≥1-ATR trend gets trailed out — 949 trades, **−0.152R**; (b) London RSI(2) extreme fade — 9,728 trades, **−0.270R**, negative every year.

**Why they fail (and always will here):** the price process measures Hurst = 0.497 with runs-test continuation at 47–49% (see `MATH-PHYSICS-VIEW.md`). "A trend has begun" carries **zero** information about the next bars, so any module keyed off *inferred market state* pays costs to trade noise. This is the single most important research finding for the engine: **the bot must monitor for EVENTS (scheduled times, structural levels, volatility shocks), not for STATES (trending / reversing / overbought).**

**The ratchet-stop experiment:** applied your trailing idea to the one breakout module that does work (NY ORB): static far-side stop = +0.083R; 2.5×ATR ratchet = +0.018R; 4×ATR ratchet = +0.059R. **Ratcheting gave back most of the edge** — in a fat-tailed market the trail keeps getting clipped by noise right before the payoff move. Exits must be structural stop + fixed time, full stop.

### 1.2 What the bot SHOULD monitor for — the validated event library

| # | Event | Edge (net) | Freq | Evidence |
|---|---|---|---|---|
| E1 | **Clock: 20:00 UTC approach** (overnight drift window) | +2.3–2.8% ATR/trade, Sharpe ~1.6–1.9 | 4/wk | script 04/05 |
| E2 | **13:30 UTC opening range forms** (NY ORB) | +0.083 R-on-risk, ~+1.7R/month | 5/wk | script 03/05/11 |
| E3 | **4σ jump 12:00–15:30 UTC** (aftershock/expansion) | +0.057R | 3–4/wk | script 09 |
| E4 | **NY break of a London-respected Asia range + pullback** | +0.125R | 0.7/wk | script 07 |
| E5 | **PDH/PDL proximity** (target/partial logic, not entries) | 85.6% touch rate | daily | script 02 |
| E6 | **Vol regime update** (ATR forecast, R²=0.58) | sizing, not signal | daily | script 08 |

Also investigated and **rejected** for the engine: VWAP-deviation fades in Asia and London (−0.20 to −0.45R despite a valid mean-reversion diagnostic), streak/momentum signals (no signal at any k), round-number logic (no effect), weekend gap fade (only untradeably small gaps fill), compression filters (folk theorem false), midday continuation chases (−0.04R longs), London-break pullbacks (−0.09R, 923 trades).

---

## Part 2 — Engine design

### 2.0 In simple terms first

Think of the bot as a **shop with four counters that open at different hours**, run by one cashier (the risk engine):

- Late evening, one counter quietly buys and holds until ~2am because gold has drifted up in that window every year for five years (Asian physical demand).
- Early afternoon, the second counter marks the 1:30–2:00pm UK opening range, puts a pending order on each side, and rides whichever breaks — no profit cap, close at 8pm.
- If a news bomb hits (a 4σ one-minute candle), the third counter waits five minutes, brackets the price, and rides the aftershock — because jumps come in clusters.
- On the rare day the overnight range survives the whole London morning and only breaks in the NY session, the fourth counter buys the pullback to the broken level.
- The cashier gives every counter the same £-risk per trade (scaled daily to the vol forecast), refuses to let two counters bet the same move twice, shuts the shop for the day if it's down a fixed amount, and closes any counter whose last 50 trades have gone flat.

Nothing in the engine predicts direction. Every module harvests either a **standing flow** (E1), **scheduled expansion** (E2/E3), or **stored structural energy** (E4), and every exit is either a structural stop or a clock.

### 2.1 Architecture (four layers)

```
┌──────────────────────────────────────────────────────────┐
│ L0 MARKET STATE (computed continuously, no orders)       │
│   clock/session · ATR20 & range forecast · Asia H/L      │
│   PDH/PDL · ORB H/L · rolling 1m σ · live spread         │
├──────────────────────────────────────────────────────────┤
│ L1 DETECTORS (event → signal)   E1 E2 E3 E4              │
├──────────────────────────────────────────────────────────┤
│ L2 RISK ENGINE (signal → order or veto)                  │
│   ATR sizing · overlap governor · daily/weekly stops     │
├──────────────────────────────────────────────────────────┤
│ L3 EXECUTION (order → fills)  spread guard · OCO · flat  │
│    timers · no take-profits anywhere                     │
└──────────────────────────────────────────────────────────┘
```

### 2.2 Module specs (identification / confirmation / execution / exit)

**E1 — Session Carry** *(clock event)*
- **Identify:** time = 19:55 UTC, Mon–Thu.
- **Confirm:** none needed (optionally: close > SMA20 daily = higher quality, fewer trades). Skip if account swap-long cost > $0.5/oz/night.
- **Execute:** market buy 20:00 UTC (or limit at 22:00 reopen to dodge reopen spread).
- **Exit:** market close 02:00 UTC. Disaster stop 0.5×ATR20 below entry. No TP.

**E2 — NY ORB** *(structural breakout event)*
- **Identify:** 14:00 UTC — opening range = H/L of 13:30–14:00.
- **Confirm:** range sanity: skip if OR width > 0.5×ATR20 (blown-out open) or < 0.04×ATR20 (dead tape / spread-dominated).
- **Execute:** OCO stop orders at OR-high and OR-low; first fill cancels the other.
- **Exit:** static stop = far side of the OR. Time exit 20:00 UTC. **No trail, no TP** (both tested worse).

**E3 — Aftershock** *(volatility shock event)*
- **Identify:** 1m |return| > 4× rolling-1-day σ, between 12:00–15:30 UTC, first jump of the day only.
- **Confirm:** wait 5 minutes (lets the spread normalise and the first reaction print). Skip if spread still > 2× normal.
- **Execute:** OCO brackets at ±0.15×ATR20 around post-jump price; 60-min arm window.
- **Exit:** stop = far bracket (risk 0.30×ATR20). Time exit 4h after fill or 20:00 UTC. No TP.

**E4 — Asia-Break Continuation** *(level event, rare)*
- **Identify:** Asia range (22:00–06:59) with **no 1m close outside it through 07:00–11:59**; then first 1m close beyond a side 12:00–15:59 UTC.
- **Confirm:** pullback: price returns to the broken level within 120 min.
- **Execute:** limit at the level.
- **Exit:** stop = Asia range mid. Time exit 20:55 UTC. No TP. (Optional: shorts at half size — long edge +0.28R vs short −0.06R in the bull sample.)

### 2.3 Risk engine rules

1. **Sizing:** every order risks the same fraction f of equity: `lots = f × equity / (stop_distance × $per_lot_per_$)`. Forecast-scaled: stop distances are already ATR-derived, which self-scales — the 6× ATR regime change 2021→2026 is absorbed automatically.
2. **Per-module risk:** E1 0.5f · E2 1.0f · E3 0.5f · E4 0.75f (weights ∝ in-sample Sharpe, capped).
3. **Overlap governor:** E2 and E3 frequently fire on the same NY move. If both are live in the same direction, the second signal is cut to half size; opposite directions = the second is vetoed. E1/E4 never overlap the others in time.
4. **Daily stop:** −2f total → flatten everything, no new signals until next dealing day.
5. **Module health:** rolling 50-trade expectancy per module; below 0 → module auto-disabled until manual review (re-run its research script on fresh data).
6. **Spread guard (L3):** any order is skipped if live spread > 2× its 30-day median for that hour — protects E3 especially, and the 22:00 reopen.

### 2.4 Expected performance (in-sample, for calibration not promises)

Per month at f = 1% risk-unit: E1 ≈ +0.8R · E2 ≈ +1.7R · E3 ≈ +0.9R · E4 ≈ +0.4R → **combined ≈ +3.5–4.5R/month** before overlap discounts, with sleeves active at different hours so daily P&L variance stays near the largest single sleeve. Monte Carlo on the sleeves individually puts a realistic combined max drawdown around **8–12R** on a bad quarter. At 1% risk that's roughly +40%/year against a ~10% max drawdown *if the future resembles the sample* — halve any expectation for live slippage/regime decay.

### 2.5 Build roadmap

1. **Phase 1 (validation live-shadow):** implement L0+L1 as signal-only (log signals, no orders) on the cTrader demo via the MCP integration or a cBot; run 4 weeks; compare signal stream to backtest frequency/quality.
2. **Phase 2 (paper execution):** enable L2/L3 on demo. Measure realised spread/slippage per module vs the $0.40 model; recalibrate.
3. **Phase 3 (small live):** f = 0.25% for one month; scale to target only after 100 live trades match backtest within tolerance.
4. **Quarterly:** re-run scripts 03–11 on refreshed data (fetch runbook in the parent folder); apply rule 5 kill criteria.

### 2.6 Design laws (learned from this dataset — do not violate)

1. Monitor **events**, not states. Trend/reversal/overbought detectors are noise-costs here (Part 1.1).
2. **Never tighten exits adaptively.** Structural stop + clock exit only. Every trail/TP variant tested reduced or destroyed edge.
3. Wide structural stops beat tight stops — the 0.33-ATR-stop experiment flipped a winning system negative.
4. All sizing off forecast ATR, refreshed daily.
5. London is for marking levels, not trading. Every London-entry module tested was negative.
6. Judge modules on 50-trade blocks; judge the engine monthly, never daily.
