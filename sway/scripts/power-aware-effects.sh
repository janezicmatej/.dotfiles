#!/usr/bin/env bash
# toggle swayfx blur and shadows based on battery state

while true; do
  status=$(cat /sys/class/power_supply/BAT1/status 2>/dev/null || cat /sys/class/power_supply/BAT0/status)

  if [ "$status" = "Discharging" ]; then
    swaymsg blur off
    swaymsg shadows off
  else
    swaymsg blur on
    swaymsg shadows on
  fi

  sleep 30
done
