#!/usr/bin/env bash

# audio + brightness info for eww volume-popup

action="${1:-status}"

case "$action" in
  status)
    default_sink=$(pactl get-default-sink 2>/dev/null)
    default_source=$(pactl get-default-source 2>/dev/null)

    # get all sink+source info in one pactl call, extract volume/mute + device lists
    all_data=$(pactl --format=json list sinks 2>/dev/null)
    sinks=$(jq -c --arg d "$default_sink" \
      '[.[] | {name: .description, sink_name: .name, active: (.name == $d)}]' <<< "$all_data" 2>/dev/null || echo '[]')
    # extract default sink volume+mute
    volume=$(jq --arg d "$default_sink" \
      '[.[] | select(.name == $d)][0] | .volume | to_entries[0].value.value_percent | rtrimstr("%") | tonumber' <<< "$all_data" 2>/dev/null || echo 0)
    muted=$(jq --arg d "$default_sink" \
      '[.[] | select(.name == $d)][0].mute' <<< "$all_data" 2>/dev/null || echo false)

    all_sources=$(pactl --format=json list sources 2>/dev/null)
    sources=$(jq -c --arg d "$default_source" \
      '[.[] | select(.name | test("monitor$") | not) | {name: .description, source_name: .name, active: (.name == $d)}]' <<< "$all_sources" 2>/dev/null || echo '[]')
    mic_volume=$(jq --arg d "$default_source" \
      '[.[] | select(.name == $d)][0] | .volume | to_entries[0].value.value_percent | rtrimstr("%") | tonumber' <<< "$all_sources" 2>/dev/null || echo 0)
    mic_muted=$(jq --arg d "$default_source" \
      '[.[] | select(.name == $d)][0].mute' <<< "$all_sources" 2>/dev/null || echo false)

    brightness=$(brightnessctl -m 2>/dev/null | cut -d, -f5 | tr -d '%')
    sink_count=$(jq 'length' <<< "$sinks" 2>/dev/null || echo 0)
    source_count=$(jq 'length' <<< "$sources" 2>/dev/null || echo 0)

    jq -nc \
      --argjson volume "${volume:-0}" \
      --argjson muted "${muted:-false}" \
      --argjson mic_volume "${mic_volume:-0}" \
      --argjson mic_muted "${mic_muted:-false}" \
      --argjson brightness "${brightness:-0}" \
      --argjson sinks "${sinks:-[]}" \
      --argjson sources "${sources:-[]}" \
      --argjson sink_count "${sink_count:-0}" \
      --argjson source_count "${source_count:-0}" \
      '{$volume,$muted,$mic_volume,$mic_muted,$brightness,$sinks,$sources,$sink_count,$source_count}'
    ;;
  set-sink)
    pactl set-default-sink "$2"
    ( data=$(~/.config/eww/scripts/volume.sh); eww update vol="$data" ) &
    ;;
  set-source)
    pactl set-default-source "$2"
    ( data=$(~/.config/eww/scripts/volume.sh); eww update vol="$data" ) &
    ;;
  toggle-mute)
    pamixer -t
    ( data=$(~/.config/eww/scripts/volume.sh); eww update vol="$data" ) &
    ;;
  toggle-mic)
    pamixer --default-source -t
    ( data=$(~/.config/eww/scripts/volume.sh); eww update vol="$data" ) &
    ;;
esac
