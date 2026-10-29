"""Build docs/data/*.json for the dashboard from the CSVs in data/treasury, data/qi, data/gbg and data/ge."""
import base64, csv, datetime as dt, getpass, json, os, re, unicodedata, pandas as pd
from pathlib import Path
from eras import ERA_ID

def warn_unmatched(folder, pattern):
    """Print a warning for every file in a folder that the glob pattern will not pick up (wrong prefix, .CSV, .xlsx, a typo...)."""
    folder = Path(folder)
    if not folder.is_dir(): return
    matched = set(folder.glob(pattern))
    for f in sorted(folder.iterdir()):
        if f.is_file() and not f.name.startswith(".") and f not in matched:
            print(f"  WARNING: {f} is ignored (the name must match {pattern})")

def file_date(f):
    """The snapshot date in a file name (YYYY-MM-DD); stops with a clear message if there is none."""
    m = re.search(r"(\d{4}-\d{2}-\d{2})", f.name)
    if not m: raise SystemExit(f"{f}: the file name needs a date such as 2026-10-26 (YYYY-MM-DD)")
    return m.group(1)

def load(folder, prefix, fix=None):
    frames = []
    warn_unmatched(folder, f"{prefix}-*.csv")
    for f in sorted(Path(folder).glob(f"{prefix}-*.csv")):
        df = pd.read_csv(f, sep=";", encoding="utf-8-sig")       # utf-8-sig strips the BOM the game export adds
        if fix: df = fix(df)
        df["date"] = file_date(f)
        frames.append(df)
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()

def number(s):
    """'1388 ↑ 15' -> 1388: keep the number and drop the change marker that some exports add."""
    return pd.to_numeric(s.astype(str).str.extract(r"(-?\d+)")[0]).fillna(0).astype(int)

def gbg_columns(df):
    """GBG files come in two layouts: player_id/player/negotiations/battles/total, or Player_ID/Player/Negotiations/Fights/Total/Attrition."""
    df = df.rename(columns=lambda c: c.strip().lower()).rename(columns={"fights": "battles"})
    for c in ("negotiations", "battles", "total"):
        df[c] = number(df[c])
    return df[["player_id", "player", "negotiations", "battles", "total"]]    # extra columns such as Attrition are ignored

def scores(df, id_col, name_col, cols):
    """Keep active rows only (score > 0); remember each player's latest name."""
    if df.empty: return {"names": {}, "rows": []}
    df = df.drop_duplicates([id_col, "date"], keep="last")
    names = df.sort_values("date").drop_duplicates(id_col, keep="last").set_index(id_col)[name_col]
    df = df[df[cols["s"]] > 0].rename(columns={id_col: "id", **{v: k for k, v in cols.items()}})
    return {"names": {str(k): v for k, v in names.items()},
            "rows": df[["date", "id"] + list(cols)].sort_values(["date", "s"], ascending=[True, False]).to_dict("records")}

def season_lookup(rows):
    by = {}
    for r in rows: by.setdefault(r["date"], {})[r["id"]] = r["s"]
    return by

def season_value(by, date, pid, exact):
    """What a member scored in the GE week / QI or GBG season that matches a member file's date (None if there is no such season)."""
    mon = dt.date.fromisoformat(date); mon -= dt.timedelta(days=mon.weekday())        # files dated Tuesday belong to that Monday
    ok = [d for d in by if (d == mon.isoformat() if exact else 0 <= (mon - dt.date.fromisoformat(d)).days <= 14)]
    return by[max(ok)].get(pid, 0) if ok else None                                  # QI/GBG: the latest season that ended on or before the file

GB_ERAS = ["BronzeAge", "IronAge", "EarlyMiddleAge", "HighMiddleAge", "LateMiddleAge", "ColonialAge", "IndustrialAge", "ProgressiveEra", "ModernEra",
           "PostModernEra", "ContemporaryEra", "TomorrowEra", "FutureEra", "ArcticFuture", "OceanicFuture", "VirtualFuture", "SpaceAgeMars",
           "SpaceAgeAsteroidBelt", "SpaceAgeVenus", "SpaceAgeJupiterMoon", "SpaceAgeTitan", "SpaceAgeSpaceHub", "StellarAgeDiscovery", "AllAge"]

