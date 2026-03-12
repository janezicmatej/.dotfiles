#!/usr/bin/env bash

# keyboard layout info as JSON for eww keyboard-popup

action="${1:-status}"

case "$action" in
  status)
    inputs=$(swaymsg -t get_inputs 2>/dev/null)

    current=$(jq -r '[.[] | select(.type == "keyboard")] | .[0].xkb_active_layout_name // "unknown"' <<< "$inputs")
    layouts=$(jq -c '[.[] | select(.type == "keyboard")] | .[0].xkb_layout_names // []' <<< "$inputs")
    layout_count=$(jq 'length' <<< "$layouts" 2>/dev/null || echo 0)

    keyboards=$(jq -c '[.[] | select(.type == "keyboard") |
      {id: .identifier, name: .name, layout: .xkb_active_layout_name}] | unique_by(.name)' <<< "$inputs")
    kb_count=$(jq 'length' <<< "$keyboards" 2>/dev/null || echo 0)

    jq -nc \
      --arg current "${current:-unknown}" \
      --argjson layouts "${layouts:-[]}" \
      --argjson layout_count "${layout_count:-0}" \
      --argjson keyboards "${keyboards:-[]}" \
      --argjson kb_count "${kb_count:-0}" \
      '{$current,$layouts,$layout_count,$keyboards,$kb_count}'
    ;;
  switch)
    swaymsg input type:keyboard xkb_switch_layout next 2>/dev/null
    ( sleep 0.3; data=$(~/.config/eww/scripts/keyboard.sh); eww update kbd="$data" ) &
    ;;
  set-layout)
    swaymsg input type:keyboard xkb_switch_layout "$2" 2>/dev/null
    ( sleep 0.3; data=$(~/.config/eww/scripts/keyboard.sh); eww update kbd="$data" ) &
    ;;
esac
