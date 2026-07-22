# 09 — Liquidity Inducement and Daily Bias (Inter Equity Trading channel)

Deep-dive into the material the Inter Equity Trading (IET) channel adds beyond the three original videos: inducement mechanics, liquidity blocks, the daily-bias method, both-sides ("ping-pong") range trading, and stacking entries.

Citation format: `(IET YYYY-MM-DD "short title" [MM:SS])` → the transcript file in `../01-transcripts/inter-equity-channel/`. Official playbook citations: `(Playbook §…)` → `../04-official-playbook/marco-trades-liquidity-playbook.md`.

## 0. Source key

Twenty Inter Equity Trading (IET) videos, 2026-01-31 → 2026-07-21, all teaching the same model as files 01–04 (the V3 walkthrough of those files is an earlier video from this same channel). Timestamps in citations are **video time** taken from the inline `<hh:mm:ss>` caption tags in the transcript files — the `[MM:SS]` line prefixes in the raw transcripts are unreliable (a prefix of `[00:01]` can cover content spoken at 6:00+); match a citation by searching the inline tags, not the prefixes.

| Cite key (date + short title) | File | What it adds |
|---|---|---|
| 2026-01-31 "Training The Eyes 12" | `2026-01-31_training-the-eyes-ep--12.md` | GBPUSD daily-TF recognition drill |
| 2026-02-03 "Profitable 2026" | `2026-02-03_how-to-become-profitable--2026.md` | Process/psychology + system recap |
| 2026-02-10 "Simple Strategy" | `2026-02-10_the-simple-trading-strategy-that-actually-works.md` | The strategy end-to-end restated |
| 2026-02-17 "Training The Eyes 13" | `2026-02-17_training-the-eyes-ep--13.md` | Recognition drill |
| 2026-02-24 "$6,600 UJ" | `2026-02-24_-6-600-liquidity-inducement-breakdown.md` | USDJPY short; LB entry discipline; stop-rolling warnings |
| 2026-03-03 "All You Need" | `2026-03-03_liquidity-inducement-trading-is-all-you-need.md` | AUDUSD; alert/limit workflow; imbalance-as-LB |
| 2026-03-10 "Liquidity Blocks" | `2026-03-10_liquidity-inducement-entries--liquidity-blocks.md` | The definitive LB lecture (diagram + chart reps) |
| 2026-03-17 "$10k in 4 min" | `2026-03-17_-10-000-liquidity-inducement-trade-in-4-minutes.md` | Gold M1 short; pre-framing entry/stop/target |
| 2026-03-24 "Sniper Entries" | `2026-03-24_the-only-entry-model-you-need--sniper-entries.md` | The 4-candle entry model |
| 2026-04-07 "Why You Can't Trade" | `2026-04-07_this-is-why-you-can-t-trade--must-watch.md` | Failure modes |
| 2026-04-14 "Step By Step" | `2026-04-14_the-simplest-liquidity-inducement-breakdown--step-by-step.md` | EURUSD daily→4H→1H→15m top-down; 1:21 |
| 2026-04-21 "Masterclass 3" | `2026-04-21_liquidity-inducement-masterclass-ep--3.md` | NQ; full inducement bookkeeping; $500K Apex claim |
| 2026-04-28 "Ping Pong" | `2026-04-28_using-liquidity-inducement-to-trade-both-sides--ping-pong.md` | Both-sides day; 10:00 a.m. rule |
| 2026-05-05 "Stacking Entries" | `2026-05-05_stacking-entries-using-liquidity-inducement--x2-profits.md` | USDCAD; the target-intact stacking rule |
| 2026-05-13 "Advanced Gold" | `2026-05-13_advanced-liquidity-concepts-on-gold.md` | "No man's land" range doctrine; BE-at-first-pool |
| 2026-06-09 "Everything Liquidity" | `2026-06-09_this-is-everything-you-need-to-know-about-liquidity.md` | Consolidated liquidity lecture |
| 2026-06-30 "Live Gold $9k" | `2026-06-30_live-trading-gold---9-000.md` | Live execution and management |
| 2026-07-07 "Liquidity Logic" | `2026-07-07_the-liquidity-logic-you-need-to-know--precision.md` | Precision logic |
| 2026-07-14 "You Don't Know Liquidity" | `2026-07-14_you-don-t-know-liquidity-until-you-watch-this.md` | Longest teaching video in corpus |
| 2026-07-21 "Correct Liquidity" | `2026-07-21_how-to-spot-the-correct-liquidity--sniper.md` | Which highs/lows to pick |

