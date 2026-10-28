# RMoose's Forge of Empires Assortment

Dashboards and small tools for two Forge of Empires guilds. Live site: https://bigfatpig89-jpg.github.io/forge-of-empires/

| Dashboard | Guild |
|---|---|
| `en19` | Team Targets (en19, Uceria) |
| `en5` | Freyja's Warriors (en5, East-Nagach) |

The site opens on a main menu. Each dashboard has a sidebar with its sections (a section appears once it has data): Guild Treasury, Quantum Incursions (QI), Guild Battlegrounds (GBG), Guild Expeditions (GE), Great Buildings, Guild Buildings and Members (password protected). The menu also links to three tools that run in the browser (nothing is saved): the Guild Expeditions Report Generator (`#/report`), the Guild Contributions Processor (`#/contributions`) and the Event League Reports page (`#/events`).

This is an unofficial fan site and is not affiliated with InnoGames. A fuller description of the project is in `RMoose_FoE_Assortment_Project_Overview.md`.

## How it works

CSV exports go into `data/`. `python3 build.py` turns them into JSON files in `docs/data/`. `docs/index.html` (one file, no server) reads the JSON and draws the pages with Plotly (`docs/plotly.min.js`, hosted locally). The fonts are hosted locally too (`docs/fonts/`), so the site loads nothing from other websites. GitHub Pages serves the `docs/` folder.

Note the two different `data` folders: `data/` holds the CSV inputs, `docs/data/` holds the generated JSON.

## Weekly update

1. Save each new export in the matching folder, named with the snapshot date (use the Monday):

   | Section | Folder | File name |
   |---|---|---|
   | Guild Treasury | `data/<dashboard>/treasury/` | `GuildGoods-YYYY-MM-DD.csv` |
   | Quantum Incursions | `data/<dashboard>/qi/` | `QI-YYYY-MM-DD.csv` |
   | Guild Battlegrounds | `data/<dashboard>/gbg/` | `GBG-YYYY-MM-DD.csv` or `GBG-PlayerList-YYYY-MM-DD.csv` |
   | Guild Expeditions | `data/<dashboard>/ge/` | `GE-YYYY-MM-DD.csv` |
   | Great Buildings | `data/<dashboard>/greatbuildings/` | `GreatBuildings-YYYY-MM-DD.csv` |
   | Guild Buildings | `data/<dashboard>/guildbuildings/` | `GuildBuildings-YYYY-MM-DD.csv` |
   | Eras (for the Num Members row) | `data/<dashboard>/eras/` | `Eras-YYYY-MM-DD.csv` |
   | Members | `data/<dashboard>/members/` | `Member-YYYY-MM-DD.csv` |
   | Event leagues (shared) | `data/events/` | any name (`.csv`) |

   `<dashboard>` is `en19` or `en5`. QI comes every two weeks and GBG once per season; the rest weekly. Missed weeks are fine, and charts break the line where data is missing.

2. Rebuild the data files (run from the project folder, the one containing `build.py`):

   ```
   python3 build.py
   ```

   It prints the number of rows per section (and asks for the Members password, see below). If a section prints 0 rows, check the folder and file name: a file with the wrong prefix is silently ignored.

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

## File formats

Dashboard CSVs are `;`-separated. They are read with a BOM-safe encoding, so the game's exports can be used as they are. The event league CSVs may use commas or semicolons.

| Section | Columns |
|---|---|
| Treasury | eraID, era, good, produceable, instock |
| QI | Player_ID, Player, Actions, Progress (Progress is the per-season score) |
| GBG | player_id, player, negotiations, battles, total, or the newer Player_ID, Player, Negotiations, Fights, Total, Attrition. Total = 2 x negotiations + battles. Cells like `1388 ↑ 15` are read as 1388. |
| GE | gexWeek, player ID, player, expeditionPoints, solvedEncounters, rank, trial. The week comes from the `gexWeek` column, not the file name. |
| Great Buildings | gbname, city_entity_id, member, level, max_level, ... (only `level` is shown) |
| Guild Buildings | building, level, eraId, era, member, guildPower, guildGoods (only `guildGoods` is used) |
| Eras | eraId, era, numberOfMembers, ... (only `numberOfMembers` is used) |
| Members | rank, member_id, member, points, eraID, eraName, guildgoods, activity_warnings, messages, gex_participation, gbg_participation, qi_participation, won_battles, guildmember |
| Event leagues | Year, Event, Type, Server, ServerName, then one column per league level |

## Files in the project

