# Engine build decisions

Per build-spec §0: where the spec says SHOULD/MAY, or where reality contradicted the
spec, the decision is recorded here. Newest first.

---

## M1 — plumbing (2026-07-28)

### Deviations from `02-Build-Specification.md`

These follow `03-Verification-Findings.md`, which tested the assumptions empirically.

| Spec said | Engine does | Why |
|---|---|---|
| `commission_per_lot` | `commission_per_million` (and rejects the old key with a pointed error) | The CLI's `--commission` is documented as "commission per million" |
| .NET 8 SDK for compilation | `dotnet_target: net6.0` | The console image ships runtime 6.0.10 and no SDK; a net8.0 `.algo` will not load |
| image `:latest` | `ctrader_console_tag` required, `latest` rejected | Reproducibility, and ghcr's `latest` returned 503 twice during testing |
| `min_trades_per_year: 30` default | default raised to 100 | 30/yr over an 18-month IS window is ~45 trades; an annualised daily Sharpe from that is noise |
| period `m1` in the example study | validated case-sensitively against the real `periods` list | `D1`/`W1`/`Month1` are capitalised; the CLI's own `--help` gets this wrong |
| `data_start: 2021-01-04` | `2021-07-18` | The repo's XAUUSD series actually begins 2021-07-18 |

### Choices made where the spec was silent

- **`results.py` added** as a separate module. The spec put the canonical result
  structures inside `ctcli.py`; splitting them means the fixture-fake and the real
  CLI wrapper produce identical objects, and every module above the execution layer
  can be built and tested with no credentials. Given that real backtests cannot run
  in a web session at all, this is load-bearing rather than cosmetic.
- **`full.csv` written alongside `insample.csv`/`holdout.csv`.** Needed for the
  same-bar SL/TP ambiguity detection in Monte Carlo (§11), which has to look at bars
  the backtest saw. It is never passed to a pre-holdout backtest.
- **Degeneracy guard in `metrics.py`.** `std([0.01]*10)` is ~1.7e-18, not 0, so an
  `sd == 0` check let a flat equity curve score a Sharpe of 8.7e16 — which would win
  any search outright. Ratios now treat a standard deviation below `1e-12 * max(1,
  |mean|)` as degenerate and return 0.0. Sortino is deliberately *not* guarded the
  same way: it divides by downside RMS, so a constant-loss series has a legitimate
  non-zero denominator.
- **Weekend gaps are not warned about.** Friday-close to Sunday-open is normal; the
  audit only reports non-weekend gaps over an hour. On the real XAUUSD series this
  leaves 1,035 gaps, and inspection shows they are Easter, Christmas and New Year
  closures — i.e. the data is clean.
- **Day-filter parameters are pinned in `fixed:`** in the shipped search space, with
  a comment explaining why. Per 01-Research §4.1 they are never to be optimised.

### Still unverified — needs a connected host

1. The exact datetime format `--data-mode=m1-csv` accepts. The engine emits
   `yyyy-MM-dd HH:mm:ss` per the spec; confirm with a one-week backtest.
2. Whether `--CustomParameter1=<name>` is literal or a placeholder for the
   parameter's own name. This determines whether `.cbotset` generation is needed
   at all.
3. Whether `Events.json` carries intra-trade equity marks or only closed trades.
   `results.reconstruct_equity` handles the latter and tags the result
   `equity_source="reconstructed"`, which must surface in the report's LIMITATIONS.
4. Whether `CTRADER_CID`'s value is accepted as a cTID (it is 26 characters and not
   an email address).
5. Wall time per backtest — the M3 throughput gate. Every budget in `study.yaml` is
   provisional until this is measured.
