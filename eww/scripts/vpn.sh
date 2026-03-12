#!/usr/bin/env bash

# vpn status as JSON for eww vpn-popup

action="${1:-status}"

case "$action" in
  status)
    ts_running=false
    ts_ip=""
    ts_hostname=""
    ts_login=""
    ts_exit_nodes="[]"
    ts_exit_count=0
    ts_peers="[]"
    ts_peer_count=0

    if command -v tailscale &>/dev/null; then
      ts_json=$(tailscale status --json 2>/dev/null)
      state=$(jq -r '.BackendState // empty' <<< "$ts_json")

      if [[ "$state" == "Running" ]]; then
        ts_running=true
        ts_ip=$(jq -r '.TailscaleIPs[0] // empty' <<< "$ts_json")
        ts_hostname=$(jq -r '.Self.HostName // empty' <<< "$ts_json")
        ts_login=$(jq -r '.CurrentTailnet.Name // empty' <<< "$ts_json")

        ts_exit_nodes=$(jq -c '[.Peer | to_entries[]? |
          select(.value.ExitNodeOption) |
          {id: .key, name: .value.HostName, ip: (.value.TailscaleIPs[0] // ""), active: (.value.ExitNode // false)}
        ] // []' <<< "$ts_json" 2>/dev/null || echo '[]')
        ts_exit_count=$(jq 'length' <<< "$ts_exit_nodes" 2>/dev/null || echo 0)

        ts_peers=$(jq -c '[.Peer | to_entries[]? |
          {name: .value.HostName, ip: (.value.TailscaleIPs[0] // ""), online: .value.Online}
        ] // []' <<< "$ts_json" 2>/dev/null || echo '[]')
        ts_peer_count=$(jq 'length' <<< "$ts_peers" 2>/dev/null || echo 0)
      fi
    fi

    wg_active=false
    wg_iface=""
    if command -v wg &>/dev/null; then
      wg_iface=$(wg show interfaces 2>/dev/null | head -1)
      [[ -n "$wg_iface" ]] && wg_active=true
    fi

    jq -nc \
      --argjson ts_running "$ts_running" \
      --arg ts_ip "$ts_ip" \
      --arg ts_hostname "$ts_hostname" \
      --arg ts_login "$ts_login" \
      --argjson ts_exit_nodes "$ts_exit_nodes" \
      --argjson ts_exit_count "$ts_exit_count" \
      --argjson ts_peers "$ts_peers" \
      --argjson ts_peer_count "$ts_peer_count" \
      --argjson wg_active "$wg_active" \
      --arg wg_iface "$wg_iface" \
      '{tailscale:{running:$ts_running,ip:$ts_ip,hostname:$ts_hostname,login:$ts_login,
        exit_nodes:$ts_exit_nodes,exit_count:$ts_exit_count,
        peers:$ts_peers,peer_count:$ts_peer_count},
       wireguard:{active:$wg_active,iface:$wg_iface}}'
    ;;
  ts-up)
    tailscale up 2>/dev/null
    ( sleep 1; data=$(~/.config/eww/scripts/vpn.sh); eww update vpn_data="$data" ) &
    ;;
  ts-down)
    tailscale down 2>/dev/null
    ( sleep 1; data=$(~/.config/eww/scripts/vpn.sh); eww update vpn_data="$data" ) &
    ;;
  ts-exit)
    if [[ -n "$2" ]]; then
      tailscale set --exit-node="$2" 2>/dev/null
    else
      tailscale set --exit-node="" 2>/dev/null
    fi
    ( sleep 0.5; data=$(~/.config/eww/scripts/vpn.sh); eww update vpn_data="$data" ) &
    ;;
  wg-up)
    sudo wg-quick up "${2:-wg0}" 2>/dev/null
    ( sleep 1; data=$(~/.config/eww/scripts/vpn.sh); eww update vpn_data="$data" ) &
    ;;
  wg-down)
    iface="${2:-$(wg show interfaces 2>/dev/null | head -1)}"
    sudo wg-quick down "${iface:-wg0}" 2>/dev/null
    ( sleep 1; data=$(~/.config/eww/scripts/vpn.sh); eww update vpn_data="$data" ) &
    ;;
esac
