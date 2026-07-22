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

The 2026-03-10 video is a dedicated LB lecture — the richest single treatment of the concept in the whole corpus, materially deeper than file 02 §B's non-level note. Everything in file 01 §5b is confirmed; the following is new or sharper.

### 2.1 Formation, by diagram

Bearish LB: uptrend printing new highs → "grabbing a low here, inducing sellers. Why does this induce sellers? They are going to view this to be a BOS. This level is going to be a trap for them... and then we stab out the liquidity, and boom, that is where the liquidity block is now created" (IET 2026-03-10 "Liquidity Blocks" [01:12]–[01:32]). "Since we have swept out previous liquidity, now we view this high right here to hold no liquidity, meaning we don't have a reason to run above it" (IET 2026-03-10 [01:52]–[02:12]). Bullish is the stated inversion ([02:12]–[02:52]). Same object as V1's "no liquidity above this high" and V2/V3's LB — full agreement.

### 2.2 The LB's job, stated as a hard precondition (extension)

The sharpest formulation in any source: **"All the liquidity block does for you essentially is provide you a level to place your stop loss... aka no liquidity block, no stop loss. So, we need an LB to take an entry, of course"** (IET 2026-03-10 [04:52]–[05:12]). This upgrades file 03 §1.5 ("should sit beyond the entry", divergence noted between V2/V3 emphasis) into an explicit necessary condition: no LB → no trade. Restated on gold: "we're not just selling above highs... we need to make sure there's a liquidity block. This provides us our actual entry. In other words, it actually provides us a level for us to place our stop loss" (IET 2026-03-17 "$10k in 4 min" [03:44]–[04:04]).

### 2.3 Priority order: liquidity first, LB second (extension)

"Liquidity blocks is not the end all be all. Liquidity will always be priority, period... From a priority perspective, you have liquidity being up here, and then liquidity blocks being number two... If you don't [understand liquidity first], all you're going to be doing is plotting on highs and lows that have been taken out, taking entries left, right, and center, and you are going to accumulate a lot of unnecessary losses" (IET 2026-03-10 [03:52]–[04:12]). I.e., the LB is an *entry-plumbing* object subordinate to the bias/target logic — "you need to build a story first in your trade, aka the bias, the direction, which comes from liquidity, and then we will use the liquidity blocks for our entries" (IET 2026-03-10 [08:33]).

### 2.4 Not every LB is traded (new discrimination)

"Not every LB we're going to be taking entries off of... just because it's an LB does not mean we're going to enter off it. But it's important to identify them because you can anticipate this false reaction here, this pullback" (IET 2026-03-10 [05:32]–[06:12]). Untraded LBs still earn their keep as *expected-reaction markers* — spots where a counter-move can stall without invalidating the bias ("yes, it didn't sell all the way to the downside, but it still provided us a reaction in the market, and that alone is so important", [07:53]). The tradeable subset is the LBs that sit at the completion of the full induce→trap grammar with a confirmed target beyond (§1.2).

### 2.5 Stop placement inside/beyond the LB (confirms + tightens file 03 §3)

- "Use the low as the level to place your stop loss... I see a lot of people getting greedy or just placing it in random levels. No, you want to keep it as repeatable and systematic as possible" (IET 2026-03-10 [07:12]).
- "Stop loss is going to go just above our liquidity block. **That will never change**" (IET 2026-05-13 "Advanced Gold" [06:46]–[07:06]); "the stop loss is going to be below our low to the left. That will always stay the same" (IET 2026-04-28 "Ping Pong" [07:22]).
- Deep-stab tolerance — do not roll early: "price can sometimes stab in, give a false reaction and then stab in higher and then the move occurs... you roll your stop loss above that high [too early], price takes you out, comes deeper into the liquidity block... Remember, stop loss needs to stay above this high" (IET 2026-02-24 "$6,600 UJ" [05:24]–[05:44]); "it actually ended up just coming for the extreme up here and then the move starts occurring... you roll that stop loss out of pure fear [and you're out]" (IET 2026-02-24 [06:44]–[07:04]). Confirms file 03 §6's re-stab expectation and file 04 §2.4's no-fear-rolls rule, now tied specifically to LB depth.

### 2.6 Imbalance ≈ liquidity block (new equivalence)

