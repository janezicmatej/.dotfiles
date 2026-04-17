#!/bin/sh
input=$(cat)

model=$(echo "$input" | jq -r '.model.display_name // empty')
total_in=$(echo "$input" | jq -r '.context_window.total_input_tokens // 0')
total_out=$(echo "$input" | jq -r '.context_window.total_output_tokens // 0')
ctx=$(echo "$input" | jq -r '.context_window.used_percentage // empty')
five_hr=$(echo "$input" | jq -r '.rate_limits.five_hour.used_percentage // empty')
five_hr_reset=$(echo "$input" | jq -r '.rate_limits.five_hour.resets_at // empty')
seven_day=$(echo "$input" | jq -r '.rate_limits.seven_day.used_percentage // empty')
seven_day_reset=$(echo "$input" | jq -r '.rate_limits.seven_day.resets_at // empty')

# format seconds until reset as human-readable
fmt_remaining() {
    now=$(date +%s)
    diff=$(( $1 - now ))
    [ "$diff" -le 0 ] && return
    h=$(( diff / 3600 ))
    m=$(( (diff % 3600) / 60 ))
    if [ "$h" -gt 0 ]; then
        printf '%dh%dm' "$h" "$m"
    else
        printf '%dm' "$m"
    fi
}

parts=""

[ -n "$model" ] && parts="$model"

if [ -n "$total_in" ] && [ "$total_in" != "0" ]; then
    total=$((total_in + total_out))
    parts="${parts:+$parts | }tokens:${total}"
fi

if [ -n "$ctx" ]; then
    parts="${parts:+$parts | }ctx:$(printf '%.0f' "$ctx")%"
fi

if [ -n "$five_hr" ]; then
    five_hr_ttl=""
    [ -n "$five_hr_reset" ] && five_hr_ttl=$(fmt_remaining "$five_hr_reset")
    parts="${parts:+$parts | }5h:$(printf '%.0f' "$five_hr")%${five_hr_ttl:+($five_hr_ttl)}"
fi

if [ -n "$seven_day" ]; then
    seven_day_ttl=""
    [ -n "$seven_day_reset" ] && seven_day_ttl=$(fmt_remaining "$seven_day_reset")
    parts="${parts:+$parts | }7d:$(printf '%.0f' "$seven_day")%${seven_day_ttl:+($seven_day_ttl)}"
fi

[ -n "$parts" ] && printf '%s' "$parts"
