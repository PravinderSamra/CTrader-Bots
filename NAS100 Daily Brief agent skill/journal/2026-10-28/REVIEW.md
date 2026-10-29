# 2026-10-28 (Wednesday) — review

Graded from `review_day.py 2026-10-28 --json`. One scan, `PRE_NY` 12:52:35Z,
`is_trading_day: true`, 276 bars, **0 test artefacts**. Arithmetic is the
script's; judgement is mine.

---

## 1. Scoreboard

| | |
|---|---|
| session O / H / L / C | **29666.9 / 30023.6 / 29521.7 / 29590.9** |
| range · net | **501.9** (0.868x ADR14 578.0) · **−76.0** |
| call | **BULLISH +6**, direction **+1**, `COHERENT_LONG`, Strategy 1 |
| post-scan move (official) | **−158.2** → **WRONG** |
| day-net move | **−76.0** → **WRONG** (bases agree; **not** a P-H deciding instance) |
| direction record | post-scan **13/25 = 52.0%** · day-net **14/25 = 56.0%** · convention cost **4.2 → 4.0** |
| levels published / touched | 23 / 17 → **hit rate 0.74** |
| fuel | budget **373.4** vs extension **297.3** → **0.80x, "about right"**; error **−76.1**; traversal **501.9 = 1.34x** |
| H26 bucket | |score| 6 → **6–9**; **|post|/ADR 0.274**, range/ADR **0.868** |

**The number that matters most is not in that table.** At 19:55Z — the last bar
before the NY cash close — price was **29835.2, +86.1 above the scan**. The
bullish call was **right through the entire cash session**. Every point of the
−158.2, the 30023.6 high, the 29521.7 low and **53.0% of the day's whole range**
were made in the **55 minutes after 20:00Z**, on the MSFT / GOOG / GOOGL
after-hours tape. Section 3 of this review treats that as the central fact.

---

## 2. What the levels actually did

**The call wall capped the day and the grader filed it as broken.**
CALL WALL 29947.1 (+201, 0.89bn, stacked with a 0.75bn shelf ⭐ and the 45-day
call wall) was above price on **1 of 97 post-scan bars**. The single 20:00Z bar
printed 30023.6 — 76.5 through it — and price then fell **501.9 points in 55
minutes** and closed **356.2 below** it. The prose said *"rallies stall, take
profit into it… a held close above flips that selling to buying"*. That is
**exactly what happened**: no held close above, and the reversal from the
overshoot was the largest move of the day. `settled_read` returns
`held: false, acted_as: "lost"`, because the 76.5 overshoot exceeds
`SETTLE_TOL = 25.0`. **The verdict is inverted** (M6, below). Same for PWH
29936.0 (+190, one bar above, close 345.1 below) and the 0.63bn shelf at
29897.1.

**Max pain was the best level in the document.** 29597.1 at **−149** (0.26x ADR
away — a real test, not a distance-confounded one). **Close 29590.9, 6.2 points
below it.** On a Wednesday, against the brief's own *"weak on a Monday, strong by
Thursday/Friday"* hedge. The 2026-10-28 review recorded the first clean max-pain
test in the record and it **failed by 234 points**; this is the second clean
test and it hits to 6.2. **Census 1–1. Nothing proposed.**

**The put wall did its job and could not be graded.** PUT WALL 29547.1 (−199):
low **29521.7**, swept **25.4** through, then bounced **69.2** to close **43.8
above** it. The prose — *"expect a bounce and a good long-sweep here"* — is a
clean hit. `review_day` returns *"touched, no settled read (too few bars on one
side)"* because the touch landed at 20:40Z with three bars left. **The day's
single best-executed wall call is formally ungraded.**

**One level held on the official read, and it held by accident.** Asia High
29812.2 is the only *"stalled at it — held as resistance"* verdict of the day
(+7.7 worst excursion, 50 min). Its settle window opens at 20:10 instead of
20:00 or 20:05 — one and two bars later than its neighbours — which is the only
reason its excursion fits inside the tolerance. Six rows above it, with the same
character, read *"lost"*.

**Six rows never reached**, all of them prev-day liquidity 278–613 below:
29468.4, 29429.3, 29340.8, 29157.9, 29138.8, 29133.4. The nearest untouched row
missed the low by **53.3** — so 10-28 is **not** a `TOUCH_TOL = 8.0` instance
(that item stays at n=2), and the four `_(stretch)_` rows behaved exactly as
labelled. No "noise level" finding today: the misses are honest distance.

**The named upside brake was at +1 point.** §3: *"UPSIDE path: has friction.
Expect a stall at 29747.1 (1pts away)."* A friction level one point from spot is
the price itself, and the board offset on the same page is **−2.9** — the brake
sits **inside its own conversion uncertainty**. It was sliced by **276.5**. The
downside brake 29697.1 (−49) was sliced by **175.4**. **H23: both reachable,
both sliced; slice census 13/3/3 → 15/3/3.**

