# GEXBot — evaluation and integration plan

Tested 2026-09-05 (Saturday). **Every figure below is Friday 4 Sep's 19:59:59
UTC close, frozen for the weekend.** Nothing about intraday behaviour or
refresh rate could be tested today; the items marked UNVERIFIED need an RTH
session.

Client: `scripts/gexbot.py`. Token read from `GEX_BOT_API_TOKEN`, never logged.

---

## 1. What the account has

Base `https://api.gexbot.com`, package **classic**, categories
`gex_full` / `gex_zero` (0DTE) / `gex_one` (1DTE).

Coverage includes everything we care about: **NDX**, **QQQ**, and futures
**`NQ_NDX`** and `ES_SPX`.

Per response: `spot`, `zero_gamma`, `major_pos_vol`, `major_pos_oi`,
`major_neg_vol`, `major_neg_oi`, `sum_gex_vol`, `sum_gex_oi`,
`delta_risk_reversal`, `max_priors`, and a **142-strike ladder** where each row
is `[strike, gex_vol, gex_oi, [5 prior samples]]`.

## 2. The three things we genuinely cannot build

**a) Volume-weighted GEX, signed.** The one thing the CBOE pipeline cannot do
honestly — volume carries no side, so weighting walls by it stacks an
assumption on an assumption. GEXBot sees the trades and signs them.

It is not a marginal difference. On Friday's close, near spot:

| Strike | Ours (OI, $bn) | Theirs OI | **Theirs VOLUME** |
|---|---|---|---|
| 29,500 | +0.197 | 2,635 | **25,523** |
| **29,525** | **−0.016** | 346 | **83,936** |
| 29,550 | +0.444 | 671 | **56,278** |

**Price closed at 29,542.65.** The volume lens put its heaviest concentration
at 29,525–29,550, exactly where price pinned. Our OI-only view showed 29,525 as
approximately nothing.

**b) Per-strike priors.** Five prior samples of GEX at *every* strike — walls
building and unwinding through the session. This is precisely the question
`research/live-walls/` was built to *estimate*.

Worth being exact about the relationship: our estimator infers **ΔOI**;
GEXBot's priors show **ΔGEX**, which moves with price and greeks as well as
positioning. They are not the same quantity. But for the practical question —
*is this wall growing or being taken off?* — the priors answer it directly and
ours only approximates it.

**c) `NQ_NDX`** — the NDX levels plus a constant (+30.82 on this snapshot),
i.e. already in futures space. That removes the stale-cash-roll-forward
workaround (`_nq_implied_cash`) that has bitten us before.

## 3. Where they disagree with us — and it is not small

Anchored to their spot, 25pt bins, ±400 around price:

**Sign agreement on the OI ladder: 25 of 32 strikes (78%).** The seven
disagreements cluster at 29,150–29,600 — around spot, where it matters.

Headline levels, same snapshot:

| | GEXBot | Ours (week) | Ours (45d) |
|---|---|---|---|
| Flip / zero-gamma | 29,542.7 | **29,323.2** | — |
| Major +GEX (OI) | 29,500 | 29,700 | 30,000 |
| Major −GEX (OI) | 29,600 | 29,050 | 28,800 |

**The −GEX row is not a disagreement, it is a different question.** Their
`major_neg` is the most negative strike *anywhere*; our put wall is *the most
put-dominated strike below spot*. Their answer sits **above** spot. Treating
those as the same level is exactly the confusion that produced D4, and the
client deliberately does not rename their fields into our vocabulary.

**Spot itself differs by 42 points** (29,542.65 theirs vs 29,584.70 ours, which
was running `nq_implied`). On a frozen weekend both cannot be right.

## 4. Two things that must be verified before use

**`zero_gamma` equalled `spot` EXACTLY** — 29,542.65 — for both `gex_full` and
`gex_zero`. It differed for `gex_one` (29,470), which argues it is genuinely
computed rather than a fallback, and Friday was an expiry with heavy pinning.
But "computed value happens to land exactly on spot to two decimals" deserves
suspicion, and **our flip is the number that decides which of the two strategies
to trade**. Verify across several RTH samples before it replaces ours.

**The `priors` array ordering is undocumented** and cannot be established from a
frozen snapshot — newest-first and oldest-first give opposite trend readings.
Sample twice during RTH and compare before reading any direction from it.

## 5. Recommendation: additive now, replacement only on evidence

**Do not swap the gamma engine.** Three reasons, all consistent with how every
other change here has been handled:

