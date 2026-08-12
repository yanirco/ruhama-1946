#!/usr/bin/env bash
# Download the Kibbutz Ruhama archive's own freely-licensed photographs from
# PikiWiki, Israel's free-use photo bank. The archive uploaded them itself, so
# this is the same provenance as the exhibition-board photographs - just with a
# licence already attached.
#
#   bash scripts/fetch_pikiwiki.sh
#
# Then open each image's page (printed below) and note two fields:
#   תאריך הצילום  - date taken
#   סוג הרישיון   - licence (some are public domain, some CC BY 2.5 Israel)
# Those two go in the caption and the credit. They differ per image; do not
# assume one licence covers the set.

set -u
cd "$(dirname "$0")/.." || exit 1
OUT=images/sourced
mkdir -p "$OUT"

# id : short slug
IMAGES="
100872:children_after_the_search_june_1946
20721:children_after_the_search_original
110700:drilling_the_well
110696:kibbutz_ruhama_a
110698:kibbutz_ruhama_b
110699:kibbutz_ruhama_c
110702:kibbutz_ruhama_d
"

for entry in $IMAGES; do
  id="${entry%%:*}"; slug="${entry##*:}"
  dest="$OUT/${id}_${slug}.jpg"
  if [ -s "$dest" ]; then
    echo "  = $dest (already here)"
    continue
  fi
  # -L because the download endpoint redirects to Wikimedia's upload host
  if curl -fsSL --max-time 90 -o "$dest" \
       "https://www.pikiwiki.org.il/image/download/${id}"; then
    printf "  + %-52s %6s KB\n" "$dest" "$(( $(wc -c < "$dest") / 1024 ))"
  else
    rm -f "$dest"
    echo "  ! $id failed - open https://www.pikiwiki.org.il/image/view/$id and save it by hand"
  fi
done

echo
echo "Credit fields to collect (open each and read תאריך הצילום + סוג הרישיון):"
for entry in $IMAGES; do
  id="${entry%%:*}"
  echo "  https://www.pikiwiki.org.il/image/view/$id"
done
echo
echo "Full archive gallery:"
echo "  https://www.pikiwiki.org.il/gallery/?s=&organization=8112"