**Secondary table, one row: 29997.1 (+251, 0.33bn) *"expect a stall"*** — high
30023.6, **exceeded by 26.5 → WRONG** on the established convention.

---

## 3. What was wrong, and why

`inputs.bias_components`: **gamma +4 · breadth +3 · vol +1 · news −2**;
structure net 0 (+1 / 0 / −1), rates 0, macro 0, fuel 0, events 0.

**(a) The call was not wrong in the session it was written for.** Through
13:30–20:00Z the brief was right: +86.1 at the close, a 235.8 cash-session range
against a 373.4 budget. What killed the grade was an **after-hours earnings
tape the brief had on its own page** (§5 listed MSFT, GOOG and GOOGL
after-hours; the `events` rows carried all three at **+0**). The engine saw the
three largest-weight earnings releases of the quarter landing 7 hours after the
scan and priced them at exactly zero, then published a **fade** strategy and
*"new highs and lows are live"*. The failure is not a wrong block; it is a block
that cannot express the only thing that mattered. **`events` has now scored 0 on
5 of 5 rows today and on every row in the record.**

**(b) The FOMC was five hours ahead and §5 said there were no events.**
`events_24h: null` (the calendar fetch failed — `upcoming_next_24h` is absent
from `mc["calendar"]`, not empty), and `brief.py:1064` renders `null` and `[]`
identically. **This is the harm case D28 was opened for, and it is demonstrable:**

| window (UTC) | range | share of the 13:30–20:00Z cash range (235.8) |
|---|---|---|
| 13:30–18:00 (pre-decision, 4.5h) | 181.1 | 76.8% |
| **18:00–18:45 (decision + first presser minutes, 45 min)** | **221.1** | **93.8%** |
| 18:45–20:00 | 175.1 | 74.3% |

The **top six 45-minute windows of the whole cash session all begin between
17:55 and 18:30Z** — every one of them contains the decision. 221.1 points is
**38.3% of ADR14** in 45 minutes, and the cash-session high (29854.5, 18:40Z)
was set inside the press conference. The Fed **held** (confirmed by the 10-29
judgement list: *"Fed Holds Interest Rates Steady After September Hikes"*).
**10-28 is a demonstrable-harm instance, not a missing-row instance** — and the
harm is specifically the §5 **rendering**, not the gate: at 12:52Z the decision
was 5.1h away and `bias_engine.py:254` only gates inside 1.5h, so the gate was
correctly `None` with or without the feed. The document also **contradicts
itself three lines apart**: §6's judgement list carries
*"[fomc_event] …Dow Falls Ahead Of Rate Decision…"* and *"Fed meeting live
updates: No hike expected…"*. The 10-29 scan's `events_24h` is **populated**, so
the outage was transient — which is the point: a transient fetch failure must
not print as a fact.

**(c) `news −2` was built on one headline the scorer read backwards and one it
read without its subject.** *"Federal Reserve likely to **skip** rate hike as
elevated inflation drives voters to the polls"* → `[hawkish]` → *"Hawkish
repricing -> bearish long-duration tech, ~180pts / 90min"*. Skipping a hike is
dovish; **the Fed did hold**. The second, *"Four reasons to start worrying about
inflation — the end of tariff **refunds** is one of them"* → `[tariff_general]`
→ *"Trade-policy escalation -> risk-off"*: the keyword matched, the subject
(refunds ending, not tariffs escalating) did not. **Reason FALSE on both.**
**Score, graded separately:** the pair carries −2 inside a **+6**; dropping the
negation failure gives **+7**, dropping both gives **+8**. **No side change, no
label change** (+6/+7/+8 are all `BULLISH` and all in H26's 6–9 bucket), and on
the official post-scan basis the correction makes a wrong call **larger** —
while on the cash-close basis it makes a right call larger. **D18 day 10 /
headline 17; D9 instance 4. Nothing proposed; both entries already carry live
proposals.**

**(d) The two gamma rows carried the call and the second one was circular.**
`gamma +2` for *"above flip by 67.3pts"* and `gamma +2` for *"week net GEX 2.12
→ pinning likely"*. The pinning row was **right about the range** (0.868x ADR,
H22 label correct) and was then spent as a **direction** vote. 67.3 points above
the flip is **0.116x ADR** — the same full-strength term the engine awards at
0.64x ADR — the no-distance-scaling finding, third consecutive session, already
owned by the unarbitrated two-gamma-rows conflict.

**(e) H27, observation 4 — the same-signed configuration.** vol ↔ breadth
**+4** (+1, +3); structure ↔ gamma **+4** (0, +4); **independent remainder −2**
(news) against a **+6** score. **The correlated pairs carry +8 of a +6 call and
the independent content opposes it.** This falls with observations 1 and 2 and
**against** observation 3 — more extremely than either, since the remainder is
not merely small but opposite in sign. The pre-registered collapse rule (drop
the smaller member on a **strict** shared sign) fires on vol/breadth only
(structure is 0, not strictly same-signed) → **+5, still direction +1, still
WRONG**. **Weight limb stays ANSWERED-NEGATIVE. Nothing re-proposed.**

