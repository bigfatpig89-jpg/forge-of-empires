# RMoose's Forge of Empires Assortment: Project Overview

*Last updated: 2026-10-29. Added a Content-Security-Policy, build warnings for ignored files, a tracked-files-only `make_zip.sh`, and the en19 Treasury From / Before 2026 toggles; fixed the Event League Reports page.*

A reference for anyone (including Claude) picking this project up. It describes what the site is, how it is built, where everything lives, the conventions agreed so far, and the gotchas found along the way.

## 1. What this is

A public, static website that tracks two Forge of Empires (FoE) guilds, plus a few small tools, all in one page.

| | |
|---|---|
| Site title | RMoose's Forge of Empires Assortment |
| Live site | https://bigfatpig89-jpg.github.io/forge-of-empires/ |
| Repo | `bigfatpig89-jpg/forge-of-empires` on GitHub (branch `main`, Pages serves the `docs/` folder) |
| Dashboards | **en19 (Uceria)**: Team Targets. **en5 (East-Nagach)**: Freyja's Warriors |
| Tools | Guild Expeditions Report Generator, Guild Contributions Processor, Event League Reports |
| Owner's setup | macOS, Terminal, Chrome, Anaconda Python 3.13, git over HTTPS with a personal access token |
| Status | Unofficial fan site. Footer says "This website is not affiliated with InnoGames." |

## 2. How it works

1. Game data is exported by browser extensions (**FoE Helper**, and since late Aug 2026 **Forge Hammer**) as CSV files. These cannot be pulled automatically, so the owner saves them by hand each week.
2. CSVs go into `data/<dashboard>/<section>/`.
3. `python3 build.py` reads every CSV and writes JSON into `docs/data/` (plus `docs/data/dashboards.json`, which lists the sections that have data).
4. `docs/index.html` is one single-file app (hash routing, no framework). It fetches the JSON and draws tables and charts. Charts use **Plotly.js** (v2.35.2), hosted locally as `docs/plotly.min.js` (do not use a CDN). The fonts are self-hosted too (`docs/fonts/`, loaded by `@font-face` in `index.html`); the site makes no requests to other websites.
5. `git add . && git commit && git push` publishes it through GitHub Pages.

There is no server and no database. Everything the browser needs is a file in `docs/`.

## 3. Repository layout

```
build.py                 data to JSON (all the data logic lives here)
eras.py                  era name to eraID map (ERAS list; Iron Age = 3 ... Stellar Age = 24)
gb_short_forms.csv       Great Building short forms (Great Building;Short form), ';' separated
README.md                weekly routine, security notes
RMoose_FoE_Assortment_Project_Overview.md   this file (at the repo root, not inside docs/, so it is not published on the site)
make_zip.sh              builds ~/Downloads/RMoose_FoE.zip for uploading to Claude (tracked files only; no .git, no raw member CSVs); committed to the repo
data/
  en19/ and en5/         one folder per dashboard
    treasury/  qi/  gbg/  ge/  greatbuildings/  guildbuildings/  eras/  members/
  events/                event league CSVs (shared, not per dashboard)
docs/                    the website (served by GitHub Pages)
  index.html             the whole app
  plotly.min.js          charting library
  fonts/                 ibm-plex-sans-400/600.woff2, fraunces-600.woff2 + licence files (SIL OFL)
  .nojekyll
  data/
    dashboards.json      {"en19": [sections with data], "en5": [...]}
    en19/*.json  en5/*.json  events.json
.gitignore               includes data/*/members/ and **/[Mm]ember*.csv (raw member CSVs must never be committed)
```

Two different `data` folders exist: **`data/`** (input CSVs) and **`docs/data/`** (generated JSON). Do not mix them up.

## 4. Site map

Hash routes: `#/` (menu), `#/<dashboard>/<section>`, `#/report`, `#/contributions`, `#/events`. Old links like `#qi` redirect to `#/en19/qi`. A top bar shows the site title and tabs (en19, en5, Report Generator, Contributions Processor, Event League Reports). Inside a dashboard a sidebar lists its sections; **a section appears only when `dashboards.json` says it has data**, so the sidebar is driven by `build.py`, not by `index.html`.

Main-menu cards carry a top line: **Dashboard** (en19, en5), **Tool** (Report Generator, Contributions Processor) or **Data** (Event League Reports). The server name (for example "en19 (Uceria)") is a subtitle under the card title.

Footer: the "All data is pulled using FoE Helper/Forge Hammer as soon after Monday 8am server time as possible." line shows on dashboard pages only. "Your data is not saved on this site and will be cleared once you leave the page." shows on the two upload tools. The InnoGames disclaimer shows everywhere.

