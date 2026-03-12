#!/usr/bin/env bash

# check wireguard and tailscale status
# outputs waybar JSON; empty when inactive

parts=()
tooltip_parts=()

if command -v wg &>/dev/null; then
    ifaces=$(wg show interfaces 2>/dev/null)
    if [[ -n "$ifaces" ]]; then
        parts+=("󰖂")
        tooltip_parts+=("wireguard: $ifaces")
    fi
fi

if command -v tailscale &>/dev/null; then
    ts_json=$(tailscale status --json 2>/dev/null)
    state=$(jq -r '.BackendState // empty' <<<"$ts_json")
    if [[ "$state" == "Running" ]]; then
        ts_ip=$(jq -r '.TailscaleIPs[0] // empty' <<<"$ts_json")
        ts_name=$(jq -r '.Self.HostName // empty' <<<"$ts_json")
        ts_exit=$(jq -r '.ExitNodeStatus.ID // empty' <<<"$ts_json")
        parts+=("󰒒")
        tip="tailscale: ${ts_name} ${ts_ip}"
        if [[ -n "$ts_exit" ]]; then
            tip="$tip (exit node)"
        fi
        tooltip_parts+=("$tip")
    fi
fi

if [[ ${#parts[@]} -gt 0 ]]; then
    text="${parts[*]}"
    tip=$(printf '%s\\n' "${tooltip_parts[@]}")
    # strip trailing \n
    tip=${tip%\\n}
    jq -nc --arg text "$text" --arg tooltip "$tip" --arg class "active" \
      '{$text,$class,$tooltip}'
fi
