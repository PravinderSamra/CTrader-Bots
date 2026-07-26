# Phase 1b — Verification Findings (empirical)

**Date:** 2026-07-26 · **Method:** actually pulled and ran the cTrader CLI container,
inspected the repo data, probed network and credentials.
**Purpose:** confirm or correct the assumptions in `01-Research-Findings.md` and
`02-Build-Specification.md` *before* implementation starts. Several Stage-0 "discovery
tasks" listed in the build spec are answered here — they no longer need discovering.

Image tested: `ghcr.io/spotware/ctrader-console:5.9.0.0` (pulled successfully).

---

## 1. Verdict on the architecture

**The Option C decision holds.** The official CLI is real, does what the research doc
claims, and is fully non-interactive in batch mode — it is genuinely agent-operable.
No change to the fundamental design is needed.

Confirmed by direct execution:

| Claim in research doc | Status |
|---|---|
| `ghcr.io/spotware/ctrader-console` exists as a Linux image | ✅ pulled; 24 tags published (`5.4` … `5.9.0.0`, `latest`) |
| `--data-mode=m1-csv` for user-supplied M1 CSV | ✅ real. Full mode list: `ticks \| m1 \| m1-csv \| open` |
| Machine-readable output | ✅ `--report-json=<path>` exists (was listed as an open question) |
| Headless `backtest` subcommand | ✅ batch mode, all claimed flags present |
| Requires cTID login even for backtests | ✅ `--ctid` + `--pwd-file` + `--account` are mandatory |
| Parameter injection without touching source | ✅ **and simpler than assumed** — see §3.4 |

