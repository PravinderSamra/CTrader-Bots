"""
Dollar-terms executive report. $100,000 account, FLAT $100 risk per trade => 1R = $100,
so trade $ = R * 100 (stop-size independent). Best config per instrument, RR = 2/2.5/3/3.5.

Outputs per instrument x RR: yearly / monthly / weekly $ tables + streaks, to analysis/dollar/.
"""
import os, sys, json
import pandas as pd
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sessions, backtest as bt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "analysis", "dollar")
os.makedirs(OUT, exist_ok=True)

RISK = 100.0          # $ per trade = 1R
ACCOUNT = 100_000.0
VOL = dict(vol_method="trailing", vol_mult=1.2)
VOLN = dict(vol_method="trailing", vol_mult=1.3)
RRS = [2.0, 2.5, 3.0, 3.5]

BEST = {
    "US30":   dict(range_ref="ny", lon_start=8.0, lon_end=9.5, bo_start=10.0, bo_end=13.0,
                   stop_method="fixed", stop_pts=75, **VOL),
    "NAS100": dict(range_ref="ny", lon_start=2.0, lon_end=9.5, bo_start=10.0, bo_end=11.0,
                   stop_method="fixed", stop_pts=40, **VOL),
}


def streaks(signs):
    """longest run of wins (+1) and losses (-1); 0 is neutral and breaks both."""
    best_w = best_l = cur_w = cur_l = 0
    for s in signs:
        if s > 0:
            cur_w += 1; cur_l = 0
        elif s < 0:
            cur_l += 1; cur_w = 0
        else:
            cur_w = cur_l = 0
        best_w = max(best_w, cur_w); best_l = max(best_l, cur_l)
    return best_w, best_l


def enrich(tdf):
    tdf = tdf.copy()
    tdf["dt"] = pd.to_datetime(tdf["date"])
    tdf = tdf.sort_values("dt").reset_index(drop=True)
    tdf["usd"] = (tdf["R"] * RISK).round(2)
    tdf["year"] = tdf["dt"].dt.year
    tdf["month"] = tdf["dt"].dt.to_period("M").astype(str)
    iso = tdf["dt"].dt.isocalendar()
    tdf["week"] = iso["year"].astype(str) + "-W" + iso["week"].astype(str).str.zfill(2)
    tdf["week_start"] = (tdf["dt"] - pd.to_timedelta(tdf["dt"].dt.weekday, unit="D")).dt.date
    return tdf


def yearly_table(tdf):
    rows = []
    for yr, g in tdf.groupby("year"):
        w, l = streaks(np.sign(g["R"]).tolist())
        wins = int((g["R"] > 0).sum()); losses = int((g["R"] < 0).sum())
        be = int((g["R"] == 0).sum())
        rows.append({
            "year": yr, "trades": len(g), "wins": wins, "losses": losses,
            "breakeven": be, "win_pct": round(wins / len(g) * 100, 1),
            "longest_win_streak": w, "longest_loss_streak": l,
            "usd": round(g["usd"].sum(), 2),
            "total_R": round(g["R"].sum(), 2),
        })
    df = pd.DataFrame(rows).sort_values("year")
    df["cum_usd"] = df["usd"].cumsum().round(2)
    df["account_end"] = (ACCOUNT + df["cum_usd"]).round(2)
    return df


def monthly_table(tdf):
    rows = []
    for m, g in tdf.groupby("month"):
        wins = int((g["R"] > 0).sum())
        rows.append({"month": m, "trades": len(g), "wins": wins,
                     "losses": int((g["R"] < 0).sum()),
                     "usd": round(g["usd"].sum(), 2)})
    return pd.DataFrame(rows).sort_values("month")


def weekly_table(tdf):
    rows = []
    for (wk, ws), g in tdf.groupby(["week", "week_start"]):
        rows.append({"week": wk, "week_start": ws, "trades": len(g),
                     "wins": int((g["R"] > 0).sum()), "losses": int((g["R"] < 0).sum()),
                     "usd": round(g["usd"].sum(), 2)})
    return pd.DataFrame(rows).sort_values("week_start")


def main():
    master = {}
    for inst, base in BEST.items():
        df = sessions.load_m5(os.path.join(ROOT, "data", inst, f"{inst.lower()}_m5.csv"))
        master[inst] = {}
        for rr in RRS:
            cfg = bt.Config(instrument=inst, rr=rr, **base)
            tdf, s = bt.run(df, cfg)
            tdf = enrich(tdf)
            tag = f"{inst}_{str(rr).replace('.', 'p')}R"
            yt = yearly_table(tdf); mt = monthly_table(tdf); wt = weekly_table(tdf)
            yt.to_csv(os.path.join(OUT, f"{tag}_yearly.csv"), index=False)
            mt.to_csv(os.path.join(OUT, f"{tag}_monthly.csv"), index=False)
            wt.to_csv(os.path.join(OUT, f"{tag}_weekly.csv"), index=False)
            tdf.to_csv(os.path.join(OUT, f"{tag}_trades.csv"), index=False)
            master[inst][rr] = {"yearly": yt, "monthly": mt, "weekly": wt,
                                "total_usd": round(tdf["usd"].sum(), 2),
                                "trades": len(tdf)}
            print(f"\n===== {inst}  RR={rr}  (stop {base['stop_pts']}pt) — total ${tdf['usd'].sum():,.0f} on {len(tdf)} trades =====")
            print(yt.to_string(index=False))
    # combined yearly $ comparison across RR
    for inst in BEST:
        print(f"\n##### {inst}: yearly $ by RR #####")
        comp = pd.DataFrame({rr: master[inst][rr]["yearly"].set_index("year")["usd"] for rr in RRS})
        comp.loc["TOTAL"] = comp.sum()
        print(comp.round(0).to_string())
    json.dump({inst: {str(rr): master[inst][rr]["total_usd"] for rr in RRS} for inst in BEST},
              open(os.path.join(OUT, "totals.json"), "w"), indent=2)
    # consolidated JSON for the executive-summary artifact
    consol = {"risk_per_trade": RISK, "account": ACCOUNT, "rrs": RRS,
              "config": {i: {k: (v if not isinstance(v, float) else v) for k, v in BEST[i].items()} for i in BEST},
              "data": {}}
    for inst in BEST:
        consol["data"][inst] = {}
        for rr in RRS:
            m = master[inst][rr]
            consol["data"][inst][str(rr)] = {
                "total_usd": m["total_usd"], "trades": m["trades"],
                "yearly": m["yearly"].to_dict(orient="records"),
                "monthly": m["monthly"].to_dict(orient="records"),
                "weekly": [{**r, "week_start": str(r["week_start"])} for r in m["weekly"].to_dict(orient="records")],
            }
    json.dump(consol, open(os.path.join(OUT, "consolidated.json"), "w"), indent=1, default=str)
    print("\nconsolidated.json written")
    return master


if __name__ == "__main__":
    main()
