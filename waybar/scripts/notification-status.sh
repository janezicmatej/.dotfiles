#!/usr/bin/env bash

# wrap swaync subscription, hide when no notifications

swaync-client -swb 2>/dev/null | while read -r line; do
  count=$(echo "$line" | jq -r '.text // "0"')
  class=$(echo "$line" | jq -r '.class // "none"')

  if [[ "$count" == "0" ]]; then
    echo '{"text": "", "class": "none"}'
  else
    jq -nc --arg text "󰂚 $count" --arg class "$class" '{$text,$class}'
  fi
done
