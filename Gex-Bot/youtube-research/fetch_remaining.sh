#!/bin/bash
# Paced retry for the gexbot videos the first pass missed.
# YouTube rate-limits the subtitle endpoint hard; metadata calls are cheap.
cd /home/user/CTrader-Bots/Gex-Bot/youtube-research
OUT=transcripts/gexbot-channel
LOG=$OUT/FETCH_LOG.txt
: > $LOG
YT="yt-dlp --skip-download --ignore-no-formats-error --extractor-args youtube:player_client=web_embedded"

# Spanish livestreams (auto-translated English is available for these)
SPANISH="eonlRevJwsA K-RiP1RHlNk gzOuu4ndHCI k2yFrQ2pMEU e5Uz6vDp694 q-x9mCeQPvw"
# Everything else the first pass reported as having no English subs
OTHERS="1TH2WaA7SeE 3TWSSWow1a4 4v5OzQs03SE 6i6Dtth-0Ik 79qxyM-e178 DROy4T9gwWs \
GkluIe8Ioyg N3Q704qw4Ko O9h0eDUW_4Y SYdkW1yKk3A Ue6mKuT2tsU YnQxDjLjXEU \
Z6PGAUZv1IE h5YZ4kXKc_s n5X3zgWmq3M psxtILQn2BE xgDUDAcoOK0 zonIw39fcDs"

echo "== pass 1: which of the remaining actually have captions ==" >> $LOG
HAVE=""
for V in $OTHERS; do
  R=$($YT --list-subs "https://youtu.be/$V" 2>&1)
  if echo "$R" | grep -q "has no automatic captions" && echo "$R" | grep -q "has no subtitles"; then
    echo "$V: genuinely no captions" >> $LOG
  elif echo "$R" | grep -qE "^en |Available (automatic captions|subtitles)"; then
    echo "$V: HAS captions" >> $LOG; HAVE="$HAVE $V"
  else
    echo "$V: unclear -- $(echo "$R" | tail -1)" >> $LOG
  fi
  sleep 5
done

echo "" >> $LOG
echo "== pass 2: download (spanish + any found above) ==" >> $LOG
for V in $SPANISH $HAVE; do
  for TRY in 1 2 3 4 5; do
    R=$($YT --write-auto-subs --write-subs --sub-langs "en" --sub-format "vtt" \
        -o "$OUT/%(upload_date)s-%(id)s.%(ext)s" "https://youtu.be/$V" 2>&1)
    F=$(ls $OUT/*-$V.en.vtt 2>/dev/null | head -1)
    if [ -n "$F" ] && [ -s "$F" ]; then
      T="${F%.en.vtt}.txt"
      python3 vtt_to_text.py "$F" "$T" >/dev/null 2>&1
      echo "$V: ok on try $TRY -- $(wc -w < "$T") words" >> $LOG
      break
    fi
    if [ $TRY -eq 5 ]; then echo "$V: FAILED after 5 tries -- $(echo "$R" | grep ERROR | head -1)" >> $LOG; fi
    sleep 90
  done
  sleep 30
done
echo "" >> $LOG
echo "DONE $(date -u +%FT%TZ)" >> $LOG