def gb_key(s):
    """Match names ignoring accents, case and punctuation (Chateau = Château)."""
    return re.sub(r"[^a-z0-9]", "", unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower())

def gb_order(entity_id):
    m = re.match(r"X_([A-Za-z]+)_", entity_id); n = re.search(r"(\d+)$", entity_id)
    return (GB_ERAS.index(m[1]) if m and m[1] in GB_ERAS else len(GB_ERAS), int(n[1]) if n else 0)

def great_buildings(folder):
    """Great Building levels per player (GreatBuildings-YYYY-MM-DD.csv). Short forms come from gb_short_forms.csv."""
    df = load(folder, "GreatBuildings")
    if df.empty: return {"gbs": [], "rows": []}
    short = {}
    if Path("gb_short_forms.csv").exists():
        with open("gb_short_forms.csv", encoding="utf-8-sig", newline="") as f:
            short = {gb_key(r["Great Building"]): r["Short form"].strip() for r in csv.DictReader(f, delimiter=";")}
    df = df.dropna(subset=["level"]).drop_duplicates(["date", "member", "city_entity_id"], keep="last")
    gbs = df.drop_duplicates("city_entity_id")[["city_entity_id", "gbname"]].to_dict("records")
    gbs.sort(key=lambda g: (gb_order(g["city_entity_id"]), g["gbname"]))
    for g in gbs:
        if gb_key(g["gbname"]) not in short: print("  no short form for", g["gbname"], "- using the full name (add it to gb_short_forms.csv)")
    return {"gbs": [{"id": g["city_entity_id"], "name": g["gbname"], "short": short.get(gb_key(g["gbname"])) or g["gbname"]} for g in gbs],
            "rows": [{"date": r["date"], "p": r["member"], "g": r["city_entity_id"], "l": int(r["level"])}
                     for r in df.sort_values(["date", "member"]).to_dict("records")]}

ERA_SHORT = {3: "IA", 4: "EMA", 5: "HMA", 6: "LMA", 7: "CA", 8: "InA", 9: "PE", 10: "ME", 11: "PME", 12: "CE", 13: "TE", 14: "FE", 15: "AF", 16: "OF",
             17: "VF", 18: "SAM", 19: "SAAB", 20: "SAV", 21: "SAJM", 22: "SAT", 23: "SASH", 24: "SAD"}      # by eraId; a new era shows its full name until added here

def guild_buildings(folder, eras_folder):
    """Guild Buildings per player and era (GuildBuildings-YYYY-MM-DD.csv): number of buildings, guild goods and building levels.
    Members per era come from the Eras files (Eras-YYYY-MM-DD.csv) in eras_folder."""
    df = load(folder, "GuildBuildings")
    if df.empty: return {"eras": [], "members": [], "rows": []}
    ef = load(eras_folder, "Eras")
    members = [] if ef.empty else [{"date": r["date"], "e": int(r["eraId"]), "m": int(r["numberOfMembers"])} for r in ef.to_dict("records")]
    for c in ("level", "eraId", "guildGoods"): df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0).astype(int)
    eras = df.drop_duplicates("eraId").sort_values("eraId")[["eraId", "era"]]            # eraId order = the order of the eras in GuildGoods
    g = df.groupby(["date", "member", "eraId"]).agg(n=("building", "count"), g=("guildGoods", "sum"), l=("level", "sum")).reset_index()
    return {"eras": [{"id": int(r.eraId), "name": r.era, "short": ERA_SHORT.get(int(r.eraId), r.era)} for r in eras.itertuples()], "members": members,
            "rows": [{"date": r.date, "p": r.member, "e": int(r.eraId), "n": int(r.n), "g": int(r.g), "l": int(r.l)} for r in g.itertuples()]}

