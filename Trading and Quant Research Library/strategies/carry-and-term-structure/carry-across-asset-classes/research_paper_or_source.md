# Carry Across Asset Classes

**Category:** Carry & Term Structure — *the first entry in this category*
**Anchor paper:** Koijen, R. S. J., Moskowitz, T. J., Pedersen, L. H., & Vrugt, E. B. (2018).
"Carry." *Journal of Financial Economics*, 127(2), 197–225.

---

## 1. Abstract / summary of the core edge

Carry is what an asset returns **if its price does not change**. A bond's yield plus roll-down. A
commodity's convenience yield net of storage. A currency's interest-rate differential. A stock's
dividend yield. Buy the assets with high carry, short the ones with low carry.

The paper's contribution is to show these are **the same trade**, and that a single model-free
characteristic predicts returns everywhere:

> "We apply the concept of carry, which has been studied almost exclusively in currency markets, to
> any asset. A security's expected return is decomposed into its 'carry,' an ex-ante and model-free
> characteristic, and its expected price appreciation. Carry predicts returns cross-sectionally and
> in time series for a host of different asset classes, including global equities, global bonds,
> commodities, US Treasuries, credit, and options."

The headline results:

| Strategy | Annualised Sharpe |
|---|---|
| Cross-sectional carry, **average across asset classes** | **0.8** |
| **Diversified portfolio of carry strategies, all asset classes** | **1.2** |
| Carry *timing* strategies, average | 0.6 |
| Global carry timing, all asset classes combined | 0.9 |

Two things make this the right anchor for the category rather than one of the many single-asset carry
papers:

1. **It unifies a fragmented literature.** The authors point out that "seemingly unrelated predictors
   of returns across different assets can be bonded together through the concept of carry." Bond
   carry is the yield-curve slope plus roll-down. Commodity carry is the basis or convenience yield.
   Equity carry is a forward-looking dividend yield. These were separate literatures; this paper shows
   they are one measurement applied to different contracts.
2. **Carry often subsumes the other predictors, not the reverse.** "Carry provides unique return
   predictability. However, in many cases, the reverse is not true. Carry often subsumes the return
   predictability of other known factors." That is a strong claim and the reason carry belongs in a
   library rather than being folded into an existing entry.

The finding that constrains any naïve implementation: **carry has a hidden common factor that only
shows up at low frequency.** The three biggest global carry drawdowns — **August 1972 to September
1975, March 1980 to June 1982, and August 2008 to February 2009** — all coincide with major global
recessions, and during them *every* carry strategy performs poorly and "significantly worse than
passive exposures to these same markets." Monthly correlations between carry strategies look modest;
that modesty is misleading.

## 2. Source links

| Source | Type | Link |
|---|---|---|
| Koijen, Moskowitz, Pedersen & Vrugt (2018), JFE — full text (verified in-session) | paper | https://spinup-000d1a-wp-offload-media.s3.amazonaws.com/faculty/wp-content/uploads/sites/3/2019/04/Carry.pdf |
| NBER Working Paper 19325 | paper | https://www.nber.org/system/files/working_papers/w19325/w19325.pdf |
| SSRN version | paper | https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2298565 |
| CBS accepted manuscript | paper | https://research-api.cbs.dk/ws/files/57294842/lasse_heje_pedersen_et_al_carry_acceptedmanuscript.pdf |
| Moskowitz, Ooi & Pedersen (2012) — the trend-following sibling | paper | https://w4.stern.nyu.edu/facdir/lpederse/papers/TimeSeriesMomentum.pdf |

## 3. Mathematical foundation

### 3.1 The definition

For a **fully collateralised futures position**, where the capital committed equals the futures
price (`X_t = F_t`):

```
C_t = ( S_t − F_t ) / F_t
```

with `S_t` the spot price and `F_t` the futures price. The excess return is computed consistently as
`r_{t+1} = (F_{t+1} − F_t) / F_t`.

The elegance is that this is **one formula for every asset class**. What changes is only which
contract you plug in:

