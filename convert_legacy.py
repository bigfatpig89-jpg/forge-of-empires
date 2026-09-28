"""One-off: split the old wide Excel export into one GuildGoods-YYYY-MM-DD.csv per week (same format as the game export)."""
import pandas as pd
from pathlib import Path
from eras import ERA_ID

SRC = "FoE_U_TeamTargets_-_TreasuryData.csv"
OUT = Path("data"); OUT.mkdir(exist_ok=True)

raw = pd.read_csv(SRC, header=None, dtype=str)
dates, body = raw.iloc[1], raw.iloc[4:109]      # body stops before the "Changes by age" block

for c in range(2, raw.shape[1], 2):             # each week = (produceable, instock) column pair
    if pd.isna(dates[c]):
        continue
    df = pd.DataFrame({"era": body[0], "good": body[1],
                       "produceable": pd.to_numeric(body[c]), "instock": pd.to_numeric(body[c + 1])})
    df = df.dropna(subset=["produceable", "instock"])        # eras not unlocked yet
    if df.empty:                                             # week with a date but no data
        continue
    df.insert(0, "eraID", df["era"].map(ERA_ID))
    assert df["eraID"].notna().all(), "unknown era name"
    d = pd.to_datetime(dates[c], format="%d/%m/%Y").strftime("%Y-%m-%d")
    df.astype({"produceable": int, "instock": int}).to_csv(OUT / f"GuildGoods-{d}.csv", sep=";", index=False)
