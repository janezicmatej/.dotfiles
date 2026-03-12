#!/usr/bin/env bash

# toggle an eww popup
# opens on the currently focused monitor

POPUPS=(system-popup battery-popup network-popup vpn-popup volume-popup bluetooth-popup keyboard-popup media-popup)

target="$1"

if [[ -z "$target" ]]; then
  echo "usage: popup.sh <popup-name|close-all>" >&2
  exit 1
fi

if [[ "$target" == "close-all" ]]; then
  eww close "${POPUPS[@]}" 2>/dev/null
  exit 0
fi

# check if target is already open
if eww active-windows 2>/dev/null | grep -q "$target"; then
  eww close "$target" 2>/dev/null
else
  # close others, open popup
  screen=$(swaymsg -t get_outputs 2>/dev/null \
    | jq '[.[] | .focused] | index(true) // 0')
  eww close "${POPUPS[@]}" 2>/dev/null
  eww open --screen "${screen:-0}" "$target"
fi