### Dashboard sections (same code for both dashboards)

| Section | What it shows |
|---|---|
| **Guild Treasury** | Total Stock by Era (line per era, markers); Goods in stock (era dropdown, one line per good); **en19 only:** both charts have their own "From 2026" / "Before 2026" toggle, default From 2026 (see section 8); Low stock table: goods under 100,000 in the order of the GuildGoods file, or, if none, "Well done!" plus the 5 lowest goods (Good, Age, Quantity). |
| **Quantum Incursions (QI)** | Team progress per season, with active players in the hover; All-Time Best Performances (top 20 ranks); Seasonal Leaderboard (season dropdown); Player history (bars, player dropdown). |
| **Guild Battlegrounds (GBG)** | Same layout as QI. Bars split into negotiations (x2) and battles. Score = battles + negotiations x 2. |
| **Guild Expeditions (GE)** | Team Percentage per Week = total solved / (80 x all players that week, including inactive); grey markers before Trials, teal after, dashed "Trials introduced" line; All-Time Best Performances = highest trial completed (80 encounters solved); Weekly Leaderboard (solved, then trial level, then expedition points; the game's own rank is ignored); Player History line graph (y axis 0 to 80), markers coloured by trial level. |
| **Great Buildings** | Latest file only. Players as rows, Great Buildings as columns (short forms, full name on hover, legend below). Blue = level went up or newly built since the previous file (players absent from the previous file are not marked). Gold = highest level of that building (all tied owners). Below: ranking section with a Great Building dropdown (ties share a rank). |
| **Guild Buildings** | Latest file only. Total guild goods per player per age (age short forms from `ERA_SHORT`, legend below), bold Total column and Total row, Num Members row (from the Eras file). Below: Guild Goods Ranking (Player, Total Guild Goods) and Goods Watchlist by Age (Age, Goods, Num Members, Goods/Members; ages with at least one member; lowest ratio first). |
| **Members** (password) | Members table (Rank, ID, Name, Points, Era, Last GE, Last GBG, Last QI, Battles Won). Name turns red if any of Last GE < 48, Last GBG < 500, Last QI < 500, and the failing cell is red. Top 10 gainers vs the previous file by points, by percentage, by battles won. A "Copy top 10 gainers" button copies name and gain, padded so values line up in a fixed-width font. |

### Tools (run entirely in the browser, nothing is saved)

- **Guild Expeditions Report Generator** (`#/report`): upload a GE CSV (default name `Participation.csv`; the file name does not matter). Produces a text report (date, ranking and guild power typed in, expedition points summed, counts of members who completed level 5 down to "did not start"), plus the uploaded data below. Level thresholds: 80, 64-79, 48-63, 32-47, 16-31, 1-15, 0 encounters. No "only" wording.
- **Guild Contributions Processor** (`#/contributions`): upload a Guild Treasury contributions log (Player ID, Player name, Era, Good, Amount, Message, Date/Time). One row per player, one column per message type, Grand Total column, Total row, negatives in red brackets.
- **Event League Reports** (`#/events`): reads `data/events/*.csv` (Year, Event, Type, Server, ServerName, then one column per league level). One section per Year + Event: "Event: 2026 Fellowship", "Minigame Type: ...", then servers as rows (`en5:East-Nagach`) and league thresholds as columns.

## 5. Data folders and file formats

All dashboard CSVs are `;` separated, usually UTF-8 with a BOM and Windows line endings. `build.py` reads them with `utf-8-sig`, so exports can be used as they come. The date in the file name is the snapshot date. **Convention: dates are Mondays** (files dated Tuesday or Wednesday were renamed to the Monday before).

| Section | Folder (under `data/<dashboard>/`) | File name | Columns |
|---|---|---|---|
| Treasury | `treasury/` | `GuildGoods-YYYY-MM-DD.csv` | eraID, era, good, produceable, instock |
| QI | `qi/` | `QI-YYYY-MM-DD.csv` | Player_ID, Player, Actions, Progress |
| GBG | `gbg/` | `GBG-YYYY-MM-DD.csv` or `GBG-PlayerList-YYYY-MM-DD.csv` | older: player_id, player, negotiations, battles, total. Newer: Player_ID, Player, Negotiations, Fights, Total, Attrition (some cells like `1388 ↑ 15`; the number before the arrow is used). `build.py` accepts both. |
| GE | `ge/` | `GE-YYYY-MM-DD.csv` | gexWeek (e.g. 05/Oct/2026), player ID, player, expeditionPoints, solvedEncounters, rank, trial. The week comes from the `gexWeek` column, not the file name. `trial` is blank before Trials existed. |
| Great Buildings | `greatbuildings/` | `GreatBuildings-YYYY-MM-DD.csv` | gbname, city_entity_id, member, level, max_level, invested_forge_points, forge_points_for_level_up (only `level` is shown) |
| Guild Buildings | `guildbuildings/` | `GuildBuildings-YYYY-MM-DD.csv` | building, level, eraId, era, member, guildPower, guildGoods (only guildGoods is used) |
| Eras | `eras/` | `Eras-YYYY-MM-DD.csv` | eraId, era, numberOfMembers, treasuryGoods, memberPoints (only numberOfMembers is used, for Num Members) |
| Members | `members/` | `Member-YYYY-MM-DD.csv` | rank, member_id, member, points, eraID, eraName, guildgoods, activity_warnings, messages, gex_participation, gbg_participation, qi_participation (Forge Hammer only), won_battles, guildmember |
| Events | `data/events/` | any name | Year, Event, Type, Server, ServerName, league columns (comma or semicolon separated) |

Naming is strict: `build.py` globs on the prefix (`QI-*.csv` and so on). A file that does not match (wrong prefix, `.CSV`, `.xlsx`) is not read, and `build.py` prints `WARNING: <file> is ignored` for it, so read the build output before pushing. A section printing 0 rows means a wrong folder or file name. A file name without a date, or an unreadable GE week, stops the build with a plain message.

## 6. Weekly routine

```
# 1. put the new files in the right data/<dashboard>/<section>/ folders
python3 build.py                 # prints row counts per section and a WARNING for every file it ignores; asks for the Members password
cd docs && python3 -m http.server    # optional preview at http://localhost:8000 (Ctrl+C to stop, then cd ..)
git add .
git commit -m "Add data for YYYY-MM-DD"
git push
```

Then wait a minute or two and hard-refresh (Cmd+Shift+R). QI comes every two weeks, GBG per season, the others weekly. A new Great Building without a short form prints a warning and shows its full name until a row is added to `gb_short_forms.csv`.

## 7. Where to change things

| To change | Edit |
|---|---|
| Add a dashboard | `DASHBOARDS` in `build.py` and `DASH` in `index.html` (name, guild, game, kicker, tile) |
| Add a section | a function in `build.py`, an entry in `build()`, and an entry in `SECTIONS` in `index.html` |
| New era in the game | `ERAS` in `eras.py`, `ERA_SHORT` and (if needed) `GB_ERAS` in `build.py` |
| Great Building short forms | `gb_short_forms.csv` (names matched ignoring accents and case) |
| Low stock limit | `LOW_STOCK = 100000` in `index.html` |
| Members red thresholds | `MIN = {ge:48, gbg:500, qi:500}` in `index.html` |
| Trials introduced date | `TRIALS_START = "2025-05-26"` in `build.py` (same for every dashboard) |
| Treasury Before / From toggle | `TREASURY_SPLIT = {"en19": "2026-01-01"}` in `build.py` (only dashboards listed get the toggle) |
| Line break gap in charts | `BREAK_DAYS = 45` in `index.html` |
| What the page may load or send | the `Content-Security-Policy` meta tag in the `<head>` of `index.html` (see section 8) |

## 8. Conventions and decisions

- Players are matched by **ID**, never by name, and show their latest name. If two IDs share a name, the dropdown shows `Name (ID 123456)` (this happens with PURPLE SAGE in en5).
- QI and GBG charts show **active players only** (score above zero). GE data keeps inactive players (needed for the team percentage), but its leaderboard and player list show active players only.
- Ranking ties share a rank (1, 2, 2, 4) everywhere.
- Missed weeks are normal. Lines break across gaps longer than 45 days; week-over-week logic is never applied across gaps.
- The wording is "season" for QI and GBG, "week" for GE.
- Era order in tables follows the eraID order of the GuildGoods file.
- Styling: IBM Plex Sans for text, Fraunces for headings (self-hosted in `docs/fonts/`, no Google Fonts link; fallbacks are `system-ui` and Georgia), dark sidebar, teal accent `#0f766e`, gold `#f4c430`, blue `#dbeafe` / `#1e40af`. Avoid CSS class names that clash with existing ones (`.top` is the top bar; a clash once stretched table rows). Use new unique class names.
- The page fetches its JSON with `cache: "no-cache"` to avoid stale data after weekly updates.
- **Treasury toggle (en19 only):** en19 has no snapshots between 2025-09-22 and 2026-09-28 (371 days) and its total stock roughly doubled over that gap (about 18.5M to 37M), so one chart flattens the early years. `build.py` writes `meta.split` (the date, or null) into each `treasury.json`; `index.html` shows the buttons only when `meta.split` is set and there are snapshots on both sides. "From" means date >= split, "Before" means date < split; the default is From (the current state). Both Total Stock by Era and Goods in stock have a toggle; they work independently. Each era (and, within an era, each good) keeps one colour in both views (Plotly's default colour order, set explicitly as `COLORWAY`). In Goods in stock the Era dropdown lists only eras with snapshots in the chosen period (for example Stellar Age Discovery appears only in From 2026) and keeps the selected era when it is still listed. The gap is a data-collection accident specific to en19, so en5 and other dashboards are deliberately not listed.
- **Escaping:** every player, good, building and file-derived name goes through `escHtml` (or `esc`) before it enters `innerHTML`. Keep doing this for every new table. Names come from strangers in a game and from uploaded files.
- **Content-Security-Policy:** a `<meta http-equiv="Content-Security-Policy">` tag at the top of `index.html` allows scripts, styles, fonts, images and `fetch` from this site only (`'unsafe-inline'` for script and style, because the app is one inline script), and sets `base-uri`, `form-action` and `object-src` to none. It is a safety net against cross-site scripting: even an injected script cannot send data to another site. Do not add anything that loads from another website (CDN scripts, Google Fonts, remote images): the CSP blocks it and the site promises not to make such requests. If something stops working after an edit, check the browser console for "violates the following Content Security Policy directive". GitHub Pages cannot send real HTTP headers, so a meta tag is the only option.

## 9. Members section: privacy and the two file kinds

- It is **password protected by encryption, not by a page check**: `build.py` encrypts the member data (AES-256-GCM, key from PBKDF2-SHA256 with 600,000 iterations) and writes only `members.json` encrypted. The browser decrypts after the password is typed. The password is typed when building (hidden) or read from the `MEMBERS_PASSWORD` environment variable; it is never stored in the repo. Needs `pip install cryptography`. Use a long password (12+ characters).
- **Raw member CSVs must never be committed** (`data/*/members/` and `**/[Mm]ember*.csv` are in `.gitignore`; check `git status` before pushing). The owner considers the data low sensitivity: the leaders want it hidden from other guild members, and a leak would not be a big deal. The password is therefore deliberately simple (build.py only warns below 12 characters). The encrypted file is public, so a determined person could guess a simple password offline; that trade-off is accepted. Names, IDs and GE/GBG/QI scores are already public in the other sections, so the red-name flags could be recomputed by anyone.
- Once unlocked, the page stays unlocked until it is reloaded.
- **FoE Helper vs Forge Hammer member files.** FoE Helper files (up to 2026-08-25 for en5) have no `qi_participation` column, and their `gex_participation` and `gbg_participation` are running counters, not season points. Forge Hammer files (from 2026-08-31) have all three columns equal to the real season values (checked against the GE, GBG and QI files). `build.py` detects a FoE Helper file by the missing `qi_participation` column and fills Last GE / GBG / QI from the GE, GBG and QI files of the same week (QI and GBG: the latest season ending on or before the file's date, within 14 days; blank if none). The Members page explains this in a note.
- `points` and `won_battles` mean the same in both kinds, so the gains tables compare across them.

## 10. Data cleaning history (for context)

- The en5 history came from shared spreadsheets and many duplicate copies. Duplicates were removed by comparing contents, keeping the larger (later) file; names were cleaned (for example `Copy of ... - Freyja_s - Participation(1).csv` became `Participation-<date>.csv`, later renamed `GE-<date>.csv`).
- Where two exports of the same QI season, GBG season or GE week differed, the most complete one was kept (higher totals, or the one holding players the other lacked; some GBG seasons were merged player by player). Weeks that look partial were flagged (for example the GE week of 2026-07-27 was excluded).
- Treasury files that repeated the previous file's stock values were removed (en5: 2026-03-24, 2026-03-31, 2026-06-09).
- The en5 treasury names the newest era "Stellar Age Discovery" (en19 uses "Stellar Age: Discovery"). This is cosmetic.

## 11. Things that bit us (check these first when something looks wrong)

- **A tab does not appear**: the sidebar comes from `docs/data/dashboards.json`, written by `build.py`. Replacing only `index.html` is not enough; `build.py` must be current and the folder and file names correct.
- **`build (1).py` in Downloads**: repeated downloads get numbered names, so `mv ~/Downloads/build.py .` can move an old copy. Check with `ls -lt ~/Downloads/build*.py`. `mv` overwrites without asking (`mv -i` asks).
- **Default fonts shown**: a file in `docs/fonts/` is missing, misnamed or not committed; the names must match the `@font-face` rules in `index.html`. The site stays usable (fallback fonts).
- **Stale data in the browser**: fixed by `no-cache` fetches; if it recurs, compare `head -c 120 docs/data/...json` with `curl -s http://localhost:8000/data/...json | head -c 120`, and check the server runs from the right `docs` folder.
- **`git push` says no upstream**: run `git push --set-upstream origin main` once.
- **`.gitignore` has no trailing newline** (as of this writing): to add a line use `printf '\nPATTERN\n' >> .gitignore`, not `echo`, or the new text is glued to the last line.
- **Sandbox limits for Claude**: no internet, so it cannot fetch the live site or download images; it cannot see the owner's machine, so commands must be run by the owner. The Members password is never shared with Claude (tests use a throwaway password).
- Fan data sites: ForgeDB's API (`api.forge-db.com`) refuses scripted requests (HTTP 403); do not spoof browser headers. FoE Helper and Forge Hammer are manual-export browser extensions with no API.

## 12. Working conventions for Claude

- Look at the actual uploaded files first (columns, ranges, anomalies) and say what was found before building. Do not guess column meanings; if something is genuinely ambiguous, make a sensible default, state it, or ask one short question.
- Deliver changed files as downloads (`index.html`, `build.py`, `README.md`, and any new data file) and always say which files to replace, whether `python3 build.py` must be re-run, and the `git add .`, `git commit`, `git push` steps. Say explicitly when `build.py` changed, because the page depends on it.
- Test before delivering: build in a scratch copy, load the page in headless Chromium with the real `docs/plotly.min.js`, and check numbers against the raw CSVs with pandas. Report what was checked and what was not (for example "I have not seen the charts rendered" when that is the case).
- Keep changes small and scoped to the request. Keep existing styling and wording. When editing data files, preserve their format (`;`, BOM, CRLF).
- Explain terminal and git steps plainly for macOS. Warn before anything destructive and explain how to undo it.
- **Uploading the project to Claude:** run `./make_zip.sh` in the project folder; it writes `~/Downloads/RMoose_FoE.zip` from the files git tracks (plus new files `.gitignore` does not exclude), so `.git`, raw member CSVs, `.DS_Store`, `__pycache__` and other zips are left out automatically, and it skips `docs/plotly.min.js`. Never upload `.git` (its config can hold a GitHub token) or the raw member CSVs. The script prints a safety check at the end that should show nothing (`docs/data/*/members.json` is encrypted and public, so it is fine). For small tasks upload only the files involved. Ask for `docs/plotly.min.js` (v2.35.2) if a browser test of the charts is needed; without it, tests can only use a stand-in for Plotly, so chart rendering is unverified.
- Never put the Members password, tokens or cookies in files or chat. Do not suggest committing member CSVs.

## 13. Known loose ends and ideas

- **Goods icons** for the Great Buildings and Guild Goods views: only 20x20 images were found. InnoGames' Fan Content Guideline allows game graphics on a non-commercial fan site if they are unaltered, credited to InnoGames, and the site states the owner is solely responsible; it is not a licence. Icons would have to be saved locally (no hotlinking), and Plotly legends cannot show images (a custom HTML legend would be needed).
- **Automating the weekly update**: the export step stays manual. After it, a script (or a GitHub Action triggered by uploading CSVs) could run `build.py` and push. Raw member CSVs must not go through GitHub if the repo is public.
- A history view for the Members section (the data for it is already in the encrypted file).
- **Stronger CSP:** move the inline script from `index.html` into `docs/app.js`, then drop `'unsafe-inline'` from `script-src` so injected inline scripts cannot run at all.
- **Quieter history:** `members.json` is re-encrypted with a fresh salt and IV on every build, so it changes (about 0.7 MB for en5) in every commit even with identical data. Skipping the Members step when the raw member files are unchanged would stop that. Never reuse an IV with the same key to get identical output (it breaks AES-GCM).
- A `requirements.txt` (pandas, cryptography), a short `data/NOTES.md` recording which files were removed or excluded and why (the cleaning in section 10 cannot be reproduced otherwise), and a backup of the raw member CSVs, which exist only on the owner's Mac (they are never committed).
