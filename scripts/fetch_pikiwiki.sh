#!/usr/bin/env bash
# Download the Kibbutz Ruhama archive's own freely-licensed photographs.
#
# PikiWiki's own /image/download/ endpoint returns 403 to anything that isn't a
# browser session, so this goes to Wikimedia Commons instead - PikiWiki mirrors
# every upload there under the same licence, and Commons serves the file
# directly through Special:FilePath. Commons does require a real User-Agent.
#
#   bash scripts/fetch_pikiwiki.sh
#
# Anything that still fails, save by hand from the page URL printed at the end.
# Then read two fields off each page and send them to me:
#   תאריך הצילום  - date taken
#   סוג הרישיון   - licence (some public domain, some CC BY 2.5 Israel)
# They differ per image. One licence does not cover the set.

set -u
cd "$(dirname "$0")/.." || exit 1
OUT=images/sourced
mkdir -p "$OUT"

UA='ruhama1946.site/1.0 (https://ruhama1946.site; commemorative archive project)'
BASE='https://commons.wikimedia.org/wiki/Special:FilePath'

# id : slug   - Commons names follow {id}_kibbutz_ruhama_PikiWiki_Israel.{jpg,png}
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
  got=""
  for ext in jpg png JPG; do
    dest="$OUT/${id}_${slug}.${ext}"
    [ -s "$dest" ] && { got="$dest"; break; }
    if curl -fsSL --max-time 90 -A "$UA" -o "$dest" \
         "${BASE}/${id}_kibbutz_ruhama_PikiWiki_Israel.${ext}" 2>/dev/null \
       && [ -s "$dest" ]; then
      got="$dest"; break
    fi
    rm -f "$dest"
  done
  if [ -n "$got" ]; then
    printf "  + %-56s %6s KB\n" "$got" "$(( $(wc -c < "$got") / 1024 ))"
  else
    echo "  ! $id - save by hand from https://www.pikiwiki.org.il/image/view/$id"
  fi
done

echo
echo "Open each and send me תאריך הצילום + סוג הרישיון:"
for entry in $IMAGES; do
  echo "  https://www.pikiwiki.org.il/image/view/${entry%%:*}"
done
echo
echo "Full archive gallery (there is more than these seven):"
echo "  https://www.pikiwiki.org.il/gallery/?s=&organization=8112"
