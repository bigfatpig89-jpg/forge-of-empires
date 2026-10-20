# Guild Tracker

Dashboards for Guild Treasury, Quantum Incursions (QI), Guild Battlegrounds (GBG) and Guild Expeditions (GE).
Live site: https://bigfatpig89-jpg.github.io/forge-of-empires/

The site opens on a main menu (RMoose's Forge of Empires Assortment) with the en19 (Uceria) Team Targets dashboard, the en5 (East-Nagach) Freyja's Warriors dashboard, and the Guild Expeditions Report Generator (upload a GE CSV, get a copyable report; it runs in the browser). Dashboard pages are `#/en19/treasury`, `#/en19/qi`, `#/en19/gbg` and `#/en19/ge`; the generator is `#/report`.

## Weekly update

1. Save the new export in the matching folder, named with the snapshot date:

   | Section | Folder | File name |
   |---|---|---|
   | Guild Treasury | `data/en19/treasury/` | `GuildGoods-YYYY-MM-DD.csv` |
   | Quantum Incursions | `data/en19/qi/` | `QI-YYYY-MM-DD.csv` |
   | Guild Battlegrounds | `data/en19/gbg/` | `GBG-YYYY-MM-DD.csv` |
| Guild Expeditions | `data/en19/ge/` | `GE-YYYY-MM-DD.csv` |

2. Rebuild the data files (run from the project folder, the one containing `build.py`):

   ```
   python3 build.py
   ```

   It prints the number of rows per section. If a section prints 0 rows, check the folder and file name.

3. Publish:

   ```
   git add .
   git commit -m "Add data for YYYY-MM-DD"
   git push
   ```

4. Wait a minute or two, then hard-refresh the site (Cmd+Shift+R).

## Preview locally (optional)

```
cd docs
python3 -m http.server
```

Open http://localhost:8000. Stop the server with Ctrl+C, then `cd ..` to return to the project folder.

## How it fits together

- `data/en19/treasury/`, `data/en19/qi/`, `data/en19/gbg/`, `data/en19/ge/`: one CSV per snapshot (`;`-separated).
  - Treasury columns: eraID, era, good, produceable, instock
  - QI columns: Player_ID, Player, Actions, Progress (Progress is a per-round score)
  - GBG columns: player_id, player, negotiations, battles, total (total = 2 x negotiations + battles)
  - GE columns: gexWeek, player ID, player, expeditionPoints, solvedEncounters, rank, trial (the week comes from the `gexWeek` column, not the file name; a file can hold one week or several)
- `build.py`: reads every CSV and writes `docs/data/en19/treasury.json`, `qi.json`, `gbg.json` and `ge.json`.
- `eras.py`: maps era names to eraIDs.
- `docs/`: the website served by GitHub Pages.
  - `index.html`: the whole dashboard (sidebar and all three sections).
  - `plotly.min.js`: the charting library, hosted locally.
  - `data/`: the JSON files created by `build.py`.

## Notes

- Files are read with a BOM-safe encoding, so the game's exports can be used as they are.
- QI and GBG charts show active players only (score above zero). Players are matched by ID, and their latest name is shown.
- Missed weeks or rounds are fine. Charts break the line where data is missing.
- When the game releases a new era, add its name to the end of the `ERAS` list in `eras.py` before running `build.py`.
- If the site doesn't update, check the Actions tab for the Pages deploy status.
- GE team chart shows the percentage of possible encounters solved: total solved / (80 x all players that week, including inactive ones). Markers are grey before Trials and one colour afterwards, with a dashed line at the first week with trial data.
- GE leaderboard ranks active players (at least one solved encounter) by encounters solved, then trial level, then expedition points. The rank in the game's export is not used.
- GE player history is a line graph that includes weeks with 0 solved. `trial` (the difficulty level a player picks each week) was only added in May 2025, so earlier points are grey, later points are coloured by trial level, and a dashed line marks the first week with trial data (found automatically from the data).
- QI, GBG and GE each have an "All-Time Best Performances" table (top 20 ranks, tied players share a rank, e.g. 1, 2, 2, 4). It uses each player's best record over all data, with the earliest date if the best was repeated. For GE the ranking is the highest trial completed, counting only weeks with all 80 encounters solved.
- The Guild Contributions Processor (`#/contributions`) takes a Guild Treasury contributions CSV (Player ID, Player name, Era, Good, Amount, Message, Date/Time) and shows each player's total per message type plus a Grand Total, with negative values in red. Like the report generator, it runs in the browser and nothing is saved.
- Each dashboard has its own data folder (`data/en19/`, `data/en5/`), each with `treasury`, `qi`, `gbg` and `ge` subfolders. `build.py` writes `docs/data/<dashboard>/*.json` plus `docs/data/dashboards.json`, which lists the sections that have data. A section appears in a dashboard's sidebar once it has files, so the en5 sidebar currently shows only Guild Battlegrounds. To add another dashboard, add its name to `DASHBOARDS` in `build.py` and to `DASH` in `docs/index.html`.
- The Members section (en5) is password protected. Put FoE Helper member exports in `data/en5/members/` named `Member-YYYY-MM-DD.csv`. `build.py` asks for the password (or reads `MEMBERS_PASSWORD`) and writes only an encrypted `docs/data/en5/members.json`; the browser decrypts it after the password is entered. Never commit the raw member CSVs (`data/*/members/` is in `.gitignore`), and use a long password. Needs `pip install cryptography`.
- Member files come in two kinds. FoE Helper files have no `qi_participation` column and their GE and GBG participation columns are counters, not season points, so `build.py` fills Last GE, Last GBG and Last QI for them from the GE, GBG and QI files of the same week (QI and GBG: the latest season that ended on or before the file's date, within 14 days; blank if there is none). ForgeHammer files have the `qi_participation` column and are used as they are. The Members page explains this under the table.
- The Great Buildings section shows each player's level in each Great Building (latest file only; players as rows, short forms as columns, with a legend underneath). Cells in blue went up, or are newly built, since the previous file; players who were not in the previous file are not marked. Put FoE Helper / Forge Hammer exports in `data/<dashboard>/greatbuildings/` named `GreatBuildings-YYYY-MM-DD.csv`. The short forms live in `gb_short_forms.csv` (Great Building;Short form) in the project folder; when a new Great Building appears, `build.py` prints a warning and shows its full name until you add a row for it.
