#!/usr/bin/env bash
# Puts pfQuest (quest givers and objectives on the world map and minimap, by Shagu, MIT licence)
# into the addons folder given as $1: the vanilla 1.12, English-only build, as its Makefile's
# "enUS" target makes it, with the toc listing each init file once.
set -euo pipefail
mkdir -p "$1"
DEST="$(cd "$1" && pwd)"
COMMIT=104f35678ca39ab1fb78b655f815cc7016f5e0c8
WORK="$(mktemp -d)"
git clone -q https://github.com/shagu/pfQuest.git "$WORK/src"
git -C "$WORK/src" checkout -q "$COMMIT"
OUT="$DEST/pfQuest"
rm -rf "$OUT"
mkdir -p "$OUT/init" "$OUT/db/enUS"
cd "$WORK/src"
cp -rf compat img "$OUT/"
for f in db/*.lua; do case "$f" in *-tbc*) ;; *) cp -f "$f" "$OUT/db/";; esac; done
for f in db/enUS/*.lua; do case "$f" in *-tbc*) ;; *) cp -f "$f" "$OUT/db/enUS/";; esac; done
cp -f ./*.lua LICENSE README.md "$OUT/"
cp -f init/addon.xml init/data.xml init/enUS.xml "$OUT/init/"
grep -v '^init\\' pfQuest.toc | sed '/^[[:space:]]*$/d' > "$OUT/pfQuest.toc"
printf 'init\\data.xml\ninit\\enUS.xml\ninit\\addon.xml\n' >> "$OUT/pfQuest.toc"
echo "$COMMIT" > "$OUT/gitrev.txt"
rm -rf "$WORK"
echo "pfQuest $COMMIT -> $OUT"
