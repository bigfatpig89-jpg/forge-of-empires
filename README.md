# Guild Tracker

Dashboards for Guild Treasury, Quantum Incursions (QI), Guild Battlegrounds (GBG) and Guild Expeditions (GE).
Live site: https://bigfatpig89-jpg.github.io/forge-of-empires/

Each section has its own page: `#treasury`, `#qi`, `#gbg` and `#ge` (for example `.../forge-of-empires/#qi`).

## Weekly update

1. Save the new export in the matching folder, named with the snapshot date:

   | Section | Folder | File name |
   |---|---|---|
   | Guild Treasury | `data/treasury/` | `GuildGoods-YYYY-MM-DD.csv` |
   | Quantum Incursions | `data/qi/` | `QI-YYYY-MM-DD.csv` |
   | Guild Battlegrounds | `data/gbg/` | `GBG-YYYY-MM-DD.csv` |
| Guild Expeditions | `data/ge/` | `GE-YYYY-MM-DD.csv` |

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

- `data/treasury/`, `data/qi/`, `data/gbg/`, `data/ge/`: one CSV per snapshot (`;`-separated).
  - Treasury columns: eraID, era, good, produceable, instock
  - QI columns: Player_ID, Player, Actions, Progress (Progress is a per-round score)
  - GBG columns: player_id, player, negotiations, battles, total (total = 2 x negotiations + battles)
  - GE columns: gexWeek, player ID, player, expeditionPoints, solvedEncounters, rank, trial (the week comes from the `gexWeek` column, not the file name; a file can hold one week or several)
- `build.py`: reads every CSV and writes `docs/data/treasury.json`, `qi.json`, `gbg.json` and `ge.json`.
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