1. Their flip is unverified and ours is properly computed by repricing the book
   across a spot grid. Swapping an unverified number into the field that picks
   the strategy is the largest single-point risk available.
2. 78% sign agreement means they disagree with us on roughly one strike in five
   near spot. **One of us is wrong there and we do not yet know which.**
3. Their wall definitions are not ours. Reconciling is real work, not a config
   change.

**What to do instead**, in order:

1. **Add the volume lens as new information** — it is additive, cannot be
   replicated, and needs no reconciliation. Nothing existing changes.
2. **Run both ladders in parallel** and grade them with the machinery already
   built: `gex_retro.py --ladder` plus `role_reversal()`. Persist a GEXBot
   ladder beside ours on every scan.
3. **Let the evidence decide the swap**, per the 3-session rule.

Opened as hypotheses rather than assumptions:

- **H12 — does the volume-weighted wall hold better than the OI-weighted one?**
  Threshold 5 sessions. Grade both with `role_reversal()`. This is the question
  that decides whether GEXBot replaces the ladder or merely enriches it.
- **H13 — is GEXBot's `zero_gamma` a real flip or a fallback to spot?**
  Threshold 5 RTH samples. Record `zero_gamma`, `spot`, and our own flip each
  scan. If it tracks spot within a point every time, it is not a flip.

## 6. What this does NOT replace

The brief's value is synthesis, and GEXBot supplies none of it: no liquidity
levels (PDH/PDL, session highs/lows, equal highs/lows), no range/fuel model, no
macro, no news, no event gating, no bias engine, no QQQ blending, and no
CFD-space conversion for the specific broker feed being traded.

**GEXBot is a better gamma input, not a replacement brief.** The correct framing
is that it may replace `cboe_gex` + part of `gex_levels`, and only once H12 and
H13 have answered.

## 7. Cost/benefit against the earlier tick-stream evaluation

The tick-stream review concluded the most valuable purchase would be a
**historical GEX archive**, because the register is rate-limited by the calendar
— 4 trading days on record against thresholds of 5 and 10.

**GEXBot as configured does not solve that.** It is a live feed with 5 prior
samples, not a backtestable history. It makes each future day richer; it does
not make past days available. Both observations stand, and they are answers to
different problems.

---

## 8. The sibling `Gex-Bot/` project already records this — do not duplicate it

Discovered 2026-09-05. There is a separate project in this repo,
`Gex-Bot/`, with a Firestore recorder that captures GEXBot snapshots every
5 minutes through the US cash session.

**It was built to answer the same question as H12.** From its own
`docs/recorder.md`:

> *"so we can answer from our own data the question the two source videos
> disagree on: does price respect the volume-derived walls or the
> open-interest-derived walls?"*

Each record stores **both readings side by side and takes no view on which is
correct** — `major_pos_vol` / `major_neg_vol` / `sum_gex_vol` against
`major_pos_oi` / `major_neg_oi` / `sum_gex_oi`, plus derived
`regimes_agree` / `walls_agree` flags so disagreement is directly queryable.

Two collections: `gex_snapshots` (append-only, doc id `{TICKER}_{scope}_{ts}`)
and `gex_latest`. Default symbols include **`ndx` and `nq_ndx`** at `zero`
(0DTE) scope.

### State as of 2026-09-05

- The workflow `gexbot-record.yml` is on `main` with a cron of **every 5
  minutes, 13:00–21:59 UTC, Mon–Fri**.
- Runs 3–6 failed on Firestore credential handling. **Run 7, today at
  14:48Z, succeeded.**
- So the machinery works as of today.

**Correction (2026-09-05, after the first authenticated read).** This section
originally said *"the archive starts now"*. That was optimistic about the
calendar. What started on Saturday was the **capability**, not the
accumulation: the cron is `*/5 13-21 * * 1-5`, 5 Sep was a **Saturday**, and
run 7 was a manual dispatch against a frozen Friday feed. **Nothing has been
recorded since, and nothing will be until Monday 2026-09-07 13:00Z.**

The archive currently holds **4 documents — which are 2 observations**, from a
single instant (2026-09-04 19:59:59–20:00:00Z). `NQ_NDX` is `NDX` plus a
constant 30.82 and `ES_SPX` is `SPX` plus 6.13, exact across every wall field,
so the futures rows are basis-shifted representations of the same computation
and carry no independent information. Any sample count that treats the
collection as four symbols overstates it by 2×.

**A working pipe reads like progress and is not one.** H12 stays at 0 of 5 and
H13 at 1 of 5.

