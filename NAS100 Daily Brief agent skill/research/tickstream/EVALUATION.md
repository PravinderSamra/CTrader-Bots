# tick-stream.xyz — evaluation

Tested 2026-08-27 ~22:10 UTC (inside the CME daily break, which limits the
futures half of the test).

Three things were assessed: the free GEX levels page, the MCP connector, and the
API key. They are all the same vendor — the key is embedded in the MCP URL.

---

## 1. The MCP connector — connects, but the useful tools are gated

`list_symbols` works unauthenticated-in-practice and the coverage is exactly
ours:

- **Futures:** ES, **NQ**, YM, RTY, CL, GC, ZN, FDAX… (38)
- **Options:** ES, NQ, SPX, **NDX**, RUT, VIX, SPY, **QQQ**, IWM, DIA

| Tool | Result |
|---|---|
| `list_symbols` | ✅ works |
| `get_quote` | permitted — returned *"no ticks (market may be closed)"* for NQ **and** ES. Tested inside the 21:00–22:00 UTC CME break; **retest during RTH before concluding** |
| `get_options` | ❌ `plan_required` — Options Core, **$29/mo** |
| `get_book` | ❌ `plan_required` — Realtime + L2, **$79/mo** |

**Free tier = "delayed, but the same feed": 15-minute delay, all 60+ markets,
7-day tick backfill, MCP included.**

## 2. The free GEX page — rich, and deliberately not machine-readable

`/free-gex-levels-realtime` genuinely carries things we do not have. From the
page itself:

| Feature | Us | Them |
|---|---|---|
| Call wall / put wall / zero-gamma flip | ✅ | ✅ |
| Expected move (ATM straddle) | ✅ | ✅ |
| Per-strike GEX ladder | ✅ | ✅ |
| **GEX weighted by VOLUME, not just OI** | ❌ | ✅ |
| **0DTE / 1DTE filters** | ❌ (tested, rejected as R1 — on OI) | ✅ |
| **Vanna and charm** | ❌ (rejected as R2 — not levels) | ✅ |
| **DEX (delta exposure)** | ❌ | ✅ |
| **Walls plotted as they MOVED through the session** | ❌ (this is the live-walls research question) | ✅ |
| **Largest option orders at their strike** — call/put, bought/sold, sweeps | ❌ | ✅ |
| **Customer vs market-maker split** | ❌ | ✅ |

**Programmatic access is blocked, explicitly.** The page fetches
`/api/gex-levels?symbol=NQ`; called directly it returns:

```
HTTP 403  {"error": "use_the_api",
 "message": "This feed powers the free tick-stream.xyz chart.
             For programmatic access, the computed GEX is a paid API"}
```

That is an access control the operator put there and explained in words. **Not
circumvented, and it should not be** — the page is free to look at, the data is
the product. Two of the site's own nav items are "Pricing" and "Products &
redistribution".

## 3. The single most useful thing found — a confirmation, not a feature

Their **Options Flow** tier at $69/mo lists *"Daily open-interest history"*.
Their tick-level OPRA product, at $69/mo, still only offers **daily** OI.

**That independently confirms the central constraint of this project: nobody
sells real-time open interest, at any price.** It was asserted earlier from the
OCC's publication schedule; this is a commercial vendor with tick-level OPRA
access pricing it the same way. The `live-walls/` research is aimed at the right
problem, and no purchase removes it.

---

## What would actually be worth buying, ranked

### 1. GEX Full — $69/mo. The reason is the archive, not the levels.

*"12 years of historical GEX, minute-sampled"*, plus 0DTE/1DTE filters and
single names.

**This is the big one, and it has nothing to do with live data.** The register
currently holds 4 trading days. H4 and H6 need 5, H8 needs 10, H11 needs 3
ladder tests, and the wall-to-wall strategy has never been backtested at all.
Twelve years of minute-sampled GEX turns *"collect evidence for a fortnight"*
into *"test it this afternoon"* — and it would let the withdrawn and open
hypotheses be settled properly rather than one session at a time.

The measurement discipline this project runs on is currently rate-limited by the
calendar. This removes that.

### 2. GEX + Greeks — $39/mo, if the history is not wanted.

Adds the **OI-or-volume lens**, DEX, vanna, charm, and per-strike call/put split
with 5 sessions of history.

The volume lens matters specifically because it is the thing we **could not
build honestly**: volume has no sign, so weighting walls by it stacks an
assumption on an assumption (documented when the idea was rejected). They have
real trade data and can sign it.

### 3. Options Core — $29/mo. Least valuable *for us*.

Live chain + live greeks. We already recompute greeks with Black-Scholes at the
current spot, correctly, because CBOE's published ones are stale. This would
remove that workaround — a simplification, not a capability.

### Not worth it here

**Realtime + L2 ($79)** and **L3 ($199)** are order-flow microstructure. Neither
of the two entry models trades off book depth, and neither would be improved by
it.

---

## The catch nobody mentions: it is a different book

Their futures GEX is computed on **NQ options**. Ours is **NDX index options +
QQQ**, converted to the NAS100 CFD.

Those are different underlyings with different open interest, so **their walls
will not match ours** and the difference is not an error in either. Integrating
them means reconciling two books, and "which book predicts the NAS100 CFD
better" is itself an open research question — not a free win.

**Recommended first step if anything is bought: run both side by side for a week
and grade them against price, before either is trusted or blended.** Exactly the
discipline in `journal/HYPOTHESES.md`.

## Free tier, what it is actually good for

One thing, and it is small: **NQ futures quotes as a cross-check on the Yahoo
`NQ=F` fetch** used by `_nq_implied_cash()` to roll a stale NDX cash print
forward. Both are ~15-minute delayed, so it is redundancy rather than an
upgrade — worth having only because that Yahoo call is a single point of failure
in a path that, when it broke before, inverted a trade call.

**Untested:** `get_quote` returned no ticks for both NQ and ES during the CME
break. Retest during RTH before relying on it for anything.

## Security note

The API key was pasted into chat and is embedded in the MCP connector URL. It is
a live credential — rotate it if that exposure matters. It has been used here
only against the vendor's own endpoints.
