#!/bin/sh
# Récupère les deux fichiers tiers que reelkit embarque dans chaque composition : GSAP et la police (Inter).
set -e
D="$(cd "$(dirname "$0")" && pwd)/reelkit/static"
curl -sL -o "$D/gsap.min.js" https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js
curl -sL -o "$D/police.woff2" https://cdn.jsdelivr.net/fontsource/fonts/inter:vf@latest/latin-wght-normal.woff2
echo "GSAP et Inter installés dans $D"
