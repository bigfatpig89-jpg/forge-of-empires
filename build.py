"""Merge every data/GuildGoods-*.csv into site/data.json for the dashboard."""
import re, pandas as pd
from pathlib import Path
from eras import ERA_ID

frames = []
for f in sorted(Path("data").glob("GuildGoods-*.csv")):
    df = pd.read_csv(f, sep=";")
    df["date"] = re.search(r"(\d{4}-\d{2}-\d{2})", f.name).group(1)
    if "eraID" not in df:
        df["eraID"] = df["era"].map(ERA_ID)
    frames.append(df)

out = pd.concat(frames, ignore_index=True).sort_values(["date", "eraID"], kind="stable")
out = out[["date", "eraID", "era", "good", "produceable", "instock"]]
out.to_json("site/data.json", orient="records")
print(f"{out['date'].nunique()} weeks, {len(out)} rows -> site/data.json")