Twice the channel identifies the LB zone with the *imbalance* the sweep leaves: "we sell off to the downside, leaving this imbalance area, **otherwise known as a liquidity block**" (IET 2026-03-03 "All You Need" [04:02]); "keep in mind we still have an imbalance above. The important part here is this is our liquidity block. That's why our stop loss is above it" (IET 2026-05-05 "Stacking Entries" [03:52]). Entry limits are parked "right in the imbalance" (IET 2026-03-03 [07:12]). Files 01–06 treat FVG/imbalance purely as a retail trap-zone concept; IET *repurposes* the displacement-gap geometry as the practical way to box the no-liquidity area behind a sweep. Divergence in vocabulary, not logic — but a bot could use the sweep candle's imbalance to bound the LB zone.

### 2.7 Workflow: drag the box to current price

The operational habit for using old LBs: "what I like to do is grab the whole area... drag it all the way over to current price action... as soon as price taps into it, we have a level to put our stop loss" (IET 2026-05-13 "Advanced Gold" [06:26]–[07:06]); same drag-over in the UJ trade ("we can take entries anywhere in this area. All we need to do is grab a box, grab this whole area and drag this across", IET 2026-02-24 [05:04]). LBs persist across sessions: the Asia-created LB served the New York re-entry ("in Asia... aka our initial entry, left a liquidity block. This whole area here... New York opens up. We get a spike up and look at that, right into our area", IET 2026-05-05 [06:52]–[07:33]).

## 3. The daily-bias method — deriving intraday bias from liquidity only

The channel never says the phrase "daily bias" (§0 note), but it teaches a complete, repeatable method for deriving each day's tradeable direction from liquidity alone — "purely just direction and bias in the market" (IET 2026-01-31 "Training The Eyes 12" [05:49]). Assembled procedure:

### 3.1 Higher timeframe first, or nothing

"I really want you guys to get used to starting off on the higher. **If you don't see anything on the higher, anything relevant, then you shouldn't be going to the lower time frame**" (IET 2026-07-21 "Correct Liquidity" [01:06]). Every trade breakdown in the corpus starts daily/4H → 1H → 15m/5m/1m (e.g., "I always build my narrative from the higher down to the lower", IET 2026-02-24 "$6,600 UJ" [00:42]; the whole of IET 2026-04-14 "Step By Step"). Timeframe choice is pragmatic: "whatever time frame makes sense in that given moment is what you need to be using... sometimes the 4-hour will make more sense, sometimes the daily does" (IET 2026-03-03 "All You Need" [00:42]); when a chart is "squeezed up" and unreadable, go *down* one timeframe to open it up (IET 2026-02-24 [01:42]; 2026-03-17 [02:24]).

### 3.2 The two-lines doctrine (the actual bias algorithm)

Mark the confirmed pool above and the confirmed pool below; everything between is noise:

> "Look how we've essentially trapped price with two lines. That's it. We have these lows intact down here and we have these highs intact up here... we're not interested in price unless it takes these highs out or we take out these lows. Look at the clarity you can now have. **Everything in between here is now just going to be known as noise**." (IET 2026-07-21 "Correct Liquidity" [11:47]–[12:27])

The in-between region is named: "I call this like **no man's land**... very choppy price action. This is where build-up of liquidity happens. I'm typically not trading in here. I want to see price either above or below... I will wait days if I have to, or weeks" (IET 2026-05-13 "Advanced Gold" [02:05]–[02:25]); "we plotted on the highs, we plotted on the lows. Anything in between here is going to be gross... This is building massive amounts of liquidity for retail. We stay away from that" (IET 2026-04-07 "Why You Can't Trade" [05:46]–[06:06]). The waiting rule: "mark out the lows, mark out the highs, **wait for one of them to get taken, and react accordingly**" (IET 2026-05-13 [04:26]–[04:46]).

This packages file 02's marking procedure into a daily decision rule: the day's bias is *conditional* until one of the two lines breaks; the break defines both the trap just completed and the draw toward the other line.

### 3.3 Bias assignment once a side is taken

