"""One-off: split the GBG-Indiv-Data tab into one GBG-YYYY-MM-DD.csv per battleground season (End Date)."""
import pandas as pd
from pathlib import Path

SRC = "FoE_U_TeamTargets.xlsx"
OUT = Path("data/gbg"); OUT.mkdir(parents=True, exist_ok=True)

g = pd.read_excel(SRC, sheet_name="GBG-Indiv-Data", usecols=range(7))   # drops the Excel notes columns
g = g.drop(columns="HelperColumn").dropna(subset=["player_id", "End Date"])
for date, df in g.groupby(g["End Date"].dt.strftime("%Y-%m-%d")):
    df = df[["player_id", "player", "negotiations", "battles", "total"]].astype(
        {"player_id": int, "negotiations": int, "battles": int, "total": int})
    df.to_csv(OUT / f"GBG-{date}.csv", sep=";", index=False)
