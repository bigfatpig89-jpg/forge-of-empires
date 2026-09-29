# Guild treasury tracker

Weekly dashboard of guild treasury goods.
Live site: https://bigfatpig89-jpg.github.io/forge-of-empires/

## Weekly update

1. Save the new export in `data/`, named `GuildGoods-YYYY-MM-DD.csv` (the date of the snapshot).
2. Rebuild the data file:

   ```
   python3 build.py
   ```

3. Publish:

   ```
   git add .
   git commit -m "Add YYYY-MM-DD"
   git push
   ```

4. Wait a minute or two, then hard-refresh the site (Cmd+Shift+R).

## Preview locally (optional)

```
cd docs
python3 -m http.server
```

Open http://localhost:8000. Stop the server with Ctrl+C.

## How it fits together

- `data/`: one CSV per weekly snapshot (`;`-separated, columns: eraID, era, good, produceable, instock).
- `build.py`: merges all the CSVs into `docs/data.json`.
- `eras.py`: maps era names to eraIDs.
- `docs/`: the website served by GitHub Pages (`index.html`, `data.json`, `plotly.min.js`).

## Notes

- When the game releases a new era, add its name to the end of the `ERAS` list in `eras.py` before running `build.py`.
- Missed weeks are fine. Charts break the line where data is missing.
- If the site doesn't update, check the Actions tab for the Pages deploy status.
