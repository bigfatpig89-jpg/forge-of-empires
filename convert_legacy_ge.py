"""One-off: split the GE-Indiv-Data tab and Participation.csv into one GE-YYYY-MM-DD.csv per week (same columns as the game export)."""
import pandas as pd
from pathlib import Path

OUT = Path("data/ge"); OUT.mkdir(parents=True, exist_ok=True)
COLS = ["gexWeek", "player ID", "player", "expeditionPoints", "solvedEncounters", "rank", "trial"]

old = pd.read_excel("FoE_U_TeamTargets.xlsx", sheet_name="GE-Indiv-Data", usecols=range(1, 8))
old = old.dropna(subset=["player ID", "gexWeek"])
new = pd.read_csv("Participation.csv", sep=";", encoding="utf-8-sig")
new["gexWeek"] = pd.to_datetime(new["gexWeek"], format="%d/%b/%Y")

df = pd.concat([old[COLS], new[COLS]], ignore_index=True)
for week, g in df.groupby("gexWeek"):
    g = g.astype({"player ID": int, "expeditionPoints": int, "solvedEncounters": int, "rank": int}).copy()
    g["trial"] = g["trial"].astype("Int64")                    # blank (not NaN text) before trials existed
    g["gexWeek"] = week.strftime("%d/%b/%Y")                   # same date format as the game export
    g[COLS].to_csv(OUT / f"GE-{week:%Y-%m-%d}.csv", sep=";", index=False)
