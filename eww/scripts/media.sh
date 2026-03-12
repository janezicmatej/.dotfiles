#!/usr/bin/env bash

# media player info as JSON for eww media-popup

action="${1:-status}"

case "$action" in
  status)
    players=$(playerctl -l 2>/dev/null | head -10)
    if [[ -z "$players" ]]; then
      jq -nc '{count:0,players:[]}'
      exit 0
    fi

    result="[]"
    while IFS= read -r name; do
      status=$(playerctl -p "$name" status 2>/dev/null || echo "Stopped")
      artist=$(playerctl -p "$name" metadata artist 2>/dev/null || echo "")
      title=$(playerctl -p "$name" metadata title 2>/dev/null || echo "")
      album=$(playerctl -p "$name" metadata album 2>/dev/null || echo "")

      # clean up player name for display
      display=${name%%.*}

      result=$(jq -c --arg name "$name" --arg display "$display" \
        --arg status "$status" --arg artist "$artist" \
        --arg title "$title" --arg album "$album" \
        '. + [{name:$name, display:$display, status:$status, artist:$artist, title:$title, album:$album}]' <<< "$result")
    done <<< "$players"

    count=$(jq 'length' <<< "$result")
    jq -nc --argjson count "$count" --argjson players "$result" '{$count,$players}'
    ;;
  play-pause)
    playerctl -p "$2" play-pause 2>/dev/null
    ( sleep 0.3; data=$(~/.config/eww/scripts/media.sh); eww update media="$data" ) &
    ;;
  next)
    playerctl -p "$2" next 2>/dev/null
    ( sleep 0.5; data=$(~/.config/eww/scripts/media.sh); eww update media="$data" ) &
    ;;
  prev)
    playerctl -p "$2" previous 2>/dev/null
    ( sleep 0.5; data=$(~/.config/eww/scripts/media.sh); eww update media="$data" ) &
    ;;
esac