- Taken side → that direction is done: "now that we've taken out all of the liquidity to the upside, you can anticipate a reaction back down" (IET 2026-01-31 "Training The Eyes 12" [02:26]–[02:33] inline tags); "now that we've taken out these lows, your eyes have to glue towards these highs. This is the next point of liquidity" (IET 2026-01-31 [05:53]–[05:59]).
- Lockout with a probability grading (new nuance): trades against the sequence aren't merely forbidden, they're *downgraded* — "since we are trading below old lows already, **sells will automatically be deemed lower probability**. Doesn't mean a sell can't occur, and it doesn't mean you can't take any sells. However, you need to pair it with time" (IET 2026-04-28 "Ping Pong" [01:02]–[01:22]); "once price starts taking out this high, buys should be out of your mind. 100%... I don't care if we actually move up and take out the high once more. Automatically, it's going to be lower probability" (IET 2026-07-14 "You Don't Know Liquidity" [12:36]–[12:56]). This softens V1's absolute lockout (file 02 §D) into a probability filter with a stated exception channel (time confluence) — a genuine refinement.
- Bias holds only while the target pool survives: "**as long as the highs stay intact, whatever happens below this high, buys are valid. Cuz that's the target**" (IET 2026-06-30 "Live Gold $9k" [04:04]); "once that target's taken, the sell is invalid" (IET 2026-04-07 [03:02]–[03:22]); "let's just say price takes the highs — you don't even have a buy target anymore. However, price still sells off, takes the lows. Why would you buy right here? That makes no sense because there's no reason for price to go higher anymore. We took the liquidity" (IET 2026-07-21 [11:07]–[11:27]). After the run completes: "the highs are taken... **buys are definitely off the cards now**" (IET 2026-06-30 [12:14]).

### 3.4 The previous-day-high/low frame (the daily bias in candle form)

The daily candle apparatus, absent from files 01–04, supplies the concrete "what do I expect today" call (IET 2026-07-07 "Liquidity Logic" throughout):

