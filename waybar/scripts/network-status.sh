#!/usr/bin/env bash

# combined network + vpn status for waybar
# format: icon ip/cidr [vpn-name ...]

iface=$(ip route show default 2>/dev/null | awk '/default/ {print $5; exit}')
icon="󰖪"
class="disconnected"
net_text=""
vpn_names=()
tooltip_parts=()

# network
if [[ -n "$iface" ]]; then
    cidr=$(ip -4 addr show "$iface" 2>/dev/null | awk '/inet / {print $2; exit}')
    gw=$(ip route show default 2>/dev/null | awk '/default/ {print $3; exit}')

    if [[ "$iface" == wl* ]]; then
        icon="󰖩"
        class="wifi"
        ssid=$(nmcli -t -f active,ssid dev wifi 2>/dev/null | awk -F: '/^yes:/ {print $2}')
        signal=$(nmcli -t -f active,signal dev wifi 2>/dev/null | awk -F: '/^yes:/ {print $2}')
        tooltip_parts+=("$iface: $cidr via $gw")
        [[ -n "$ssid" ]] && tooltip_parts+=("ssid: $ssid (${signal}%)")
    else
        icon="󰈀"
        class="wired"
        tooltip_parts+=("$iface: $cidr via $gw")
    fi
    net_text="$cidr"
else
    tooltip_parts+=("no connection")
fi

# wireguard — show config name (interface name, e.g. wg-office)
if command -v wg &>/dev/null; then
    for wg_iface in $(wg show interfaces 2>/dev/null); do
        wg_cidr=$(ip -4 addr show "$wg_iface" 2>/dev/null | awk '/inet / {print $2; exit}')
        vpn_names+=("$wg_iface")
        tooltip_parts+=("wg: $wg_iface $wg_cidr")
    done
fi

# tailscale — show exit node name if routed, otherwise tailnet name
if command -v tailscale &>/dev/null; then
    ts_json=$(tailscale status --json 2>/dev/null)
    ts_state=$(jq -r '.BackendState // empty' <<<"$ts_json")
    if [[ "$ts_state" == "Running" ]]; then
        ts_ip=$(jq -r '.TailscaleIPs[0] // empty' <<<"$ts_json")
        ts_self=$(jq -r '.Self.HostName // empty' <<<"$ts_json")
        ts_exit_id=$(jq -r '.ExitNodeStatus.ID // empty' <<<"$ts_json")

        if [[ -n "$ts_exit_id" ]]; then
            exit_name=$(jq -r --arg id "$ts_exit_id" '[.Peer[] | select(.ID == $id) | .HostName][0] // "exit"' <<<"$ts_json")
            vpn_names+=("$exit_name")
            tooltip_parts+=("ts: $ts_self $ts_ip → $exit_name")
        else
            tooltip_parts+=("ts: $ts_self $ts_ip")
        fi
    fi
fi

# build text
text="$icon"
[[ -n "$net_text" ]] && text+=" $net_text"
if [[ ${#vpn_names[@]} -gt 0 ]]; then
    text+=" [$(IFS=,; echo "${vpn_names[*]}")]"
fi

tooltip=$(printf '%s\n' "${tooltip_parts[@]}")

jq -nc --arg text "$text" --arg class "$class" --arg tooltip "$tooltip" \
  '{$text,$class,$tooltip}'
