# Secrets & environment setup

**No secret value belongs in this repository.** Everything is read from the
environment at runtime; the repo carries only names and instructions.

| Variable | Needed for | Required? |
|---|---|---|
| `CTRADER_MCP_SLUG` | NAS100 CFD prices, levels, ADR/fuel (`levels_fuel.py`) | Yes — already set in this repo's sessions |
| `FRED_API_KEY` | Real yields, breakevens, credit spreads, financial conditions, Fed liquidity (`fred_probe.py`) | **Optional.** Free: https://fredaccount.stlouisfed.org/apikey |

Without `FRED_API_KEY` the brief still runs end to end — it degrades to nominal
yields and **says so in the output**. Verified both paths.

---

## ⚠️ Read this before putting a key in a cloud environment

The Claude Code docs are explicit
([cloud-environments → Set environment variables](https://code.claude.com/docs/en/cloud-environments#set-environment-variables)):

> "Anyone who uses the environment can read the values, and cloud environments
> have no dedicated secrets store, so don't add API keys or other credentials."

That guidance is aimed at shared and organization environments. For a personal
environment the practical exposure is limited to your own account — but the
right call differs sharply by credential:

| Credential | Verdict |
|---|---|
| **`FRED_API_KEY`** | Acceptable risk in a **personal** environment. It is free, read-only, public data, no billing attached, no personal information. Worst case someone burns your rate limit. Regenerating takes ten seconds and needs no code change |
| **`CTRADER_MCP_SLUG`** | **Different category — this authenticates a trading account.** It is already set in this environment. If that environment is ever shared with anyone, or made organization-shared, rotate it first. Prefer a **demo-plant** slug for anything scheduled or automated, and keep the live-account slug out of cloud environments entirely |

---

## Where to set them

### 1. Cloud environment (persists across sessions) — for `FRED_API_KEY`
1. Go to **[claude.ai/code](https://claude.ai/code)** — environments are managed
   there (`/remote-env` in the CLI only *selects* a default, it can't edit one).
2. Open the environment this repo's sessions use and edit it.
3. In the environment-variables box, add one `KEY=value` per line, `.env` format:
   ```
   FRED_API_KEY=your-key-here
   ```
   Plain values need no quotes. Quote anything containing a `#`, or the rest of
   the line is treated as a comment and dropped.
4. Save.

**Applies to new sessions only.** Each session copies the values once at
startup, so a session already running keeps what it started with. Start a fresh
session to pick up the change.

### 2. GitHub Actions repo secret — for the Phase-2 scheduled job
This *is* a proper secrets store, and it's the right home for anything the
scheduled brief needs.

`Settings → Secrets and variables → Actions → New repository secret`, named
exactly `FRED_API_KEY` (and `CTRADER_MCP_SLUG` if the job needs live prices).
The workflow injects them as env vars; they never appear in the workflow file
or the job log.

### 3. One-off, current shell only
```bash
export FRED_API_KEY="your-key-here"
cd "NAS100 Daily Brief agent skill/prototypes" && python3 brief.py
```

---

## Rotating the FRED key

The key was shared in a chat transcript during Phase 1. Nothing in this repo
hardcodes it, so rotating needs **no code change** — generate a new one at the
link above and update the two places in §1 and §2. Ten seconds.
