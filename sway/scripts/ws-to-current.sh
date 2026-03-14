#!/bin/sh
# switch to workspace and move it to the currently focused output
output=$(swaymsg -t get_outputs | jq -r '.[] | select(.focused) | .name')
swaymsg "workspace number $1, move workspace to output $output"
