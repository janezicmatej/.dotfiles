#!/usr/bin/env bash

# bluetooth device info as JSON for eww bluetooth-popup

action="${1:-status}"

case "$action" in
  status)
    powered=$(bluetoothctl show 2>/dev/null | grep -q "Powered: yes" && echo true || echo false)

    devices="[]"
    count=0
    if [[ "$powered" == "true" ]]; then
      # get connected devices in one pass
      devices=$(bluetoothctl devices Connected 2>/dev/null | while read -r _ mac name; do
        info=$(bluetoothctl info "$mac" 2>/dev/null)
        battery=$(awk '/Battery Percentage:/{gsub(/[()]/,""); print $4}' <<< "$info")
        jq -nc --arg name "$name" --arg mac "$mac" --argjson battery "${battery:--1}" \
          '{$name,$mac,$battery}'
      done | jq -sc '.')
      [[ -z "$devices" || "$devices" == "null" ]] && devices="[]"
      count=$(jq 'length' <<< "$devices" 2>/dev/null || echo 0)
    fi

    jq -nc \
      --argjson powered "$powered" \
      --argjson count "$count" \
      --argjson devices "$devices" \
      '{$powered,$count,$devices}'
    ;;
  toggle-power)
    if bluetoothctl show 2>/dev/null | grep -q "Powered: yes"; then
      bluetoothctl power off
    else
      bluetoothctl power on
    fi
    ( sleep 0.5; data=$(~/.config/eww/scripts/bluetooth.sh); eww update bt="$data" ) &
    ;;
  disconnect)
    bluetoothctl disconnect "$2"
    ( sleep 0.5; data=$(~/.config/eww/scripts/bluetooth.sh); eww update bt="$data" ) &
    ;;
esac