def members(folder, out):
    """Member exports (Member-YYYY-MM-DD.csv); the date comes from the file name.
    FoE Helper files (no qi_participation column) hold counters instead of season points, so their
    Last GE / GBG / QI values are filled in from the GE, GBG and QI files of the same week."""
    ge, gbg, qi = (season_lookup(out[k]["rows"]) for k in ("ge", "gbg", "qi"))
    opt = lambda v: None if v is None or pd.isna(v) else int(v)
    rows = []
    warn_unmatched(folder, "Member-*.csv")
    for f in sorted(Path(folder).glob("Member-*.csv")):
        df = pd.read_csv(f, sep=";", encoding="utf-8-sig")
        if "guildmember" in df: df = df[df["guildmember"] != 0]            # keep current members only
        helper = "qi_participation" not in df                               # ForgeHammer files have this column, FoE Helper files do not
        date = file_date(f)
        for r in df.to_dict("records"):
            row = {"date": date, "id": int(r["member_id"]), "rank": int(r["rank"]), "name": r["member"], "points": int(r["points"]),
                   "era": r.get("eraName"), "ge": opt(r.get("gex_participation")), "gbg": opt(r.get("gbg_participation")),
                   "qi": opt(r.get("qi_participation")), "wb": opt(r.get("won_battles"))}
            if helper:
                pid = row["id"]; row.update(ge=season_value(ge, date, pid, True), gbg=season_value(gbg, date, pid, False),
                                            qi=season_value(qi, date, pid, False), filled=True)
            rows.append(row)
    return {"rows": rows}

ITER = 600_000
_password = None
def password():
    """The Members password is asked for when building (or read from MEMBERS_PASSWORD); it is never stored in the repo."""
    global _password
    if _password is None:
        _password = os.environ.get("MEMBERS_PASSWORD") or getpass.getpass("Password for the Members section (input is hidden): ")
        if 0 < len(_password) < 12: print("Warning: use a long password (12+ characters); the encrypted file is public and can be guessed offline.")
    return _password

def encrypt(obj, pw):
    """AES-256-GCM with a PBKDF2-SHA256 key, readable by the browser's Web Crypto API."""
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    salt, iv = os.urandom(16), os.urandom(12)
    key = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=ITER).derive(pw.encode())
    data = AESGCM(key).encrypt(iv, json.dumps(obj, separators=(",", ":")).encode(), None)
    b = lambda x: base64.b64encode(x).decode()
    return {"v": 1, "iter": ITER, "salt": b(salt), "iv": b(iv), "data": b(data)}

