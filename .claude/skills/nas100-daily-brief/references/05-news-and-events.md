# 05 — Judging news and event gates

## Your job vs the script's
The script auto-scores only unambiguous, declarative, past-tense events. It
deliberately refuses anything with negation, a modal, a contrast clause, or an
off-topic subject — measured, keyword scoring got 8 of its top 14 wrong on those.

Everything in `NEEDS_JUDGEMENT` is yours. Handle what keywords can't:
*"Nasdaq futures CLIMB after sharp selloff"* is bullish. *"May plunge, even if
it beats"* is not an event at all.

## Reaction mapping — direction is not tone
| Print | Surprise | NAS100 | Size | Half-life |
|---|---|---|---|---|
| CPI / core CPI | Hot | **Bearish** | 150–350pt | 60–90 min, often retraced |
| CPI / core CPI | Cool | **Bullish** | 150–300pt | Holds better in a hawkish regime |
| Core PCE | either | Same sign as CPI | 80–180pt | 45 min |
| NFP | Strong | **Regime-dependent** — in a hawkish tape, strong jobs = bearish | 150–300pt | 90 min |
| Avg hourly earnings | Hot | Bearish — often the real mover inside NFP | 80–150pt | 45 min |
| ISM Services | Weak | Bearish (growth) | 80–150pt | 45 min |
| UoM 5–10y inflation expectations | Higher | Bearish — the subcomponent moves more than the headline | 80–150pt | 45 min |
| Poor 10y/30y auction | Tail | Bearish, yields jump | 60–140pt | 30 min |

**Fed:** the FOMC statement spike is noise; **the presser sets direction**, and
frequently reverses the first move. No entries until it has settled.

**Earnings:** NVDA is the single largest scheduled NAS100 event, ranking with
CPI. The session before is pinned, the session after gaps and expands. AVGO /
AMD / TSM / MU move the whole semi complex, so their index impact exceeds their
weight.

**Live themes:** semiconductor tariffs and export controls hit the most
concentrated part of the index — sharp, 150–250pt, no warning.

## Two hard rules
1. **A High-impact US event inside 90 minutes = STAND ASIDE.** Both models need
   a sweep that *fails*; a data print manufactures one that keeps going. Give
   the window, then the levels to watch after.
2. **A headline under 15 minutes old that has already moved price >0.4×ADR is
   not tradeable** on either model until new structure forms.

## The part people miss
A data print doesn't only create risk — **it creates the day's best liquidity**.
The high and low of the first 30 minutes after a Tier-0 print are among the most
reliably swept levels on the chart. Add them to the board once they exist.
