"""One-off: split the QI-Data tab of the old workbook into one QI-YYYY-MM-DD.csv per round (same format as the game export)."""
import pandas as pd
from pathlib import Path

SRC = "FoE_U_TeamTargets.xlsx"
OUT = Path("data/qi"); OUT.mkdir(parents=True, exist_ok=True)

q = pd.read_excel(SRC, sheet_name="QI-Data", usecols=range(5))     # Player_ID, Player, Actions, Progress, Date ended
q = q.dropna(subset=["Player_ID", "Date ended"])
for date, df in q.groupby(q["Date ended"].dt.strftime("%Y-%m-%d")):
    df = df[["Player_ID", "Player", "Actions", "Progress"]].astype({"Player_ID": int, "Actions": int, "Progress": int})
    df.to_csv(OUT / f"QI-{date}.csv", sep=";", index=False)