Verified `backtest` signature (from the image's own `--help`):

```
dotnet backtest <cbot.algo> [<params.cbotset>] --start=<dd/MM/yyyy> --end=<dd/MM/yyyy>
      --data-mode=<mode> [--data-file=<path>] [--balance=<n>] [--commission=<n>]
      [--spread=<pips>] [--report=<path>] [--report-json=<path>]
      --ctid=<cTID> --pwd-file=<path> --account=<n> --symbol=<n> --period=<p>
      [--CustomParameter1=<v>] [-e]
```

---

## 2. Blocking realities the Phase 1 docs do not mention

### 2.1 The engine cannot be run end-to-end from a Claude Code web session

The CLI authenticates over direct TCP to Spotware endpoints. Measured in this sandbox:

- `demo.ctraderapi.com:5035` — **blocked** (DNS resolves; TCP connect fails)
- `demo.ctraderapi.com:5036` — **blocked**
- `live.ctraderapi.com:5035` — **blocked**
- HTTPS via the agent proxy — works (that is how the remote MCP reaches cTrader)

Running `backtest`/`accounts` in the container therefore fails with
`Connection can't be established`, regardless of whether credentials are correct.

**Consequence for the build plan.** Split the work by whether it needs the CLI:

- *Buildable and testable in a web session (no CLI, no credentials):* `config.py`,
  `data.py`, `metrics.py`, `optimise.py` (against a fixture-backed fake runner),
  `walkforward.py`, `plateau.py`, `montecarlo.py`, `overfit.py`, `gates.py`,
  `report.py`, and the entire unit-test suite. This is the large majority of the code.
- *Requires a host with open egress (your machine or a VPS):* `ctcli.py` integration,
  `compile.py`, `smoke`/parity, and **every real backtest** — i.e. milestones M2/M3
  integration onward.

The build spec's milestone M1 is already credential-free, which is correct. M2 should
be explicitly re-labelled "runs on the trader's host, not in a web agent session", and
the recorded-fixture fake of `ctcli` (already specified in M2) becomes the critical
path for everything else, not a nicety.

### 2.2 Docker daemon is not running by default in a web session

`dockerd` is installed but no daemon/socket exists until started
(`sudo dockerd --iptables=false &`). Worth one line in the README so this isn't
rediscovered each session.

### 2.3 Registry flakiness — pin the tag

`docker pull …:latest` failed twice with `503 Service Unavailable` from ghcr.io
(once mid-blob, once on the manifest HEAD). Pulling the pinned tag `5.9.0.0`
succeeded. **Pin the image tag in `study.yaml`** — needed for reproducibility anyway,
and it avoids the flakier `latest` path.

---

## 3. Corrections to `02-Build-Specification.md`

### 3.1 The data window in the example `study.yaml` is wrong

Spec says `data_start: 2021-01-04`. Actual repo data:

| File | Rows | Range |
|---|---|---|
| `XAUUSD_M_1_2021.csv` | 163,053 | **2021-07-18** → 2021-12-31 |
| `XAUUSD_M_1_2022.csv` | 352,085 | 2022 full |
| `XAUUSD_M_1_2023.csv` | 348,605 | 2023 full |
| `XAUUSD_M_1_2024.csv` | 355,177 | 2024 full |
| `XAUUSD_M_1_2025.csv` | 353,094 | 2025 full |
| `XAUUSD_M_1_2026.csv` | 190,474 | 2026 → **2026-07-16** |

So coverage is **2021-07-18 → 2026-07-16 (~5.0 years)**, not 5.5, and 2021 is a half
year. Set `data_start: 2021-07-18`.

The WFA geometry still works: with IS=18/OOS=6/step=6 over 2021-07-18 → 2025-07-01 you
get **5 complete folds**, concatenated OOS = 2023-01 → 2025-07 (30 months), holdout =
2025-07-01 → 2026-07-16 (12.5 months). That is at the low end of the research doc's
"5–6 folds" claim, so the claim stands — but note the honest OOS sample is 30 months,
and the "2021–22 range regime" fold only starts mid-July 2021.

Format confirmed as described: `datetime,open,high,low,close,volume` with header,
ISO `2021-07-18T22:00:00Z` timestamps, tick-count volume.

### 3.2 Target framework: .NET 6, not .NET 8 — this will break the build as specified

The console image ships **runtime `Microsoft.NETCore.App 6.0.10` only, and no SDK**
(`dotnet --list-sdks` is empty; `DOTNET_VERSION=6.0.10`).

The spec's §1 says to compile with `mcr.microsoft.com/dotnet/sdk:8.0`. An `.algo`
targeting `net8.0` will not load in a 6.0.10 host. **Target `net6.0`**, or first verify
that a newer image tag ships a newer runtime. Confirm the loaded `.algo` runs before
building anything on top of it — this is a hard failure at M2 otherwise.

### 3.3 `--commission` is *per million*, not per lot

The options reference reads: `--commission=<value>   commission per million`.
The example `study.yaml` has `commission_per_lot: 0.0`. Rename and convert, or the
cost model is silently wrong the moment a non-zero commission is set.

### 3.4 `.cbotset` reverse-engineering may be unnecessary

Both the research doc (open question #4) and the build spec (§5.1) treat the `.cbotset`
JSON schema as an unknown that must be reverse-engineered from a GUI export. The CLI
offers a direct alternative:

- Batch mode: `--CustomParameter1=<value>` — *"set any cBot parameter by name"*
- Interactive: `--robot-params=<k=v,...>`
- `dotnet metadata <cbot.algo>` — prints parameter metadata extracted from the `.algo`

**Recommendation:** make CLI-flag parameter injection the primary path and treat
`.cbotset` as optional. This removes the spec's single largest unknown. Keep the
deterministic hash of the *resolved parameter dict* as the cache-key component
(§6) — that works identically either way.

Note the exact flag spelling (`--CustomParameter1` looks like a placeholder for the
parameter's own name) still needs one empirical check on a host with connectivity.

### 3.5 Batch auth uses `--pwd-file`; inline `--password` routes to interactive

Documented routing: passing `--password=<v>` forces the **interactive** shell, which
will block an agent. Batch mode requires `--pwd-file=<path>`. The engine must write the
password to a 0600 file at runtime (tmpfs preferred), never pass it inline.

The CLI also supports `-e` / `--environment-variables` to supply any option via env var
(e.g. `CTRADER_CLI_AUTHTOKEN`), which fits this repo's existing env-var convention —
worth testing as a cleaner alternative to the secrets YAML in spec §1.1.

### 3.6 Period tokens are case-sensitive and the help text is wrong about it

`dotnet periods` (no auth, no network — works offline) returns:

```
t1…t1000  m1 m2 m3 m4 m5 m6 m7 m8 m9 m10 m15 m20 m30 m45
h1 h2 h3 h4 h6 h8 h12  D1 D2 D3  W1  Month1  Re1…Ra…Hm…Hh…Hd…
```

Note `D1`, `W1`, `Month1` are **capitalised**, while the `--help` text claims
"d1, w1, month1". Validate `market.period` against live `periods` output; do not
hardcode from the help text.

### 3.7 The docs-vs-reality gap is real — trust execution, not documentation

`--help` states `create` and `build` need "No auth". In practice
`create cbot TestBot csharp` fails with `Missing --ctid in non-interactive mode`,
and `metadata /path.algo` fails argument parsing (`Unable to determine destination for
argument value`). The build spec's instruction to verify empirically and record in
`DECISIONS.md` is not bureaucracy — it is necessary. Keep it.

---

## 4. Methodology review

The anti-overfitting stack (walk-forward → plateau → Monte Carlo battery → DSR/PBO →
one-shot holdout → honest REJECT) is rigorous and well above typical retail practice.
The mandatory anti-fooling test (spec §16.4 — run the whole pipeline on a known-random
strategy and require REJECT) is the strongest single item in either document. The
holdout ledger and post-holdout study immutability are good discipline. No objection to
any of it.

Four substantive critiques:

### 4.1 `min_trades_per_year: 30` is far too low for a Sharpe-based objective

30 trades/year over an 18-month IS window is ~45 trades. An annualised daily Sharpe
estimated from that is close to pure noise, and Stage 1 will happily rank noise. Either
raise the floor substantially (100+/yr for a day-trading bot) or make the primary
objective expectancy-in-R with an explicit trade-count penalty, keeping Sharpe as a
reported metric. The current setting undermines the rest of the methodology.

### 4.2 Pin what DSR deflates by

Spec §12 computes DSR from "the trial log" without saying which. The number of trials
is the whole point of the statistic. It must deflate by the **total configurations
evaluated in the study** — Stage 1 (800) plus WFA folds (5 × 150 = 750) plus plateau
probes (~2·dims + 32) ≈ 1,600–1,800 — not Stage 1 alone. State this explicitly or the
gate is optimistic by roughly a factor of two in N.

### 4.3 Expect REJECT, and budget for it emotionally and practically

`DSR ≥ 0.95` **and** `PBO ≤ 0.25` on a ~30-month OOS sample is a demanding pair of
gates. That is the correct behaviour for an honest engine, but the realistic outcome
for the first bot is REJECT or CONDITIONAL. Running ThreeDownDaysBot first (as the spec
plans) is the right call precisely because it calibrates expectations cheaply.

### 4.4 Throughput is unquantified and is the biggest practical risk after credentials

Neither document estimates wall time for one backtest over ~1.76M M1 bars. The budgets
imply ~1,600–1,800 real backtests per bot-study. At 60s/run that is ~28 hours
single-threaded; at 5 minutes/run it is unworkable. **Add a hard gate to M3: measure
runs/hour on real data and re-derive the budgets in `study.yaml` from that number
before Stage 1 is allowed to start.** The caching design (§6) is sound and will help
substantially on plateau/repeat work.

---

## 5. Credentials status

Present in the environment: `CTRADER_CID` (26 chars, not an email — format unverified
against the CLI's "cTrader ID or email"), `CTRADER_ACCOUNT_ID` (7 digits),
`CTRADER_PASSWORD`, `CTRADER_MCP_SLUG`.

This materially advances README blocking item #1, but **none of it could be verified
here** because of §2.1 — `accounts --ctid=… --pwd-file=…` returns
`Connection can't be established`, which is a network failure, not an auth failure.
First task on a connected host: run `dotnet accounts` and confirm the cTID form and
account number are accepted.

**Separately — the remote cTrader MCP is failing auth, and a password change cannot fix
it.** `get_balance` → `401 cServer authentication failed`; `get_version` →
`session expired`. The MCP does not use the password: it authenticates with
`CTRADER_MCP_SLUG`, which decodes to
`{"plant":"pepperstoneuk","environment":"demo","token":"<44-char OAuth token>"}`.
That token has expired. It must be re-minted via the Open API OAuth flow and the slug
rebuilt:

```bash
echo -n '{"plant":"pepperstoneuk","environment":"demo","token":"<NEW_TOKEN>"}' \
  | base64 | tr '+/' '-_' | tr -d '='
```

The CLI path (`--ctid` + `--pwd-file`) and the MCP path (OAuth token) are two
independent auth mechanisms. **An expired MCP token does not block this engine** — the
engine only uses the CLI path.

---

## 6. Recommended changes before implementation starts

1. Fix `data_start` to `2021-07-18`; state the honest OOS sample as 30 months.
2. Change the compile target to `net6.0` (or verify a newer runtime in a newer tag).
3. Rename `commission_per_lot` → `commission_per_million` and convert.
4. Make CLI-flag parameter injection primary; demote `.cbotset` to optional.
5. Pin `ctrader_console_tag: 5.9.0.0` in `study.yaml`.
6. Raise `min_trades_per_year` or change the primary objective (§4.1).
7. Define DSR's N as the study-wide configuration count (§4.2).
8. Add the M3 throughput gate (§4.4).
9. Re-label M2 as host-only work and make the `ctcli` fixture-fake the critical path
   for all web-session development (§2.1).
