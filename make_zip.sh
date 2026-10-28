#!/bin/bash
cd "$(dirname "$0")" || exit 1
rm -f ~/Downloads/RMoose_FoE.zip
zip -r ~/Downloads/RMoose_FoE.zip . -x ".git/*" "data/*/members/*" "*.DS_Store" "__pycache__/*" "docs/plotly.min.js"
echo "Created ~/Downloads/RMoose_FoE.zip"
