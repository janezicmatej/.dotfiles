#!/usr/bin/env bash

# network info as JSON for eww network-popup

action="${1:-status}"

case "$action" in
  status)
    active=$(nmcli -t -f DEVICE,TYPE,STATE,CONNECTION device status 2>/dev/null \
      | grep ':connected:' | head -1)
    iface=$(echo "$active" | cut -d: -f1)
    conn_type=$(echo "$active" | cut -d: -f2)
    conn_name=$(echo "$active" | cut -d: -f4-)

    ip=$(ip -4 -o addr show "$iface" 2>/dev/null | awk '{print $4}' | cut -d/ -f1)
    gateway=$(ip route show default dev "$iface" 2>/dev/null | awk '{print $3}')

    networks="[]"
    net_count=0

    # always check active wifi regardless of primary connection type
    ssid=$(nmcli -t -f active,ssid dev wifi 2>/dev/null | grep '^yes' | cut -d: -f2-)
    signal=$(nmcli -t -f active,signal dev wifi 2>/dev/null | grep '^yes' | cut -d: -f2-)
    signal=${signal:-0}

    # scan nearby wifi
    saved=$(nmcli -t -f NAME connection show 2>/dev/null | sort -u)
    # replace last 3 colons with tabs to handle SSIDs containing colons
    all_wifi=$(nmcli -t -f SSID,SIGNAL,SECURITY,IN-USE dev wifi list --rescan no 2>/dev/null \
      | sed 's/:\([^:]*\):\([^:]*\):\([^:]*\)$/\t\1\t\2\t\3/' \
      | awk -F'\t' 'NF>=3 && $1!=""' \
      | sort -t$'\t' -k4,4r -k2,2rn \
      | awk -F'\t' '!seen[$1]++')

    # known networks nearby
    networks=$(echo "$all_wifi" \
      | while IFS=$'\t' read -r s sig sec use; do
          echo "$saved" | grep -qxF "$s" && printf '%s\t%s\n' "$s" "$sig"
        done \
      | head -10 \
      | jq -Rnc --arg active "$ssid" '[inputs | split("\t") |
          {ssid:.[0], signal:(.[1]|tonumber), active:(.[0] == $active)}]')
    net_count=$(jq 'length' <<< "$networks" 2>/dev/null || echo 0)

    # unknown networks nearby
    unknown=$(echo "$all_wifi" \
      | while IFS=$'\t' read -r s sig sec use; do
          echo "$saved" | grep -qxF "$s" || printf '%s\t%s\t%s\n' "$s" "$sig" "$sec"
        done \
      | head -5 \
      | jq -Rnc '[inputs | split("\t") |
          {ssid:.[0], signal:(.[1]|tonumber), security:.[2]}]')
    unknown_count=$(jq 'length' <<< "$unknown" 2>/dev/null || echo 0)

    jq -nc \
      --arg type "${conn_type:-none}" \
      --arg iface "${iface:-none}" \
      --arg ip "${ip:-none}" \
      --arg gateway "${gateway:-none}" \
      --arg ssid "$ssid" \
      --argjson signal "${signal:-0}" \
      --arg conn_name "$conn_name" \
      --argjson count "${net_count:-0}" \
      --argjson networks "${networks:-[]}" \
      --argjson unknown_count "${unknown_count:-0}" \
      --argjson unknown "${unknown:-[]}" \
      '{$type,$iface,$ip,$gateway,$ssid,$signal,$conn_name,$count,$networks,$unknown_count,$unknown}'
    ;;
  connect)
    ( nmcli dev wifi connect "$2" 2>/dev/null; sleep 1; data=$(~/.config/eww/scripts/network.sh); eww update net="$data" ) &
    ;;
  disconnect)
    ( nmcli connection down "$2" 2>/dev/null; sleep 1; data=$(~/.config/eww/scripts/network.sh); eww update net="$data" ) &
    ;;
  connect-new)
    ssid="$2"
    pass=$(zenity --entry --hide-text --title="WiFi" --text="Password for $ssid" 2>/dev/null)
    ( [[ -n "$pass" ]] && nmcli dev wifi connect "$ssid" password "$pass" 2>/dev/null; sleep 1; data=$(~/.config/eww/scripts/network.sh); eww update net="$data" ) &
    ;;
esac
