# 04 — Entries, Stops, Targets & Management

The where/when of execution. Assumes the setup has passed the six gates of
SKILL.md §2 and the bias/timing read of reference 03. Provenance: doc 03
§1–§6, doc 04 §1–§4, doc 09 §1.4/§2.5/§5/§7, Playbook §Execution/§Management.

---

## A. The entry trigger

### A.1 Enter at the stab, the moment the trap completes

> "As soon as… once this low right here is taken, where the liquidity is, you
> enter your buy position." (doc 03 §2.1)

- The trigger is the sweep of the **identified, confirmed** pool — the last
  unswept level at the extreme of the buildup ("trail your eyes all the way to
  the extreme", doc 02 §E) — into/toward the LB.
- **Execute after liquidity is taken, not before** (Playbook §Execution).
  Entry timing before the sweep = trading inside the trap zone = rule-break.
- **Don't over-refine.** No hunting for an imbalance inside the low, no waiting
  for the very top/bottom: "typically when people overrefine you're going to
  start missing entries" (doc 03 §2.1); "direction and bias is what pays the
  profits" (doc 03 §2.2). It can feel like catching a falling knife; it is per
  the system (doc 10 P6).

### A.2 Fill styles (three, economically equivalent — doc 05 §2.5)

| Style | When | Mechanics |
|---|---|---|
| **Market on confirmation** | Futures/gold intraday, at the screen | Market order as the level is stabbed and rejection shows (Playbook: "use market execution once the high/low is taken and the trap is confirmed") |
| **Resting limit in the LB / imbalance** | FX / HTF setups, incl. overnight | Limit parked at the swept level or inside the LB's imbalance, stop and target pre-set; "phones away… I'm going to be asleep" (doc 09 §1.4) |
| **Zone fill** | When the stab travels | Anywhere in the band **[swept level → far side of the LB]** is a valid fill — the band is fractal, same rule at 1H and 1m (doc 03 §1.5 visual) |

Pre-frame every trade **before** the trigger: entry, stop, target known in
advance — "I've already done all the hard work before I actually click the
button" (doc 09 §1.4). Set alerts at the arming level rather than staring.

### A.3 The LTF confirmation drop-down (RR rescue)

If the execution-TF LB makes the stop too wide ("the RR is shot… I just don't
take those trades"): drop to the lower timeframe and wait for the **same model
to print fractally there** — its own buildup, its own last-level sweep into a
LTF LB — and enter on that stab with the tight LTF stop, same HTF target
(doc 03 §2.3; gold 1m example: stop shrank ~8×, RR ~1.7 → ~1:12). This is the
*only* sanctioned refinement — a conditional tool, not the standard
(Playbook reconciliation note). Same fallback applies when **no LB exists at
all** (doc 09 §7 item 1).

### A.4 Timing qualifiers on the trigger (intraday futures/gold)

- Inside the **session window only** (NY; ≈ stock open, sometimes from ~08:00).
  Setup outside the window → no trade (reference 03 §B.1).
- **10:00 a.m. H4 roll** and stock open are the preferred trigger times; the
  first NY move is presumed a trap to be faded once complete (reference 03
  §B.2).
- **Never enter before news; wait ~2–4 min after** (doc 03 §2.4).
- Candle-close confirmation is for *adds*, not the base entry — except the one
  case of perfect multi-TF time confluence (doc 09 §3.5).
- Expect the extreme to be stabbed **more than once**; a post-entry deeper stab
  into the LB does not invalidate (doc 03 §6).

## B. Stop placement

### B.1 Just beyond the LB — "always cover the last high/low"

> "Stop covers this high always. I don't want to get greedy." (doc 03 §3.1)
> "Stop loss is going to go just above our liquidity block. That will never
> change." (doc 09 §2.5)

- **Structural, never a fixed pip/tick count, never inside the swept range.**
  Anchor = behind the LB / the left-hand low(high) the sweep tapped
  (Playbook §Execution: "always cover the last high/low with your stop").
- Anchor choice is case-by-case — sometimes the LB's far side, sometimes a
  deeper left-hand extreme — but always behind structure that itself swept
  liquidity (doc 03 §3.1 visual nuance).
- If price trades beyond it, the idea is **invalid** — that is the
  invalidation line you quote in the output.

### B.2 Instrument buffer

- **Futures:** a tick or two beyond the level is fine (centralized feed)
  (doc 03 §3.2).
- **CFD/FX (incl. XAUUSD CFD): add spread breathing room** — observed ≈ $1–3
  beyond the wick on gold (~0.01–0.07% of price, scaling with the anchor's
  timeframe); "you need to be opening up your stop loss a little bit more…
  accounting for spread" (doc 03 §3.2; doc 09 §1.4).

## C. Targets

### C.1 Layered targets at real liquidity only

- **Target = the opposing confirmed pool. Never a fixed R number**
  (doc 03 §4.1; reference 01 §8).
- **Internal partial → external full:** nearest opposing internal pool
  (engineered highs/lows, structural points, PDH/PDL, prior H4 high) is the
  partial point; the HTF external pool finishes the trade (doc 03 §4.2).
- Partial only where the RR at that level justifies paying yourself
  (≈ **1:5+**); otherwise risk-off only (doc 09 §7 item 3). When partialing:
  small — ~20–25%, majority held to target (doc 04 §3).
- Each internal pool consumed on the way is also a **management event** (see D).

### C.2 The RR filter

- **Floor ≈ 1:3 minimum** to the analyzed target, computed off the *structural*
  stop (doc 03 §4.3). Fails the floor → skip or LTF drop-down (A.3).
- Skip small absolute moves regardless of RR (doc 03 §4.3).
- Quote `rr_estimate` honestly in the output — to the partial and to the full
  target.

## D. Trade management

Execution order, long case (mirror for shorts):

1. **Initial stop** per §B. Don't touch it out of fear; don't let mid-trade
   candles shake you out (doc 04 §2.4–2.5).
2. **Move the stop only after price moves in your favour** and forms a higher
   low that "should not be revisited" — roll below it, cutting risk
   (Playbook §Management; doc 04 §2.2).
3. **Risk-off / break-even when the first opposing pool is consumed.** The
   reconciliation (default to practice — full table in reference 01 §10):
   - **Practice (V2/V3/IET, Marco's demonstrated operation):** first opposing
     high (long) taken → roll to BE; "once we took out this internal high, I
     went risk-free." Partial decided separately by RR-at-that-level (≥ ~1:5 →
     partial, else BE only).
   - **Playbook (stricter wording):** "No break-even stops unless partials have
     been taken" — treat as the guard against premature/fear BE, not a ban.
4. **Optional trail-to-new-LB (futures urgency):** trail behind freshly-minted
   LBs — "This LB should protect my SL. If it runs it, I don't want to be in
   the trade no more" (doc 09 §7 item 4).
5. **Hold to the analyzed target.** "Don't cut trades early unless your system
   says so" (Playbook §Management). If it doesn't reach target, "there's no
   profits and it is what it is" — no forcing (doc 04 §8). Intraday: be out
   before NY lunch when possible (doc 04 §5).

### D.1 Adds and stacking

- **Scale-ins (within one trade):** only below a fresh local mini-sweep, each
  with its own independent invalidation; a 5m close in your favour gates the
  add (doc 04 §4).
- **Stacking (separate sequential trades):** allowed while the shared target
  survives — "if our target is left intact… we have another opportunity" —
  each stack entry must independently complete the full model (own sweep, own
  LB). The stack dies when the target is consumed (doc 09 §5).

## E. With-bias vs counter-bias — always label which

- **With-bias** (aligned with the HTF draw and the sequencing): higher
  conviction, full framework applies. This is the default trade.
- **Counter-bias / short-term** (against the sequence, e.g. fading toward an
  internal pool while the HTF draw points the other way): "automatically lower
  probability"; licensed **only with a session-time confluence** (stock open /
  10:00 H4 roll), typically targeting internal liquidity only, managed faster
  (doc 09 §3.3, §4.2).
- Every setup in the output carries `alignment: "with_bias" | "counter_bias"`
  (schema, reference 02) and the commentary says which one it is and why
  (SKILL.md §6).

## F. Pre-trigger checklist (condensed)

Before quoting a setup as armed:

- [ ] Confirmed target pool intact in the trade direction (gate 1).
- [ ] The identified near-side pool actually swept — trap complete (gate 2).
- [ ] LB behind the entry; stop covers the last high/low + spread buffer
      (gate 3).
- [ ] Bias lockout satisfied, or a stated time qualifier for the counter-bias
      exception (gate 4).
- [ ] Inside the session window; no imminent news; not lunch (gate 5).
- [ ] Not no-man's-land (gate 6).
- [ ] RR ≥ ~1:3 to the analyzed target off the structural stop.
- [ ] Entry, stop, both targets, and invalidation written down **before** the
      trigger.
