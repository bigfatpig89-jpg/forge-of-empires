#!/bin/bash
# Builds ~/Downloads/RMoose_FoE.zip for uploading to Claude.
# Allow-list approach: it zips only files that git tracks, plus new files that .gitignore
# does not exclude. Anything ignored (raw member CSVs, .DS_Store, __pycache__, other zips)
# and the whole .git folder (which can hold a GitHub token) are left out automatically.
# docs/plotly.min.js (4.5 MB) is left out too; add it by hand only if a browser test is needed.
cd "$(dirname "$0")" || exit 1
OUT=~/Downloads/RMoose_FoE.zip
rm -f "$OUT"
git -c core.quotepath=off ls-files --cached --others --exclude-standard \
  | grep -v -x "docs/plotly.min.js" \
  | grep -v -i -E '(^|/)member[^/]*\.csv$' \
  | while IFS= read -r f; do [ -f "$f" ] && printf '%s\n' "$f"; done \
  | zip -q "$OUT" -@
echo "Created $OUT"
echo "Safety check (should print nothing below):"
unzip -l "$OUT" | grep -i -E " \.git/|member[^/]*\.csv|\.env"