- **After a wild outside day** (spiked both Monday's high and the lows): "typically this following day is going to be no trading for me... I anticipate price to have more of an inside day, meaning we're going to trade below previous daily high and above previous daily low. And typically in those conditions... it's just going to be small in-and-out scalpy kind of trades... I'm usually on the brakes" (IET 2026-07-07 [02:43]–[03:23]).
- **Next-day script from the daily chart alone:** "since Wednesday has closed up, we have a PDL that we have yet to run... I don't believe Tuesday's low needs to get ran. Why? We just ran that level of liquidity. This low can act as a liquidity block. So what I'm anticipating just off the daily chart alone is Thursday to open up, we spike down below Wednesday's low, we hold Tuesday's [low], we use it as an LB, and eventually we can trade higher... Wednesday's high could be an intraday target; if you have more of a swing target, possibly Tuesday's high" (IET 2026-07-07 [07:23]–[08:03]). The play captured "the whole daily range, from PDL to PDH... a 1:9" (IET 2026-07-07 [10:23]–[10:43]).
- **The same candle logic is fractal:** the identical read executed on the 30-minute chart — previous 30m candle's low left unran, next candle spikes it → entry ("same thing's now happening on the 30-minute chart... the next candle comes in and boom, we spike out the previous 30-minute low. Boom, that is your entry", IET 2026-07-07 [10:03]–[10:23]).
- **Day-boundary confluence:** "Friday's high, Friday's low. Great, great confluence. We've talked about this a million times on the channel. Monday spikes above Friday['s high]. Boom. We now have a great target to the downside, aka Friday's low" (IET 2026-07-14 "You Don't Know Liquidity" [17:36]); the trade thesis "price to trade above Monday's high... then sell off into Friday's low and eventually lows in the left-hand side" (IET 2026-07-07 [02:03]–[02:23]).
- **No-trade calendar days:** "if there ever is a bank holiday, do not trade, guys. Do not trade... It is just simply a no trading day" (IET 2026-07-14 [09:56]–[10:16]).

### 3.5 The H4-candle / 10:00 a.m. model (the flagship timing-plus-bias rule)

A fully specified model, new relative to files 01–04 (V1 only *observed* a 4H-close entry at 10:00; here it is systematized) (all IET 2026-02-10 "Simple Strategy"):

1. The reference candle is the **6:00 a.m.–10:00 a.m. (NY) H4 candle**: "we're going to be talking about the 6 a.m. to 10:00 a.m. H4 candle... Typically, I am trading only New York session" ([01:27]–[02:07]).
2. At **10:00 a.m.** the next H4 candle opens — "a very, very powerful time, especially in the futures market" ([01:47]–[02:07]).
3. Bullish case: **longs only below the previous H4 low, only around/after 10:00** — "once we trade below previous 4-hour low, this is when you want to start looking for longs... We are not longing until that low is taken out. Once the low is taken out, longs are active. It's a very strict rule for this model" ([02:47]–[03:27]).
4. The sell-off into the sweep is pre-classified: "typically we'll view this whole sell-off from high to low being false... That's what we usually call the **10:00 a.m. reversal**" ([07:47]–[08:07]).
5. The entry still requires the standard plumbing — an LB and a stop covering the left-hand low: "we need to make sure there's actually a proper entry... my stop loss always covers this low to the left-hand side" ([05:47]–[07:27]).
6. Mechanical target option: **the previous H4 high** — "you can just target that H4 high. Very systematic, very repeatable. It's a stupid simple strict model that you can use on a daily basis" ([08:27]–[08:47]) — or liquidity targets beyond it.

Corroboration across the corpus: the both-sides day pivots at 10:00/10:30 with "we just swept out the previous 4-hour candle. Look at the time" (IET 2026-04-28 "Ping Pong" [07:22]); "if price action delivers an entry in and around stock open, that move is typically going to be a trap move, and once the trap move is complete... then you can look for that reversal" (IET 2026-04-28 [08:43]–[09:03]); a 10:00 a.m. sell-off runs the marked internal level "what a coincidence" (IET 2026-07-21 [07:06]–[07:26]); the gold short whose "clean time... was perfect. To the minute" — the 9:00 a.m. simultaneous 5m/1H/4H(CFD) candle open spikes the high and closes back below → the **only** situation where a candle-closure entry is allowed: "the only time I ever take a candle closure entry is when I have a time confluence to a T, and it has to be perfect" (IET 2026-07-14 [19:18]–[19:58]).

**Note (my analysis):** this makes *time* a first-class arming input in IET's system in a way files 01–04 only hinted at through V1's session filter: stock open (9:30), 10:00 a.m. H4 roll, Asia open (8:00 p.m. — used as the "great timing confluence" for the Asia entry in IET 2026-07-07 [09:03], [11:03]–[11:23]), and day boundaries all act as trigger qualifiers.

### 3.6 Time asymmetry of build vs run (expectation-setting)

Liquidity builds slowly and is consumed fast — quantified twice: "from the point where we started building liquidity: 5 days of price action. And then all it took was 18 hours for us to swallow all of that price action up" (IET 2026-06-09 "Everything Liquidity" [12:06]); "4 and a half days basically, we had a build-up... rapid move back down: 19 hours. So 25% of the time" (IET 2026-06-09 [15:26]–[15:46]). Setups can take "four days... seven days, eight hours of waiting" to arm (IET 2026-04-07 [05:46], [08:29]–[08:49]) — and marked levels stay valid meanwhile ("leave the lows marked on or leave the highs marked on. It will be used in the future", IET 2026-04-07 [01:02]–[01:22]; the Thursday internal lows used "24 hours later, and it aligns perfectly with news", IET 2026-07-21 [14:29]–[14:49]).

## 4. Both-sides / ping-pong range trading

Files 01–04 treat each setup as one-directional. IET 2026-04-28 "Ping Pong" demonstrates trading **both legs of the same day** — the trap move down, then the reversal up — as two independent instances of the same model, chained. This is the practical realization of file 03 §4.4 ("the target sweep may arm the next setup") with the missing operating rules.

### 4.1 The worked NQ day (all cites IET 2026-04-28 "Ping Pong")

1. **Context:** price already below old lows → "any sells automatically will be deemed low probability... you need to pair it with time" ([01:02]–[01:22]). The short is taken anyway *because* the time qualifier holds (stock open).
2. **Leg 1 (short), pre-framed before it happens:** liquidity above the respected high ("tapped into this area once, twice, causing that sell-off — there's going to be liquidity above this high", [02:42]); equal lows below as target ("look at those equals the market left for us", [03:02]); "in order for me to look for a sell, I definitely need to see price above this high" ([02:42]–[03:02]). Stock-open volatility spikes the high → sellers trapped → LB above ("we have induced sellers and trapped them. We have no reason to run above that high... we're going to use this level as an area where we can place our stop loss", [04:42]–[05:02]). Entry at the stab: ~200 ticks/51 points stop, "down to these internal lows you're already achieving over a 1:3, and the full target down to the lows... almost a 1:5" ([05:02]–[05:22]).
3. **Hinge:** the sell-off completes into the low-side pool at **10:00 a.m.** — "10:00 a.m. has now opened up and we are spiking out lows, trapping buyers, leaving internal highs intact" ([06:02]–[06:22]). The short's *target consumption* is simultaneously the long's *arming sweep*.
4. **Leg 2 (long):** requirements re-verified from scratch — buildup below the low ("we are building a significant amount of liquidity below that low", [07:02]–[07:22]), LB to the left, time confluence ("we just swept out the previous 4-hour candle. Look at the time. 10:30", [07:22]), and a reason to go up ("we left an internal high... **if we didn't leave these highs, most likely I probably wouldn't be looking for this buy back up**. This is logic, reasoning for price to go back long up to here", [07:42]–[08:02]). Entry 10:50, target hit 16 minutes later ([08:22]–[08:43]).

### 4.2 The extractable rules

- **Each leg must independently satisfy the full model** (pool, trap, LB, target, time). The reversal long is *not* taken merely because the short's target was hit — the internal highs left behind are its precondition ([07:42]).
- **The against-sequence leg needs a time excuse; the with-sequence leg doesn't.** Low-probability grading (§3.3) is overridden only by session-structure timing (stock open / 10:00 a.m. H4 roll) ([01:02]–[01:22], [08:43]–[09:03]).
- **Stock-open moves are presumed traps:** "if price action delivers an entry in and around stock open, that move is typically going to be a trap move, and once the trap move is complete, aka the sell in this scenario, then you can look for that reversal" ([08:43]–[09:03]). I.e., the first NY move is faded, then ridden back.
- **Rarity disclaimer:** "these days do not come often" ([08:43]). The default remains one-directional.
- Range-context version of both-sides bookkeeping: in "no man's land" both edge pools are marked and *either* break is tradeable — "wait for one of them to get taken, and react accordingly... I waited for price to move bullish and run the sellers" (IET 2026-05-13 "Advanced Gold" [04:26]–[04:46]); the flip side is monitored even mid-trade: "I always like to look at it from the flip side too, just in case I'm incorrect... look at all these lows we've been building — could possibly provide us another buy opportunity after taking the lows out" (IET 2026-06-30 "Live Gold $9k" [01:43]–[02:23]).

## 5. Stacking / scaling entries

V1's scale-ins (file 04 §4) were adds to a live position below fresh mini-sweeps. IET 2026-05-05 "Stacking Entries" teaches a different structure: **sequential full entries in the same direction, each a complete standalone setup, justified by one shared surviving target** — closer to file 03 §7 row 7's stacked gold entries (V2) than to V1's adds.

### 5.1 The governing rule (the new content)

> "**If you guys want to learn how to stack entries, you need to understand: if our target is left intact, all that means is we have another opportunity to sell.**" (IET 2026-05-05 "Stacking Entries" [08:13]–[08:33])

And its guard: "as long as what? Our target stays intact. This is very important. **If we stay above this low, sell setups are still active**, they're still valid" ([05:52]–[06:12], said of staying-*above* the target lows in the sell case). The stack closes when the shared target is consumed: "now that these lows have been taken, we're out of our positions. These are done. Our sells are completed" ([09:33]–[09:53]).

### 5.2 The worked USDCAD stack (both cites IET 2026-05-05)

- **Entry #1 (Asia, passive):** internal high respected → liquidity above; sweep leaves an LB; "once price did this, all I did was set a limit... Stop goes above the high. Let's open this up though for spread... this is almost a one-to-eight opportunity... even to this structural low, still a one-to-4.6" ([02:52]–[03:32]). Taken asleep, managed by nobody ("I'm sleeping, so it doesn't matter what happens... I have a stop loss set and I have a target set", [04:52]).
- **Between entries:** post-trap reactions are re-labeled traps that *feed* the next entry: "since we have taken out the highs, you have to deem these areas as traps. If we do react off them, these bullish reactions will only provide us **another opportunity to sell**" ([05:32]–[05:52]).
- **Entry #2 (New York, next day):** a fresh respected high prints; the question asked is the standard checklist — "we have a level of liquidity. Awesome. We want to sell above it, of course. But do we have a liquidity block to take our entry off of?" — and the answer is **entry #1's own LB, reused**: "last night, aka our initial entry, left a liquidity block... New York opens up. We get a spike up and, look at that, right into our area" ([06:52]–[07:33]). Stop above the high "with breathing room... you forex guys know you need to be leaving breathing room for spread" ([07:33]).
- **Targets for the stack:** the engineered buyer liquidity built on the way up — "all of this buyer liquidity that was engineered on the way up, you want to use that as your target" ([07:53]).

### 5.3 Reconciliation with V1's scale-ins (my analysis)

Compatible but distinct layers: V1 adds contracts *inside one trade* on fresh LTF sweeps with per-add invalidation (file 04 §4); IET stacks *separate trades over hours/days* under one HTF target, each with its own full arming sequence and stop. The shared invariants: every add/stack requires its own sweep-plus-LB, and everything dies when the shared target is consumed. The Masterclass NQ trade and TTE 13 show the same pattern intraday — "entry, build, entry, build, entry... all three of these entries repeatable, the exact same thing over and over" with per-entry LBs and RRs 1:4/1:8/1:8 (IET 2026-02-17 "Training The Eyes 13" [07:12]–[08:33]).

## 5. Stacking / scaling entries

## 6. Confirmations of existing rules (brief)

## 7. Extensions and divergences from files 01–04
