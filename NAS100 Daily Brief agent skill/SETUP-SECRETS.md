# Secrets & environment setup

**No secret value belongs in this repository.** Everything here is read from the
environment at runtime, and the repo carries only names and instructions.

| Variable | Needed for | Where to get it |
|---|---|---|
| `CTRADER_MCP_SLUG` | NAS100 CFD prices, levels, ADR/fuel (`levels_fuel.py`) | Already set in this repo's sessions. The base64url `eyJwb…` slug — see `ctrader-mcp-integration-guide.md` |
| `FRED_API_KEY` | Real yields, breakevens, credit spreads, financial conditions, Fed liquidity (`fred_probe.py`) | Free, instant, no card: https://fredaccount.stlouisfed.org/apikey |

`FRED_API_KEY` is **optional**. Without it the brief still runs end to end —
it degrades to nominal yields only, and says so out loud in the output rather
than silently dropping the layer.

---

## Where to set them

### 1. Claude Code environment settings (persists across sessions — do this one)
Add both as environment variables in your Claude Code environment settings.
This is the path that makes `python3 brief.py` work in any future session
without re-exporting anything.

### 2. GitHub Actions repo secret (for the Phase-2 scheduled job)
`Settings → Secrets and variables → Actions → New repository secret`, named
exactly `FRED_API_KEY` and `CTRADER_MCP_SLUG`. The workflow injects them as
env vars; they never appear in the workflow file or the job log.

### 3. One-off, this shell only
```bash
export FRED_API_KEY="your-key-here"
cd "NAS100 Daily Brief agent skill/prototypes" && python3 brief.py
```

---

## A note on the FRED key specifically

The FRED key was shared in chat during Phase 1. It is a free, read-only key to
public data with no personal information behind it and no billing attached, so
the exposure is genuinely low — but a chat transcript is not a secret store.
If you'd rather not leave it there, regenerating it takes about ten seconds at
the link above; nothing in this repo hardcodes it, so a new key needs no code
change at all — just update the two places in §1 and §2.

The cTrader slug is a different matter: it authenticates a **trading account**.
Keep it in the environment and in GitHub secrets only, never in a file, never
in chat.