### What this changes

**H12 does not need a bespoke collection pipeline.** The right move is to read
the sibling project's archive rather than build a second one — two recorders
of the same feed would drift, and the register already carries that lesson from
the two-graders problem.

It also partly answers the constraint the tick-stream evaluation identified.
That review concluded the binding limit was the *calendar* — evidence
accumulating one session at a time. This does not retrieve the past, but from
now on it accumulates at **5-minute resolution** rather than one scan a day,
which is a large multiple on how fast H12 and H13 can be settled.

### The blocker, and it is small

**This session cannot read Firestore.** `FIREBASE_SERVICE_ACCOUNT_JSON` is a
*repository* secret, available to Actions but not exported into the Claude
environment, and `google-cloud-firestore` is not installed here.

To use the archive from the brief, that credential needs to be available to the
session the same way `GEX_BOT_API_TOKEN` is. Until then the brief reads GEXBot
**live** on each scan, which works and is what it does today — it simply cannot
look back at days when no scan was run.

### One correction the sibling project's docs forced

Its `docs/recorder.md` describes `max_priors` as a
**1/5/10/15/30-minute max-change panel**, while `docs/api-reference.md` calls
the per-strike array "5 prior gex readings". **Those are not the same claim**,
and a multi-horizon panel read as an equal-interval series would produce a
confident and wrong trend.

`gexbot.wall_drift()` was already written to be ordering-agnostic — it reports
which strikes appear and the spread between them, nothing about direction — and
the caveat in `gexbot.py` now records why that must stay true until one of the
two descriptions is confirmed.

---

## 9. Why no Claude session can read Firestore — and what would change that

Checked 2026-09-05 after a reasonable challenge: the Gex-Bot and PravZella
sessions never complained, so why does this one?

**Because neither of them read Firestore either.** They wrote code that runs
*elsewhere*, where the credentials live.

The Gex-Bot project says so in its own documentation
(`Gex-Bot/docs/recorder.md`):

> *"The Firestore write path has not been executed end to end. **No service
> account credentials were available in the development session**, so the
> encoder is unit-tested … but the first real write will happen on the first
> manual run."*

That session hit **exactly this wall**. It unit-tested the encoder, verified
both failure paths, and let GitHub Actions perform the first real write.

Three separate trust boundaries are in play:

| Who | How it authenticates | Where the credential is |
|---|---|---|
| **The recorder** | Admin SDK, service account | GitHub repo secret, injected by `gexbot-record.yml` |
| **The dashboard** | Firebase Auth, signed-in user | **your browser**, at login |
| **A Claude session** | — | **nothing** |

Verified here: a full environment scan for anything matching
`firebase|google|gcp|firestore|service_account|vite` returns **empty**, and
`google-cloud-firestore` is not installed. An unauthenticated Firestore REST
read returns **403 PERMISSION_DENIED**, which is the rules working as designed
— `db/firestore.rules` requires `request.auth != null` on both `gex_latest`
and `gex_snapshots`, deliberately, because GEXBot Classic is paid and the
dashboard is served from a public site.

### Options, least privilege first

**A. A Firebase Auth user for the session (recommended).** Two env vars — the
public web `apiKey` and an account email/password. Sign in through the Auth
REST endpoint, read Firestore over its REST API. **No library to install and no
rule changes.** Security rules still apply, and since both collections are
`allow write: if false`, the access is **read-only by construction**. This is
the dashboard's existing trust model, reused.

**B. `FIREBASE_SERVICE_ACCOUNT_JSON` in the session env (quickest, widest).**
Mirrors the workflow. But be clear about what it grants: **the Admin SDK
bypasses security rules entirely** — full read *and write* across the whole
project, including the trade journal, not just the two GEX collections. That is
a large grant for a read-only need, and it is the reason A is preferred rather
than a matter of taste. Also needs `google-cloud-firestore` installed.

**C. Give this session nothing; let Actions do the comparison.** The recorder
already runs where the credentials are. It could compute the H12 grading there
and commit only the **verdict** — held/broke/chopped counts — rather than the
feed itself, which keeps `recorder.md`'s no-republishing rule intact. Slowest
to build, but needs no new credential anywhere.

**Until one of these exists the brief reads GEXBot live on every scan**, which
works today. What it cannot do is look back at days when no scan was run —
which is the entire reason to want the archive.


---

## 10. What the archive can and cannot answer (verified 2026-09-05)

*The read that made this checkable is recorded in §11; this section is what
that read implies for anything built on the archive.*

