#!/usr/bin/env bash

url="http://localhost:10767/api/v1/playback"

status_raw=$(curl -s --max-time 2 "$url/is-playing")

# CASE 1: API is totally unreachable (App closed)
if [[ -z "$status_raw" ]]; then
    echo '{"text": "offline", "class": "offline", "alt": "offline"}'
    exit 0
fi

# Extract playing status, defaulting to false if null
is_playing=$(echo "$status_raw" | jq -r '.is_playing // false')

# 2. Get song info
info_raw=$(curl -s --max-time 2 "$url/now-playing")

# CASE 2 & 3: Handle empty metadata vs. active metadata
echo "$info_raw" | jq -c \
    --argjson is_playing "$is_playing" \
    '
    # Helper function to escape & for Pango
    def pango_escape: sub("&"; "&amp;"; "g");

    if (.info.name == null or .info.name == "") then
        {text: "idle", class: "paused"}
    else
        {
          text: "\(.info.name | pango_escape) - \(.info.artistName | pango_escape)",
          tooltip: "\(.info.albumName | pango_escape // "Unknown")",
          class: (if $is_playing then "playing" else "paused" end)
        }
    end'