**Note on the daily-bias sources:** the corpus contains no video literally titled "Finding the Daily Bias ONLY Using Liquidity" or "The Daily Bias SIMPLIFIED"; the phrase "daily bias" does not appear verbatim in any transcript. The daily-bias method in §3 is assembled from the explicit bias/direction teaching spread across the corpus (especially 2026-01-31, 2026-02-10, 2026-05-13, 2026-06-09, 2026-07-14) — each claim is cited to where it is actually said.

## 1. Inducement mechanics — the induce → trap → enter grammar

The IET channel's core loop, stated more explicitly and more often than in V1–V3. Everything is organized around the **intention (purpose) of each move**: "the whole exercise... is understanding basically the why, the intentions behind all these moves" (IET 2026-04-21 "Masterclass 3" [00:42]).

### 1.1 The three-step grammar (sell-side version; buys are the mirror)

1. **Induce.** A sweep of an *internal* low ("old lows", "structural point") whose function is to pull sellers into the market: "when we take out these old lows, this induces sellers, and then price returns back into these levels... sells back off" (IET 2026-04-21 "Masterclass 3" [02:22]); "we take out this structural point inducing sellers... which tells me even more liquidity above this high" (IET 2026-02-24 "$6,600 UJ" [06:24]). Retail reads the sweep as a BOS: "they are going to view this to be a BOS. This level is going to be a trap for them" (IET 2026-03-10 "Liquidity Blocks" [01:12]). Every induced participant deposits stops on the far side — the sweep *manufactures the next pool*: repeated respects of the overhead high while lows keep getting taken = "we are simply just building liquidity above here" (IET 2026-04-21 "Masterclass 3" [02:42]–[03:02]).
2. **Trap.** Price then runs the level where the induced participants live — for shorts, it stabs the high their liquidity sits above: "in order for me to sell, I need to see sellers trapped... as soon as price stabs out this high, then I'm interested in selling" (IET 2026-04-21 "Masterclass 3" [06:04]–[06:24]). "We're trying to short the market here. Therefore, we're not going to short *with* the sellers. We want to wait for the sellers to get taken out of the market. AKA, you can call it a trap move, a liquidity run, a false run, whatever you want to call it" (IET 2026-03-17 "$10k in 4 min" [03:04]).
3. **Enter.** Entry fires the moment the trap completes — at the stab, no over-refinement: "as soon as we stab out this high, entries are taken just like this... I don't need to get greedy. I don't need the top of the imbalance or the very extreme, the very top, no. I just want to enter as soon as that liquidity is taken" (IET 2026-04-21 "Masterclass 3" [08:04]–[08:24]). Stop above the liquidity block, targets at the opposing engineered pools (§2, §5). This **confirms** file 03 §2.1 verbatim in a fourth+ independent set of recordings.

The post-trap trade thesis is always stated as a two-sided bookkeeping fact, not a prediction: "we get that trap move up to induce the buyers, and then we get the actual move back down to get rid of all the buyers in the market. So, sellers trapped, hunting all the buyer liquidity" (IET 2026-04-21 "Masterclass 3" [11:04]–[11:24]); "buyers stepping in here, pushing price higher, we trap those early sellers, boom, now we're taking advantage of these moves back down into the liquidity" (IET 2026-03-03 "All You Need" [10:34]).

### 1.2 Inducement vs a plain sweep

The channel is explicit that a sweep **by itself is nothing** — what matters is which role the sweep plays in the grammar:

