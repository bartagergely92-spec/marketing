#!/usr/bin/env bash
# Előkészítés: Kitti vágott beszéde (work/edit.json alapján), fotók, elmosott hátterek, logó, zene.
# Használat: scripts/prepare.sh <forrásmappa>
#   A forrásmappa a Drive „Mit vegyetek fel?” mappa letöltött tartalma, a felvételek így elnevezve:
#   v1_102154.mp4 … v9_104611.mp4 (= VID_20261108_<idő>.mp4), music.mp3, a fotók eredeti néven.
#   A logó a ../mit-hozzatok/assets/logo.png (vagy a Drive „Miket hozzatok?” mappa logo-sarga.png-je).
set -euo pipefail
SRC="$1"; cd "$(dirname "$0")/.."
mkdir -p assets/photos assets/music
TMP=$(mktemp -d); : > "$TMP/list.txt"; i=0
python3 -c "
import json; d=json.load(open('work/edit.json'))
for s in d['segments']: print(s['take'], s['in'], s['frames'], s['fade_out'])" | while read take a n fo; do
  d=$(python3 -c "print(f'{$n/30:.6f}')")
  # Szűrős vágás a felvétel saját időbélyegein: a kép néhány tized mp-cel később indul, mint a hang,
  # ezért mindkettőt ugyanahhoz az A ponthoz viszonyítjuk, és a kép elejét az első képkockával töltjük ki.
  ffmpeg -nostdin -hide_banner -loglevel error -y -threads 2 -i "$SRC/$take.mp4" -filter_complex \
    "[0:v]trim=start=$a,setpts=PTS-$a/TB,fps=30:start_time=0,scale=1080:1920,format=yuv420p[v];[0:a]atrim=start=$a,asetpts=PTS-$a/TB,afade=t=in:d=0.012,afade=t=out:st=$(python3 -c "print(round($d-$fo,3))"):d=$fo[a]" \
    -map "[v]" -map "[a]" -t "$d" -frames:v "$n" -c:v libx264 -crf 18 -preset medium -g 30 -c:a pcm_s16le -ar 48000 "$TMP/p$(printf %02d $i).mov"
  echo "file '$TMP/p$(printf %02d $i).mov'" >> "$TMP/list.txt"; i=$((i+1))
done
ffmpeg -hide_banner -loglevel error -y -f concat -safe 0 -i "$TMP/list.txt" -c:v copy \
  -af "loudnorm=I=-16:TP=-1.5:LRA=9" -c:a aac -b:a 192k -ar 48000 assets/kitti_cut.mp4
rm -rf "$TMP"

for f in $(python3 -c "
import json; d=json.load(open('work/edit.json'))
print(' '.join(p['name'] for p in d['photos'] if not p['name'].startswith('@')))"); do
  ffmpeg -hide_banner -loglevel error -y -i "$SRC/$f.jpg" -vf "scale='min(2400,iw)':'min(2400,ih)':force_original_aspect_ratio=decrease" -q:v 3 "assets/photos/$f.jpg"
  ffmpeg -hide_banner -loglevel error -y -i "$SRC/$f.jpg" -vf "scale=540:960:force_original_aspect_ratio=increase,crop=540:960,gblur=sigma=28,eq=brightness=-0.06:saturation=0.9,scale=1080:1920" -q:v 4 "assets/photos/$f-bg.jpg"
done
cp ../mit-hozzatok/assets/logo.png assets/logo.png
cp "$SRC/music.mp3" assets/music/cheerful-joyful-playful-maksymmalko.mp3
ffprobe -v error -show_entries stream=codec_type,duration,nb_frames -of compact assets/kitti_cut.mp4