The recorder stores the **compact record** in `gex_snapshots` and the
142-strike ladder only in `gex_latest`, which is overwritten every poll.
Appending the ladder to history would cost roughly 1 GB/month, so the trade is
correct — but it has an analytical consequence worth stating plainly:

> **Per-strike history is never retained. Any question needing the full ladder
> at a past timestamp cannot be answered from this archive at all — not now,
> not later.**

That is fine for H12's headline claim (volume wall vs OI wall), which lives
entirely in the compact fields. It permanently rules out retro-grading the
ranked **C1–C3 / P1–P3** ladder, which is what `gex_retro.py --ladder`
consumes. **An archive reader must therefore not reuse that flag** — it would
promise a comparison the data cannot support. A separate path, with its output
marked walls-only, keeps the limit enforced rather than remembered.

Two further notes for whoever builds that reader:

- **The index/CFD offset reconstructs itself.** Each snapshot carries both
  `spot` and `source_ts`, so
  `offset = CFD_close_of_the_M5_bar_covering(source_ts) − snapshot["spot"]`.
  Per-snapshot, not per-day — the basis drifts intraday. If no bar covers
  `source_ts` within a bar-width, **skip that snapshot**: a wrong offset shifts
  every level uniformly and therefore looks entirely plausible. This is the
  same failure that put 14.5pts on every level when the offset was taken
  against a live price instead of a matched one.
- **Any `generated_utc` must be the feed's `source_ts`, never `fetched_at`.**
  The retro clips bars to those after publication to prevent look-ahead; using
  the read time (14:48Z Saturday, for a Friday-close feed) would grade levels
  against price action that predates them — the exact look-ahead bug that
  survived once by luck and is recorded in D5.
---

## 11. Firestore read achieved — and what the archive actually contains

Checked 2026-09-05, after `FIREBASE_SERVICE_ACCOUNT_JSON` was added to the
session environment (option **B** from §9). This section records a **real
read**, not an inference.

### The credential is well formed

It parses as **strict JSON**. `json.loads(raw)` succeeds with no fallback, and
`firestore_sink._candidates()` yields only `"as stored"` — the lenient
`strict=False` repair path in `Gex-Bot/scripts/firestore_sink.py` is **not**
exercised. `private_key` decodes to 28 real newlines from properly escaped
`\n`, and begins and ends with intact PEM guards.

This matters because the sink would have *worked either way*: it repairs a
mangled secret and only warns on stderr. A secret that works via the fallback
is still stored malformed. **This one is not** — the secret is clean.

Two container fixes were needed, neither of them a project defect:

- `google-cloud-firestore` is absent (as §9 predicted) — `pip install` fixes it.
- The distro `cryptography` 41.0.7 at `/usr/lib/python3/dist-packages`
  **panics** (`pyo3_runtime.PanicException`) the moment `google.oauth2` imports
  it, which kills any credentialed call before it is made. It cannot be
  uninstalled (Debian-managed, no RECORD file);
  `pip install --upgrade --ignore-installed cryptography` shadows it and
  resolves it. Worth knowing, because the failure looks like a credential
  problem and is not.

gRPC reaches Firestore through the agent proxy without special handling.

### What is in there: four documents, one instant