MONTHS = {m: i for i, m in enumerate("Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split(), 1)}
def week(v):
    """GE dates come as 15/Dec/2025 (game export); ISO dates are accepted too."""
    m = re.fullmatch(r"(\d{1,2})/(\w{3})/(\d{4})", str(v).strip())
    if m and m[2].title() not in MONTHS: raise SystemExit(f"GE file: cannot read the week '{v}' (expected a date like 15/Dec/2025)")
    return f"{m[3]}-{MONTHS[m[2].title()]:02d}-{int(m[1]):02d}" if m else pd.to_datetime(v).strftime("%Y-%m-%d")

TRIALS_START = "2025-05-26"    # when Trials were introduced; the same for every dashboard (first trial week in the en19 data)

def guild_expeditions(folder):
    """The date comes from the gexWeek column, so a file may hold one week or many. All players are kept, including those with 0 solved."""
    frames = []
    warn_unmatched(folder, "GE-*.csv")
    for f in sorted(Path(folder).glob("GE-*.csv")):
        df = pd.read_csv(f, sep=";", encoding="utf-8-sig")
        df["date"] = df["gexWeek"].map(week) if "gexWeek" in df else file_date(f)
        frames.append(df)
    if not frames: return {"names": {}, "meta": {}, "rows": []}
    df = pd.concat(frames, ignore_index=True).drop_duplicates(["date", "player ID"], keep="last")
    names = df.sort_values("date").drop_duplicates("player ID", keep="last").set_index("player ID")["player"]
    has_trial = df["trial"].notna().any()                       # trial is blank in weeks before Trials existed
    act = df.rename(columns={"player ID": "id", "solvedEncounters": "s",      # inactive players are kept: the team percentage needs the full roster
                             "expeditionPoints": "p", "rank": "r", "trial": "t"})
    rows = act.sort_values(["date", "s", "p"], ascending=[True, False, False])[["date", "id", "s", "p", "r", "t"]].to_dict("records")
    for r in rows: r["t"] = None if pd.isna(r["t"]) else int(r["t"])
    return {"names": {str(k): v for k, v in names.items()},
            "meta": {"trialStart": TRIALS_START if has_trial else None}, "rows": rows}

def event_leagues(folder):
    """Event league thresholds from the CSV files in data/events (any file name; comma or semicolon separated).
    Columns: Year, Event, Type, Server, ServerName, then one column per league level. An event is one Year + Event."""
    frames = []
    warn_unmatched(folder, "*.csv")
    for f in sorted(Path(folder).glob("*.csv")):
        text = f.read_text(encoding="utf-8-sig")
        frames.append(pd.read_csv(f, sep=";" if text.split("\n")[0].count(";") > text.split("\n")[0].count(",") else ",", encoding="utf-8-sig", dtype=str, keep_default_na=False))
    events = []
    if frames:
        df = pd.concat(frames, ignore_index=True).drop_duplicates(["Year", "Event", "Server"], keep="last")
        fixed = ["Year", "Event", "Type", "Server", "ServerName"]
        server_key = lambda s: (re.sub(r"\d+", "", s), int(re.search(r"\d+", s)[0]) if re.search(r"\d+", s) else 0)
        for (year, event), g in sorted(df.groupby(["Year", "Event"], sort=False), key=lambda kv: (kv[0][0], kv[0][1]), reverse=True):
            leagues = [c for c in df.columns if c not in fixed and (g[c].str.strip() != "").any()]          # league levels this event has
            servers = [{"server": r["Server"], "name": r["ServerName"], "values": [int(r[c]) if str(r[c]).strip().isdigit() else r[c] for c in leagues]}
                       for r in sorted(g.to_dict("records"), key=lambda r: server_key(r["Server"]))]
            events.append({"year": year, "event": event, "type": ", ".join(dict.fromkeys(g["Type"])), "leagues": leagues, "servers": servers})
    return {"events": events}

DASHBOARDS = ["en19", "en5"]    # one folder per dashboard: data/<name>/{treasury,qi,gbg,ge}; sections without files are simply left out

def build(dash):
    base, out = f"data/{dash}", {}
    t = load(f"{base}/treasury", "GuildGoods")
    if not t.empty and "eraID" not in t: t["eraID"] = t["era"].map(ERA_ID)
    out["treasury"] = {"rows": [] if t.empty else t.sort_values(["date", "eraID"], kind="stable")
                       [["date", "eraID", "era", "good", "produceable", "instock"]].to_dict("records")}
    out["qi"] = scores(load(f"{base}/qi", "QI"), "Player_ID", "Player", {"a": "Actions", "s": "Progress"})
    out["gbg"] = scores(load(f"{base}/gbg", "GBG", gbg_columns), "player_id", "player", {"n": "negotiations", "b": "battles", "s": "total"})
    out["ge"] = guild_expeditions(f"{base}/ge")
    out["greatbuildings"] = great_buildings(f"{base}/greatbuildings")
    out["guildbuildings"] = guild_buildings(f"{base}/guildbuildings", f"{base}/eras")
    Path(f"docs/data/{dash}").mkdir(parents=True, exist_ok=True)
    for name, d in out.items():
        Path(f"docs/data/{dash}/{name}.json").write_text(json.dumps(d, separators=(",", ":")))
        print(dash, name, len(d["rows"]), "rows")
    sections = [name for name, d in out.items() if d["rows"]]       # the sections that have data
    m = members(f"{base}/members", out)
    if m["rows"]:                                                    # members are only ever written encrypted
        pw = password()
        if not pw: print(dash, "members: no password given, section skipped")
        else:
            try:
                Path(f"docs/data/{dash}/members.json").write_text(json.dumps(encrypt(m, pw)))
                print(dash, "members", len(m["rows"]), "rows (encrypted)"); sections.append("members")
            except ImportError: print(dash, "members: run  pip install cryptography  and build again")
    return sections

manifest = {dash: build(dash) for dash in DASHBOARDS}
Path("docs/data/dashboards.json").write_text(json.dumps(manifest))
ev = event_leagues("data/events"); Path("docs/data/events.json").write_text(json.dumps(ev))
print("events", len(ev["events"]), "events")   # tells the page which sections to show for each dashboard
