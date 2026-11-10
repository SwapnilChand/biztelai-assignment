#!/usr/bin/env bash
# Join the laptop recording with a screen recording made on the phone.
# usage: demo/assemble.sh laptop-part.mp4 phone-recording.mp4 out.mp4
set -euo pipefail
LAPTOP=$1 PHONE=$2 OUT=$3
FONT=/usr/share/fonts/liberation/LiberationSans-Bold.ttf
TMP=$(mktemp -d)
# phone clip: fit into the 1280x800 stage, same caption bar as the laptop part, no audio
ffmpeg -loglevel error -y -i "$PHONE" -an -vf "fps=30,scale=-2:800,pad=1280:800:(ow-iw)/2:0:color=0x2a2f34,pad=1280:880:0:80:color=0x14171a,drawtext=fontfile=$FONT:text='Opened and used from my phone on the same Wi-Fi':fontcolor=white:fontsize=30:x=32:y=24,drawbox=x=0:y=0:w=10:h=80:color=0xf2b400:t=fill,format=yuv420p" -c:v libx264 -crf 22 "$TMP/phone.mp4"
printf "file '%s'\nfile '%s'\n" "$(realpath "$LAPTOP")" "$TMP/phone.mp4" > "$TMP/list.txt"
ffmpeg -loglevel error -y -f concat -safe 0 -i "$TMP/list.txt" -c copy -movflags +faststart "$OUT"
ffprobe -v error -show_entries format=duration -of csv=p=0 "$OUT"