| | |
|---|---|
| `gex_latest` | **4 docs** — `SPX_zero`, `NDX_zero`, `NQ_NDX_zero`, `ES_SPX_zero` |
| `gex_snapshots` | **4 docs** — same four symbols, one timestamp each |
| Distinct `source_ts` | **2** — `1788551999` and `1788552000` |
| Date range | a single point: **2026-09-04 19:59:59–20:00:00Z** (Friday's close) |
| Distinct `fetched_at` | **1** — `2026-09-05T14:48:53Z` |
| Scopes | `zero` only |

So the archive holds **exactly one poll**: run 7, the manual `workflow_dispatch`
that §8 recorded as the first success. The two `source_ts` values are one
second apart and split by underlying, not by time — SPX/ES_SPX at `:20:00:00`,
NDX/NQ_NDX at `:19:59:59`. That is per-symbol feed staleness, **not** a refresh.

**Nothing has accumulated since.** The cron is `*/5 13-21 * * 1-5` and
2026-09-05 is a **Saturday**, so no scheduled run has ever fired. The first one
is Monday 2026-09-07 at 13:00Z.

§8's "the archive starts now" was right about the machinery and optimistic
about the calendar: what started was the *capability*, not the accumulation.

### The four documents are two observations, not four

`NQ_NDX` is `NDX` plus a constant **30.82**, and `ES_SPX` is `SPX` plus a
constant **6.13** — verified across `spot` and every wall, exactly. They are
basis-shifted representations of the same computation, so they carry **no
independent information**. The archive holds **two** underlyings at **one**
instant — and that instant is the same frozen Friday close already recorded
against H12 and H13.

**No new evidence exists. The session count for both hypotheses is unchanged.**

### The refresh-cadence question is NOT settled

`recorder.md` expected that "once a session of data exists, the distinct
`source_ts` values will show how often the feed actually updates". That test
**cannot run yet**: one poll of a frozen weekend feed yields one `source_ts`
per symbol and zero refresh events. Measuring an interval needs at least two
distinct values from the same symbol during RTH.

The 5-minute cron therefore remains **a guess, not a derived figure**. The
measurement becomes possible after the first RTH session — Monday 2026-09-07 —
and the query is one line: count distinct `source_ts` per ticker per day and
diff them.

### The ladder is missing from `gex_latest`, and the reason is benign

`recorder.md` says `gex_latest` carries the full 142-strike ladder. It does
not — the `ladder` key is **absent entirely** from all four documents.

This is not a defect. `git log` settles it:

| | |
|---|---|
| `faa8dd5` 14:46:14Z | "Store max_priors as maps" — contains **no** ladder code |
| **run 7** 14:48:53Z | the only successful write, from that commit |
| `30ccd88` 15:42:04Z | adds `build_ladder()` and `{**r, "ladder": ladder}` |

The ladder-writing code landed **54 minutes after** the only run that has ever
succeeded. The next successful poll will write it. Nothing needs fixing —
but until Monday proves it, the ladder path remains, like the Firestore write
path before it, **unexecuted end to end**.

### The one structural limit, and it constrains the H12 design

**`gex_snapshots` does not carry the ladder — by design, permanently.** Per
`recorder.md`, the 142-strike ladder goes *only* to `gex_latest`, which is
overwritten every poll, because appending it to the history would cost of the
order of a gigabyte a month.

The consequence for H12 is precise, and it cuts both ways:

- **Answerable from the archive**: the wall comparison. `major_pos_vol` /
  `major_neg_vol` against `major_pos_oi` / `major_neg_oi`, plus `zero_gamma`,
  are all in the compact per-timestamp record. This *is* H12's headline claim.
- **Not answerable from the archive**: the ranked **C1–C3 / P1–P3 ladder**
  comparison. Per-strike history is never retained, so a retro grading of the
  full ranked ladder on a day no scan was run is **impossible** — not merely
  unimplemented. Only `gex_latest`'s single live snapshot ever holds it.

Any wiring that promises retro ladder grading is promising something the
archive cannot supply. The wall grading it *can* supply is enough for H12.

### The frozen snapshot, read directly

| doc | spot | zero_gamma | Δ | pos_vol | pos_oi | neg_vol | neg_oi | regimes_agree | walls_agree |
|---|---|---|---|---|---|---|---|---|---|
| `NDX_zero` | 29542.65 | 29542.65 | **0.00** | 29530 | 29500 | 29580 | 29600 | True | False |
| `NQ_NDX_zero` | 29573.47 | 29573.47 | **0.00** | 29560.82 | 29530.82 | 29610.82 | 29630.82 | True | False |
| `SPX_zero` | 7717.85 | 7712.50 | 5.35 | 7720 | 7715 | 7710 | 7720 | False | False |
| `ES_SPX_zero` | 7723.98 | 7718.63 | 5.35 | 7726.13 | 7721.13 | 7716.13 | 7726.13 | False | False |

One observation is worth flagging for **H13**, without promoting it to
evidence. On the *same feed at the same instant*, `zero_gamma` equals `spot`
to the cent on NDX but sits **5.35 below** it on SPX. A field that is stubbed
to spot could not differ on SPX. So the field is **computed, not a stub** —
which is the direction H13's `gex_one` observation already pointed.

That is an argument against the *stub* reading. It is **not** an argument that
NDX's value is a usable flip: a computed value that lands exactly on spot is
still useless as a flip, and on NDX — the only symbol that matters here — it
did exactly that. `walls_agree` is **False on all four**, which is the
disagreement H12 exists to adjudicate, and the volume walls (50pts apart)
bracket spot far more tightly than the OI walls (100pts apart).

**H13's threshold remains 5 RTH samples. This is still the same one frozen
snapshot. Status unchanged: OBSERVING, do not use as the flip.**
