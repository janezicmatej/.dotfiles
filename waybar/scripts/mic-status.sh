#!/usr/bin/env bash

# mic volume for waybar custom module

vol=$(pamixer --default-source --get-volume 2>/dev/null || echo 0)
muted=$(pamixer --default-source --get-mute 2>/dev/null || echo false)

if [[ "$muted" == "true" ]]; then
  printf '{"text": "󰍭", "class": "muted", "tooltip": "mic muted"}\n'
else
  printf '{"text": "󰍬 %d%%", "class": "", "tooltip": "mic %d%%"}\n' "$vol" "$vol"
fi
