# Ladder preview harness

Renders `GexBotView` against a real recorded session so the chart can be
**looked at**, not just typechecked. Building it blind is how four visual bugs
shipped last time; the first render of this rewrite showed no chart at all --
an SVG with only a viewBox collapses to zero height inside a flex row.

Serve the dashboard with Vite on any free port and open
`/CTrader-Bots/xauusd-dashboard/preview.html`.

> When killing that dev server afterwards, do not put the server's command
> line inside the same shell invocation as a `pkill -f` for it: `pkill`
> matches its own parent's command line and takes out the shell. That has now
> happened twice.

## The fixture is deliberately not committed

`gexFixture.json` is a full 142-strike ladder plus a session of spot samples --
paid vendor data, licensed for personal, non-commercial use with no
redistribution. This repository is public, so the file is gitignored. Rebuild
it from an EOD report you already hold: read the `gex_zero` and `gex_full`
members of the zip, take the last sample of each as `zero` and `full` (adding a
`ladder` list of `{strike, gex_vol, gex_oi, priors}` mapped from `strikes`),
and sample every 300 seconds for the `history` price series.

Without the file the page renders nothing. That is the intended failure, not a
bug.
