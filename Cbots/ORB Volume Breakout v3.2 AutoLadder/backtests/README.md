# ORB v3.2 backtests — 1 November 2026

Four runs, all cTrader server tick data, US100.cash m1, commission 0, the
`.cbotset` in the folder above.

The two full-window logs are gzipped (3.9 MB each raw). `parse_orb_log.py`
reads any of them:

```
python3 parse_orb_log.py "2026-10 October from 96504 (live-comparison run).log"
gzip -dc "...Size 5.log.gz" > /tmp/s5.log && python3 parse_orb_log.py /tmp/s5.log
```

It keys on the bot's own `TRADE ENTERED` / `POSITION CLOSED` lines (this bot
prints no `H|` history block) and on the daily `L|` risk-ladder line.

## Run 1 — October 2026 against live

Started at **$96,504**, the account's real balance on 1 October, because the
risk ladder is balance-driven: starting at $100,000 picks the $650 rung where
live was on $400, and the position sizes would not have matched.

| | |
|---|---|
| backtest | **−2,055.20** |
| live (from the account History) | **−1,996.99** |
| gap | **$58**, 2.9% |
| mean per-day difference, 9 shared days | **3.9 points** |

**The backtest lost money in October too, slightly more than live did.** No
execution leak, no slippage problem. This is the live-execution validation the
strategy document said was still outstanding, and it passes.

Three days do not line up: 01/10 the backtest traded and live did not, 15/10
live traded and the backtest did not, 16/10 the backtest ran two legs to live's
one. They roughly cancel. Unexplained, worth a look, not a leak.

The first run (from $100,000) is kept for comparison: identical pips, different
position sizes, net −2,228.78.

## Runs 2 and 3 — full window, Size 5 against Size 4

1 Jan 2021 – 30 Oct 2026, $100,000 start, compounding. One parameter differs:
`AddSizeMultiplier` 5.0 vs 4.0. Verified on the first trade of the run —
2021-01-04 adds vol 11.01 against 8.81, a ratio of exactly 5/4.

| | Size 5 (live) | Size 4 |
|---|---|---|
| ending balance | $393,935.57 | $372,605.75 |
| return | +294% | +273% |
| trades closed | 1,013 | 1,023 |
| legs profitable | 43% | 43% |
| deepest balance drawdown | $34,771 | $31,297 |
| **return ÷ drawdown** | **8.45** | **8.71** |

Size 5 earns **7.8% more profit for 11.1% more drawdown**, so risk-adjusted it
is slightly behind Size 4.

Neither path ever dipped below the $100,000 start, so the FTMO floor was never
approached — but that is one path, and it opened with a winning stretch. The
one-pager's resampled floor odds (0.6% at Size 4, 1.2% at Size 5) remain the
better estimate, and both were computed on $10,000 of headroom.

"43% of legs profitable" and the one-pager's "35–36% win rate" are not in
conflict: this counts legs, the one-pager counts days.
