#!/usr/bin/env bash

# detect remote ssh sessions and optionally disconnect them
# outputs waybar JSON; empty when no remote sessions

if [[ "$1" == "disconnect" ]]; then
  pkill -HUP -f 'sshd-session:.*@' 2>/dev/null
  exit 0
fi

count=$(pgrep -cf 'sshd-session:.*@' 2>/dev/null || echo 0)

if [[ "$count" -gt 0 ]]; then
  # get remote session details
  sessions=$(who 2>/dev/null | awk '$NF ~ /\([0-9]/ {gsub(/[()]/, "", $NF); print $1 "@" $NF}')
  tooltip=${sessions:-"$count remote sessions"}
  # replace newlines with \n for valid JSON
  tooltip=${tooltip//$'\n'/\\n}
  tooltip=${tooltip//\"/\\\"}
  printf '{"text": "●", "class": "active", "tooltip": "%s"}\n' "$tooltip"
fi
