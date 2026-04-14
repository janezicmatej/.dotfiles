#!/usr/bin/env bash

# screenshot focused monitor with satty
output=$(swaymsg -t get_outputs | jq -r '.[] | select(.focused) | .name')
grim -o "$output" - | satty -f - --fullscreen --early-exit

