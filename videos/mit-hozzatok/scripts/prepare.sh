#!/usr/bin/env bash
# Előkészítés: Kitti vágott beszéde, fotók, elmosott hátterek, logó, zene.
# Használat: scripts/prepare.sh <forrásmappa>   (a Drive „Miket hozzatok?” mappa letöltött tartalma, raw.mp4 = VID_20261107_154444.mp4)
set -euo pipefail
SRC="$1"; cd "$(dirname "$0")/.."
mkdir -p assets/photos assets/music

# Megtartott szakaszok a nyers felvételből (kezdet vége, mp). Lásd EDIT.md.
SEGS=(
 "1.25 3.54"   "8.23 9.24"   "9.81 13.98"  "14.25 25.42" "29.27 33.15"
 "33.95 35.07" "35.77 36.62" "36.90 42.33" "45.45 53.18" "54.18 55.30"
 "56.26 59.37" "59.66 69.29" "70.14 71.27" "71.70 74.66" "75.06 82.57"
 "83.77 86.60" "86.92 93.90"
)
TMP=$(mktemp -d); : > "$TMP/list.txt"; i=0
for s in "${SEGS[@]}"; do
  set -- $s; a=$1; b=$2
  n=$(python3 -c "print(round(($b-$a)*30))"); d=$(python3 -c "print(f'{$n/30:.6f}')")   # képkockára kerekítve, hogy a kép és a hang ugyanolyan hosszú legyen
  # pontos vágás újrakódolással; 12–15 ms-os hangáttűnés a kattanások ellen
  ffmpeg -hide_banner -loglevel error -y -threads 2 -ss "$a" -i "$SRC/raw.mp4" -t "$d" \
    -vf "scale=1080:1920,fps=30,format=yuv420p" \
    -af "afade=t=in:d=0.012,afade=t=out:st=$(python3 -c "print(round($d-0.015,3))"):d=0.015" \
    -frames:v "$n" -c:v libx264 -crf 18 -preset medium -g 30 -c:a pcm_s16le -ar 48000 "$TMP/p$i.mov"
  echo "file '$TMP/p$i.mov'" >> "$TMP/list.txt"; i=$((i+1))
done
ffmpeg -hide_banner -loglevel error -y -f concat -safe 0 -i "$TMP/list.txt" -c:v copy \
  -af "loudnorm=I=-16:TP=-1.5:LRA=9" -c:a aac -b:a 192k -ar 48000 assets/kitti_cut.mp4
rm -rf "$TMP"

# Fotók: max. 2400 px, és egy erősen elmosott, kissé sötétített háttér mindegyikhez (1080×1920).
for f in Boti_1_eves-11 KEP01888 Zitaek-7 Zsuzsiek-9 Zitaek-2 Viki-12 KEP07843 KEP02968-Edit; do
  ffmpeg -hide_banner -loglevel error -y -i "$SRC/$f.jpg" -vf "scale='min(2400,iw)':'min(2400,ih)':force_original_aspect_ratio=decrease" -q:v 3 "assets/photos/$f.jpg"
  ffmpeg -hide_banner -loglevel error -y -i "$SRC/$f.jpg" -vf "scale=540:960:force_original_aspect_ratio=increase,crop=540:960,gblur=sigma=28,eq=brightness=-0.06:saturation=0.9,scale=1080:1920" -q:v 4 "assets/photos/$f-bg.jpg"
done

# Logó (palettás PNG → RGBA, 1100 px magas)
ffmpeg -hide_banner -loglevel error -y -i "$SRC/logo-sarga.png" -vf "scale=-1:1100,format=rgba" assets/logo.png
cp "$SRC/cheerful-joyful-playful.mp3" assets/music/cheerful-joyful-playful.mp3
ffprobe -v error -show_entries format=duration -of csv=p=0 assets/kitti_cut.mp4
