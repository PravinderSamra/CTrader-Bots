# Stage 3 — the edge does not survive out of sample

Run 2026-11-16. Dataset extended from 274 to **514 aligned sessions**
(17 Nov 2024 → 15 Nov 2026, two full years). ES = `US500`, VIX = `VIX`.
Transcription validated: 0 OHLC-consistency failures across 1,030 bars.

## The split that matters

Everything up to 2025-12-10 is where the effect was **found** — in-sample by
construction. Everything after is genuine out-of-sample.

### 3R target

| | n | win% | avg R |
|---|---|---|---|
| **IN-SAMPLE (to 2025-12-10)** | | | |
| A — reclaim alone | 68 | 38.2% | +0.44 |
| B — + VIX weak | 13 | 61.5% | **+1.46** |
| B' — + VIX confirmed | 55 | 32.7% | +0.20 |
| **OUT-OF-SAMPLE (after)** | | | |
| A — reclaim alone | 67 | 35.8% | +0.43 |
| B — + VIX weak | 14 | **28.6%** | **+0.14** |
| B' — + VIX confirmed | 53 | 37.7% | +0.51 |
| **COMBINED (2 years)** | | | |
| A — reclaim alone | 135 | 37.0% | +0.44 |
| B — + VIX weak | 27 | 44.4% | +0.78 |
| B' — + VIX confirmed | 108 | 35.2% | +0.35 |

**Out of sample the VIX filter did WORSE than no filter at all** — 28.6%
against 37.7%, +0.14R against +0.51R. Fisher one-sided p = 0.828, i.e. the
difference runs the *opposite* way to the hypothesis.

Combined over two years: p = 0.250. **Not significant.**

## A second small-sample artefact, found by the extension

The last event in the stage-1 window (2025-12-10) ran off the end of the data
and was scored **+3.83R** because the walk-forward had nowhere left to go.
With the extra year it resolves properly: price traded to 6801.20 the very
next session, **below the 6813.10 stop — a straight −1R.**

That alone moves the in-sample arm from 9/13 to 8/13 before any sequencing
correction. Two independent artefacts (this, and the sequencing failure in
stage 2a) each cost one trade out of thirteen, which is what n=13 buys you.

## Verdict

**The VIX leg is not a tradeable edge.** It is not established at 2R, at 3R,
in sample after correction, or out of sample — where it was actively harmful.
The original 69% / +1.83R was small-sample noise, exactly as the p=0.056 after
correction warned.

Nothing should be built on it. Recorded, closed.

## What DID survive — and it is the simple thing

**Arm A, the plain previous-day-low reclaim, with no VIX and no NQ:**

| | n | win% | avg R |
|---|---|---|---|
| in-sample | 68 | 38.2% | +0.44 |
| out-of-sample | 67 | 35.8% | +0.43 |
| **combined** | **135** | **37.0%** | **+0.44** |

**+0.44R in sample and +0.43R out of sample.** That is as stable as this kind
of test gets, on ten times the sample of the arm we were chasing, and it fires
~66 times a year.

The irony is clean: every elaborate leg of the source's setup failed — the NQ
confluence fired once a year and scored below the null, the VIX filter failed
out of sample — while the plain mechanical bit underneath them held.

## Next, if this is taken further

Arm A is now the candidate, not the VIX setup. Before it could be a bot:

1. Sequence-check arm A on intraday bars (the stage 2a bias applies to it too,
   and it will shave the number).
2. Extend further back — 2021–2024 would take it past 300 events.
3. Weekend-gap exposure (still outstanding).
4. Entry cushion and target, tested rather than inherited.

