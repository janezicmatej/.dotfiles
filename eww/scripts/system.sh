#!/usr/bin/env bash

# system metrics as JSON for eww system-popup

# delta-based cpu: sample /proc/stat twice 0.5s apart
read -r _ u1 n1 s1 i1 _ < /proc/stat
sleep 0.5
read -r _ u2 n2 s2 i2 _ < /proc/stat
cpu=$(( (u2+n2+s2 - u1-n1-s1) * 100 / (u2+n2+s2+i2 - u1-n1-s1-i1) ))

ram_info=$(free -b | awk '/^Mem:/{printf "%.0f %.1f %.1f", $3/$2*100, $3/1073741824, $2/1073741824}')
ram_percent=$(awk '{print $1}' <<< "$ram_info")
ram_used=$(awk '{printf "%.1f", $2}' <<< "$ram_info")
ram_total=$(awk '{printf "%.1f", $3}' <<< "$ram_info")

temp=$(cat /sys/class/thermal/thermal_zone*/temp 2>/dev/null | sort -rn | head -1)
temp=$(( ${temp:-0} / 1000 ))

disk_info=$(df -h / | awk 'NR==2{gsub(/%/,""); printf "%s %s %s", $5, $3, $2}')
disk_percent=$(awk '{print $1}' <<< "$disk_info")
disk_used=$(awk '{print $2}' <<< "$disk_info")
disk_total=$(awk '{print $3}' <<< "$disk_info")

swap=$(free -h | awk '/^Swap:/{printf "%s/%s", $3, $2}')
load=$(awk '{print $1, $2, $3}' /proc/loadavg)
uptime_str=$(uptime -p 2>/dev/null | sed 's/up //' || echo "n/a")

jq -nc \
  --argjson cpu "${cpu:-0}" \
  --argjson ram_percent "${ram_percent:-0}" \
  --arg ram_used "${ram_used:-0}Gi" \
  --arg ram_total "${ram_total:-0}Gi" \
  --argjson temp "${temp:-0}" \
  --argjson disk_percent "${disk_percent:-0}" \
  --arg disk_used "$disk_used" \
  --arg disk_total "$disk_total" \
  --arg swap "$swap" \
  --arg load "$load" \
  --arg uptime "$uptime_str" \
  '{$cpu,$ram_percent,$ram_used,$ram_total,$temp,$disk_percent,$disk_used,$disk_total,$swap,$load,$uptime}'