- `build.py`: reads every CSV and writes `docs/data/<dashboard>/*.json`, `docs/data/dashboards.json` (the sections that have data for each dashboard) and `docs/data/events.json`.
- `eras.py`: maps era names to eraIDs (used only when a treasury file has no `eraID` column).
- `gb_short_forms.csv`: Great Building short forms (`Great Building;Short form`). A new Great Building prints a warning and shows its full name until a row is added.
- `docs/index.html`: the whole site (menu, sidebar, all sections and tools).
- `docs/fonts/`: the site fonts as `.woff2` files (IBM Plex Sans 400 and 600, Fraunces 600) with their licence files (SIL Open Font License). `index.html` loads them through `@font-face`; the file names there must match the files in this folder.

## Where to change things

| To change | Edit |
|---|---|
| Add a dashboard | `DASHBOARDS` in `build.py` and `DASH` in `docs/index.html` |
| A new era appears in the game | `ERAS` in `eras.py`, and `ERA_SHORT` (and `GB_ERAS` if needed) in `build.py` |
| Low stock limit (100,000) | `LOW_STOCK` in `docs/index.html` |
| Members red-name minimums (GE 48, GBG 500, QI 500) | `MIN` in `docs/index.html` |
| Date Trials were introduced | `TRIALS_START` in `build.py` |

## Members section (password protected)

- Put the member exports in `data/<dashboard>/members/`. `build.py` asks for the password when it runs (typing is hidden), or reads the `MEMBERS_PASSWORD` environment variable. It writes only an encrypted `members.json`; the browser decrypts it after the password is entered. The password is never stored in the repo. Use a long password (12+ characters). Needs `pip install cryptography`.
- **Never commit the raw member CSVs.** `data/*/members/` is in `.gitignore`.
- Members table: red name and red cell when Last GE, Last GBG or Last QI is under its minimum. Top 10 gainers (points, percentage, battles won) compare the latest file with the previous one, and a button copies them as text.
- Two kinds of member file exist. FoE Helper files have no `qi_participation` column and their GE and GBG participation values are counters, not season points. For those files `build.py` fills Last GE, Last GBG and Last QI from the GE, GBG and QI files of the same week (QI and GBG: the latest season that ended on or before the file's date, within 14 days; blank if there is none). Forge Hammer files have `qi_participation` and are used as they are. The page explains this under the table.

## Notes on the pages

- Players are matched by ID and shown with their latest name. If two IDs share a name, the player dropdown adds `(ID ...)`.
- QI and GBG show active players only (score above zero). Ranking ties share a rank (1, 2, 2, 4). The All-Time Best Performances tables show the top 20 ranks and use each player's best record (earliest date if repeated).
- GE: the team chart is the percentage of possible encounters solved (total solved / (80 x all players that week, including inactive ones)), grey before Trials and one colour after, with a dashed line at the Trials date. The leaderboard ranks by encounters solved, then trial level, then expedition points. The All-Time table ranks the highest trial completed (all 80 encounters solved).
- Guild Treasury: goods under 100,000 are listed in the order of the GuildGoods file; if there are none, the 5 lowest goods are shown instead.
- Great Buildings: latest file only. Blue = the level went up (or the building is new) since the previous file; players who were not in the previous file are not marked. Gold = the highest level of that building (all tied owners). A ranking section below ranks the owners of a chosen building.
- Guild Buildings: total guild goods per player and age (columns in the order of the eras in GuildGoods, short forms from `ERA_SHORT`), a Total row and column, a Num Members row from the Eras file, a ranking of members by total goods, and a Goods Watchlist by Age (ages with at least one member, lowest goods per member first).
- Event League Reports: one section per event (Year + Event), with servers as rows (`en5:East-Nagach`) and the point thresholds for each league level as columns.
- Guild Expeditions Report Generator: upload a GE CSV (the file name does not matter) to get a text report to copy. Guild Contributions Processor: upload a treasury contributions log to get each player's totals by contribution type.

## Troubleshooting

- **A section is missing from the sidebar:** the sidebar comes from `docs/data/dashboards.json`, which `build.py` writes. Check the folder and file names, re-run `python3 build.py`, and make sure `build.py` is the current version (replacing only `index.html` is not enough).
- **The page shows old data:** hard-refresh (Cmd+Shift+R). The page re-checks its data files on every load, so also confirm the preview server runs from this project's `docs` folder.
- **`git push` says the branch has no upstream:** run `git push --set-upstream origin main` once.
- **The fonts look wrong (default fonts shown):** check that `docs/fonts/` holds `ibm-plex-sans-400.woff2`, `ibm-plex-sans-600.woff2` and `fraunces-600.woff2`, and that they were committed. If a font file is missing the browser falls back to system fonts; nothing else breaks.
- **The site doesn't update:** check the repository's Actions tab for the Pages deploy status.
