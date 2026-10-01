"""Build docs/data/*.json for the dashboard from the CSVs in data/treasury, data/qi, data/gbg and data/ge."""
import json, re, pandas as pd
from pathlib import Path
from eras import ERA_ID

def load(folder, prefix):
    frames = []
    for f in sorted(Path(folder).glob(f"{prefix}-*.csv")):
        df = pd.read_csv(f, sep=";", encoding="utf-8-sig")       # utf-8-sig strips the BOM the game export adds
        df["date"] = re.search(r"(\d{4}-\d{2}-\d{2})", f.name).group(1)
        frames.append(df)
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()

def scores(df, id_col, name_col, cols):
    """Keep active rows only (score > 0); remember each player's latest name."""
    if df.empty: return {"names": {}, "rows": []}
    names = df.sort_values("date").drop_duplicates(id_col, keep="last").set_index(id_col)[name_col]
    df = df[df[cols["s"]] > 0].rename(columns={id_col: "id", **{v: k for k, v in cols.items()}})
    return {"names": {str(k): v for k, v in names.items()},
            "rows": df[["date", "id"] + list(cols)].sort_values(["date", "s"], ascending=[True, False]).to_dict("records")}

MONTHS = {m: i for i, m in enumerate("Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split(), 1)}
def week(v):
    """GE dates come as 15/Dec/2025 (game export); ISO dates are accepted too."""
    m = re.fullmatch(r"(\d{1,2})/(\w{3})/(\d{4})", str(v).strip())
    return f"{m[3]}-{MONTHS[m[2].title()]:02d}-{int(m[1]):02d}" if m else pd.to_datetime(v).strftime("%Y-%m-%d")

def guild_expeditions(folder):
    """The date comes from the gexWeek column, so a file may hold one week or many. All players are kept, including those with 0 solved."""
    frames = []
    for f in sorted(Path(folder).glob("GE-*.csv")):
        df = pd.read_csv(f, sep=";", encoding="utf-8-sig")
        df["date"] = df["gexWeek"].map(week) if "gexWeek" in df else re.search(r"(\d{4}-\d{2}-\d{2})", f.name).group(1)
        frames.append(df)
    if not frames: return {"names": {}, "meta": {}, "rows": []}
    df = pd.concat(frames, ignore_index=True).drop_duplicates(["date", "player ID"], keep="last")
    names = df.sort_values("date").drop_duplicates("player ID", keep="last").set_index("player ID")["player"]
    first_trial = df.loc[df["trial"].notna(), "date"].min()      # trial is blank before Trials existed
    act = df.rename(columns={"player ID": "id", "solvedEncounters": "s",      # inactive players are kept: the team percentage needs the full roster
                             "expeditionPoints": "p", "rank": "r", "trial": "t"})
    rows = act.sort_values(["date", "s", "p"], ascending=[True, False, False])[["date", "id", "s", "p", "r", "t"]].to_dict("records")
    for r in rows: r["t"] = None if pd.isna(r["t"]) else int(r["t"])
    return {"names": {str(k): v for k, v in names.items()},
            "meta": {"trialStart": None if pd.isna(first_trial) else first_trial}, "rows": rows}

out = {}
t = load("data/treasury", "GuildGoods")
if "eraID" not in t: t["eraID"] = t["era"].map(ERA_ID)
out["treasury"] = {"rows": t.sort_values(["date", "eraID"], kind="stable")
                   [["date", "eraID", "era", "good", "produceable", "instock"]].to_dict("records")}
out["qi"] = scores(load("data/qi", "QI"), "Player_ID", "Player", {"a": "Actions", "s": "Progress"})
out["gbg"] = scores(load("data/gbg", "GBG"), "player_id", "player", {"n": "negotiations", "b": "battles", "s": "total"})
out["ge"] = guild_expeditions("data/ge")

Path("docs/data").mkdir(parents=True, exist_ok=True)
for name, d in out.items():
    Path(f"docs/data/{name}.json").write_text(json.dumps(d, separators=(",", ":")))
    print(name, len(d["rows"]), "rows")