| Asset class | Carry corresponds to |
|---|---|
| Currencies | Interest-rate differential (the classic carry trade) |
| Global bonds | **Yield-curve slope + "roll down"** — the price change as the bond ages along the curve |
| Commodities | Basis / convenience yield net of storage |
| Global equities | A forward-looking dividend yield, derived from futures prices |
| US Treasuries | Carry across the maturity cross-section |
| Credit | Spread carry |
| Options | Carry across moneyness |

The paper emphasises that carry is **ex ante and model-free** — it is observable today from prices,
requiring no estimation, no regression, and no model of expected returns. That is a genuine
advantage over most predictors in this library, which need parameters fitted on history.

### 3.2 The return decomposition

```
E[return]  =  carry  +  E[price appreciation]
```

This is an identity, not a theory. The empirical question is what the coefficient on carry is when
you regress future returns on it:

| Coefficient | Interpretation | Where observed |
|---|---|---|
| **> 1** | Carry predicts *additional* price appreciation on top of the carry itself | **Global equities, global bonds, credit** |
| **< 1** but > 0 | The market "takes back part of the carry" — but not all of it, contradicting uncovered interest parity and the expectations hypothesis | **Commodities, options** |

Both cases are profitable; they differ in mechanism. A coefficient above one means high-carry assets
also tend to appreciate — the opposite of what textbook parity conditions predict. A coefficient
between zero and one means the classic carry-trade story: you collect the carry, give some back in
price, and keep the difference.

### 3.3 Position sizing

Positions are fully collateralised (`X_t = F_t`), so carry scales linearly with position size — "for
an investor who uses twice the leverage, both the return and the measured carry naturally double."
Where asset volatilities differ substantially in the cross-section, the authors choose position sizes
"that put the various assets on a comparable scale," i.e. volatility scaling of the kind used in the
TSMOM entry.

### 3.4 Why the edge should exist

The paper tests the obvious risk-based explanations and finds all of them **partially** relevant and
none sufficient. From the abstract: carry captures exposures to "global recession, liquidity, and
volatility risks, though **none fully explains carry's premium**."

The strongest evidence for a risk story is the drawdown structure in §1: carry loses in global
recessions, uniformly across asset classes, and loses *more* than passive exposure to the same
markets. That is what a risk premium should look like — you get paid on average for taking losses
precisely when losses hurt most.

The strongest evidence against a pure risk story is that the Sharpe ratios are too high (1.2 for the
diversified portfolio) to be plausible compensation for the measured exposures, which is the same
puzzle Daniel & Moskowitz raise about momentum's 22.3% alpha.

## 4. Known criticisms and limitations

1. **The drawdowns are correlated in a way monthly data conceals.** The authors are explicit: "This
   lower frequency co-movement is obscured when considering monthly returns. Hence, the modest
   unconditional pairwise correlations mask some important dynamics." Any risk model built on monthly
   correlations across carry strategies will materially understate the joint tail risk.
2. **Three drawdowns is a thin basis for characterising the tail.** 1972–75, 1980–82, 2008–09 are the
   identified episodes. As with the momentum-crashes entry, conditioning on a handful of events is a
   real statistical limitation, mitigated here by the breadth across asset classes rather than by
   sample length.
3. **Carry trades are short volatility and short liquidity.** The currency carry literature documents
   this extensively — high-carry currencies crash. The paper's own liquidity and volatility exposures
   are consistent with it. The returns are negatively skewed in the same way momentum's are.
4. **Implementation requires futures or forwards across seven asset classes.** This is not a
   retail-accessible strategy. It needs futures accounts, margin, roll management, and the operational
   capacity to hold dozens of positions.
5. **Roll and transaction costs are material and the headline figures are the paper's own
   construction.** A strategy trading global futures monthly across seven asset classes incurs real
   roll cost. Price the turnover using `../../execution-and-cost/almgren-chriss-optimal-execution/`
   before treating a 1.2 Sharpe as achievable.
6. **Post-publication crowding.** Carry is now a standard factor offered in systematic multi-asset
   products. The 2018 publication date is recent enough that meaningful post-publication
   out-of-sample evidence is still limited, but the same decay logic that applies to every published
   factor applies here.
