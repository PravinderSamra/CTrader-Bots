# Trade journal

Append-only log of every idea the `liquidity-inducement-phone` skill produces —
including the ones that concluded no-trade, because a day with no entry must be
distinguishable from a day that was never scanned.

- One file per month: `YYYY-MM.jsonl`, one JSON object per line.
- Schema and the writing procedure: skill reference `07-trade-journal.md`.
- Scoring: `scripts/journal_review.py` walks price forward from each idea's
  `as_of` and records whether it triggered, filled, and how it resolved.

This exists to give the strategy research something it has never had: ground
truth. Ideas here were written before the outcome was known, so they can settle
questions a replay cannot.