- **An inducing sweep** takes an *internal* level in the direction of the (false) move, with a confirmed pool still intact beyond it. Its product is participants + their stops: "stab out internal lows... once we take out these internal lows, we induce sellers" (IET 2026-04-28 "Ping Pong" [04:02]). You *want* to see it but must not trade it: "this is not moves we want to be involved in, guys... However, you want to see it occur because this is now a confluence for us to push higher" (IET 2026-01-31 "Training The Eyes 12" [04:27]–[04:38] inline tags).
- **A trapping sweep** takes the level where induced stops rest — this one is the entry trigger (§1.1 step 2/3).
- **A sweep with no grammar around it is a pattern, and patterns are forbidden:** "just because we took out this high, does not mean immediately we have to look for sells back to the downside. No, that's called patterns and we're not trading patterns, we're looking for logic" (IET 2026-04-21 "Masterclass 3" [05:43]). And even a correctly-sequenced trap is untradeable without a stop anchor: "we're not just selling above highs, we're not just buying below lows. No, we need to make sure there's what? A liquidity block. This provides us our actual entry" (IET 2026-03-17 "$10k in 4 min" [03:44]).

This resolves the distinction files 01–03 imply but never state as a rule-pair: **inducement = sweep that *creates* a pool (mark it, don't trade it); trap = sweep that *consumes* the pool created by a prior inducement (trade it, immediately)**. The discriminator is whether confirmed early participants exist on the swept side.

### 1.3 The bookkeeping habit: mark the inducement, inherit the trap zone

Each inducement is annotated the moment it happens, because it defines where the *next* wave of doomed entries will occur: "since we have induced them, where is there going to be traps? All of these areas. Buyers will look to get in here. We understand the liquidity is below here... once you identify that level of liquidity aka early buyers, you want to wait for this low to get taken" (IET 2026-04-14 "Step By Step" [04:33]–[05:14]). Reactions inside those zones are pre-classified: "any bullish reactions in these levels, deem them to be false and they should be a trap, because we've just induced buyers and trapped sellers" (IET 2026-04-21 "Masterclass 3" [10:04]–[10:24]) — confirming file 01 §6 and extending it with the *copy-paste annotation* workflow ("I can just copy and paste this exact same annotation. Drag it over. We take out another low, which tells us sellers have been induced again", IET 2026-03-03 "All You Need" [06:32]).

### 1.4 Execution plumbing around the grammar (new operational detail)

- **Alerts at the arming level, then hands off:** "all I did was I set an alert here... my phone got buzzed when this high got taken out" (IET 2026-03-03 "All You Need" [04:48]–[05:28]); trades are framed *before* trigger: "I know where I'm entering, I know where I'm having my stop loss, and I know where I'm targeting even before I take the trade... I've already done all the hard work before I actually click the button. Because once you click that button, emotions are heightened" (IET 2026-03-17 "$10k in 4 min" [05:04]–[05:24]).
- **Resting limits inside the LB/imbalance for overnight forex setups:** "limit was set... right in the imbalance. I wanted to keep it as precise as possible. 2.9 pips to the high... you need to be opening up your stop loss a little bit more... accounting for spread" (IET 2026-03-03 "All You Need" [07:12]–[07:32]); "once price did this, all I did was set a limit... Stop goes above the high. Let's open this up though for spread" (IET 2026-05-05 "Stacking Entries" [03:12]). Confirms file 03 §2.1's passive-limit variant and file 03 §3.2's CFD breathing-room rule, and adds the sleep-through workflow: "phones away... I have a stop loss set and I have a target set... I'm going to be asleep" (IET 2026-03-03 "All You Need" [08:32]).
- **Futures session discipline:** "you guys all know me that I only trade futures in New York session. It could be sometimes around 8:00 a.m.... but mainly it's after stock open" (IET 2026-04-21 "Masterclass 3" [04:23]–[04:43]) — same NY-window regime as V1, with forex limit orders as the session-agnostic exception (as in V2).

## 2. Liquidity blocks as taught by IET

## 3. The daily-bias method — deriving intraday bias from liquidity only

## 4. Both-sides / ping-pong range trading

## 5. Stacking / scaling entries

## 6. Confirmations of existing rules (brief)

## 7. Extensions and divergences from files 01–04