---

## 4. Change proposals — none

**Nothing is proposed from 10-28.** `track.py` prints no literal
`actionable: YES/NO` — it prints *"threshold met, read the evidence before
proposing"* — so the 3-session rule was applied **by hand, per entry**. Every
item below is appended to `HYPOTHESES.md`; **no ID was allocated** (next free
stays **H28 · D29 · P-J**).

**The one item that reached three sessions and still does not qualify.**
`review_day` grades to the **last bar of the trading-day bucket, 20:55Z** —
55 minutes past the cash close. Re-run across the **31 finished trading days the
bar window still serves** (09-24 excluded by hand; anchor = `price_at_scan`),
grading to the last bar before 20:00Z instead changes the verdict on **3 days**:

| day | to last bar | to cash close | effect |
|---|---|---|---|
| 09-29 | +11.1 **RIGHT** | −30.5 **WRONG** | the late hour **saved** a wrong call |
| 09-30 | +7.8 **WRONG** | −23.3 **RIGHT** | the late hour **broke** a right call |
| **10-28** | **−155.6 WRONG** | **+88.7 RIGHT** | the late hour **broke** a right call |

Three instances, **split 2–1**. The rule is three sessions *pointing the same
way*; this does not, so **nothing is proposed**. Recorded with the pre-registered
test and the range limb (post-20:00Z bars supplied >20% of the day's range on
3 of 31 days: 10-28 **53.0%**, 10-19 46.0%, 09-17 22.1%). Grepped to **P-H**
before writing — P-H owns the grading convention; this is a different limb of it
(the window's **end**, not its start) and takes no number.

**Still observing, with today's observation.** H26 (re-derived from source,
n=31: magnitude monotonic a 10th time at **0.167 / 0.329 / 0.510 / 0.685**;
direction **—/50.0%/55.6%/42.9%**, still inverted at the top — and the 6–9
figure **disagrees with the register's carried 66.7% because 09-11 aged out of
the bar window today**: D26 is now eating H26's sample, both numbers reported,
neither averaged) · P3/H6 (structural call-wall touch **2**, but **confounded** —
the 45-day wall is merged into the weekly wall at the same price, so on a strict
reading the call side is still at **1 clean instance**; the *"stop publishing
it"* narrowing stays **blocked**) · H2 (doubly a **non-instance** —
`ROOM_TO_EXPAND` **and** above the flip — but the two-opposite-instructions
contradiction **fired outside the LOW_FUEL/EXHAUSTED branch for the first time**:
§2 *"breakouts mostly fail"* against §3 *"new highs and lows are live…
somewhere to go"*, which **breaks the 3-control localisation**) · M6 session 34
(**6 inverted verdicts off two adjacent bars**; driver of the series stays
**UNKNOWN**) · P5 (**0 of 1**, and the two-session streak of the best level
sitting in the ungraded secondary table **BREAKS** — today's best level,
max pain, was on the main board) · TOUCH_TOL (**not** an instance, stays n=2) ·
H18/P1 (instance 27, duplication 32/32, both members **scored 0** — a clean
null) · board offset (**5th** level printed inside its own offset, and the first
where the affected row is the brief's **own named brake**) · D23 (**observation
11**, §7 absent, no residual inferred, D25 interrupted at 29) · D26 (**visible
31 days / 31 scans against 41 finished on disk**; 9 invisible and **09-14 filed
*"not finished"* at 97 bars — the original D26 symptom has RECURRED** after the
10-22 review reported it had changed to silent invisibility) · D27 (**6th
consecutive 401**) · H22 (n=15, label **RIGHT**) · H8 (close **inside** the
29505–29988 band) · H4 (flip lost, close 88.3 away — **negative**) · H23
(15/3/3) · P-E instance 17 / P-E(b) #18 · P-G **#34/#35** · P-B(b) 22nd
(**zero** guaranteed windows, closest pair 9.1) · session-context 22nd (**10 of
24** rows already traded pre-scan) · dead-weight (**20 of 29** rows scored zero).

**No instance:** H7 · H10 (inside the prior-week range — control) · H11 ·
H12/H13 (volume ladder lost to the 401) · H17 (31.5% of session range, outside
the deadband; stays 2 of 3) · H20 · H3 (closed) · D7 (footnote 1 row against a
cap of 6 — control on both limbs) · D21 (`gamma +0`, 50% up the band — control) ·
D22 · D24 (correctly no instance; see D28) · `PIN_THEN_EXPAND` (`COHERENT_LONG`;
closed, falsified 3/3, **P-I** is the live item) · the gamma-outvoted cell
(gamma **won**) · P-F (price above PD mid, inside the PD range — inside-control,
not re-derived).

**No new data point is warranted.** The FOMC was free, scheduled, and already in
this pipeline — the feed carried the full FOMC block on 09-16. The fix is to
stop asserting the calendar's absence (**D28**, already proposed), not to buy a
second feed. The earnings that actually decided the grade were **already printed
on the page** at `+0`. Nothing external was missing on 10-28.
