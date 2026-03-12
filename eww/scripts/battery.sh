#!/usr/bin/env bash

# battery info as JSON for eww battery-popup

action="${1:-status}"

if [[ "$action" == "set-profile" ]]; then
  powerprofilesctl set "$2"
  ( data=$(~/.config/eww/scripts/battery.sh); eww update bat="$data" ) &
  exit 0
fi

bat_path=$(echo /sys/class/power_supply/BAT* 2>/dev/null | awk '{print $1}')

if [[ ! -d "$bat_path" ]]; then
  jq -nc '{capacity:0,status:"No battery",power:"0",time:"",cycles:0,profile:"unknown"}'
  exit 0
fi

capacity=$(cat "$bat_path/capacity" 2>/dev/null || echo 0)
status=$(cat "$bat_path/status" 2>/dev/null || echo "Unknown")

power_uw=$(cat "$bat_path/power_now" 2>/dev/null || echo 0)
power=$(awk -v p="$power_uw" 'BEGIN{printf "%.1f", p/1000000}')

cycles=$(cat "$bat_path/cycle_count" 2>/dev/null || echo 0)
[[ "$cycles" =~ ^[0-9]+$ ]] || cycles=0

bat_upower=$(upower -e 2>/dev/null | grep BAT | head -1)
time_str=""
if [[ -n "$bat_upower" ]]; then
  time_str=$(upower -i "$bat_upower" 2>/dev/null | awk '/time to/{print $4, $5}')
fi

profile=$(powerprofilesctl get 2>/dev/null || echo "unknown")

jq -nc \
  --argjson capacity "$capacity" \
  --arg status "$status" \
  --arg power "$power" \
  --arg time "$time_str" \
  --argjson cycles "${cycles:-0}" \
  --arg profile "$profile" \
  '{$capacity,$status,$power,$time,$cycles,$profile}'
