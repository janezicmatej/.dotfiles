#!/usr/bin/env bash
# NOTE:(@janezicmatej) layout adapted from github.com/nejcr/grind statusline.js:
# model + context, repo, 5h/7d limits, session id, optional dev-links row

input=$(cat)

# one jq call emits every field as a quoted shell assignment
eval "$(jq -r '
  def s: tostring | @sh;
  "model=\(.model.display_name // "" | s)",
  "used=\(.context_window.total_input_tokens // 0 | s)",
  "total=\(.context_window.context_window_size // 0 | s)",
  "ctx_pct=\(.context_window.used_percentage // "" | s)",
  "cwd=\(.workspace.current_dir // "" | s)",
  "project_dir=\(.workspace.project_dir // "" | s)",
  "session_id=\(.session_id // "" | s)"
' <<<"$input")"

# claude only sends rate_limits after the first api response, so a fresh session
# would show none until its first prompt; every refresh that has them writes the
# last known limits next to the config, and a fresh session reads those back dimmed
cfg_dir=${CLAUDE_CONFIG_DIR:-$HOME/.claude}
limits_cache=$cfg_dir/statusline-limits.json
read_limits() {
  jq -r '
    def s: tostring | @sh;
    "five_pct=\(.five_hour.used_percentage // "" | s)",
    "five_reset=\(.five_hour.resets_at // "" | s)",
    "seven_pct=\(.seven_day.used_percentage // "" | s)",
    "seven_reset=\(.seven_day.resets_at // "" | s)"
  ' 2>/dev/null
}
current=$(jq -c '.rate_limits // {} | with_entries(select(.value.used_percentage != null))' <<<"$input")
stale=""
if [[ $current != "{}" ]]; then
  eval "$(read_limits <<<"$current")"
  # merged, not replaced: a turn carrying one window must not wipe the other;
  # written then renamed so a concurrent session never reads it half-written
  merged=$(jq -c --argjson cur "$current" '. * $cur' "$limits_cache" 2>/dev/null) || merged=$current
  tmp=$limits_cache.$$.tmp
  if { printf '%s\n' "$merged" > "$tmp"; } 2>/dev/null; then mv -f "$tmp" "$limits_cache" 2>/dev/null || rm -f "$tmp"; fi
elif [[ -f $limits_cache ]]; then
  stale=1
  eval "$(read_limits < "$limits_cache")"
fi

R=$'\e[0m' C=$'\e[36m' G=$'\e[32m' Y=$'\e[33m' RE=$'\e[31m' D=$'\e[2m'

# "Claude 3.5 Sonnet" -> "Sonnet 3.5", "Claude Fable 5.1" -> "Fable 5.1"
model=$(sed -E -e 's/^Claude +([0-9.]+) +([A-Za-z0-9_]+)$/\2 \1/; t' -e 's/^Claude +//' <<<"${model:-unknown}")

# 61234 -> 61.2k, half-up rounding to match Math.round
fmt() { awk -v n="$1" 'BEGIN { if (n >= 1000) printf "%.1fk", n / 1000; else printf "%d", n }'; }
round() { awk -v x="$1" 'BEGIN { printf "%d", int(x + 0.5) }'; }

# same scale for context and limits: green under 50, yellow under 80, red above
color_for() {
  if (( $1 >= 80 )); then printf %s "$RE"; elif (( $1 >= 50 )); then printf %s "$Y"; else printf %s "$G"; fi
}

# repo: origin url from the host onwards (host/group/repo), else the folder name
repo=""
if url=$(git -C "$cwd" --no-optional-locks remote get-url origin 2>/dev/null); then
  repo=$(sed -E \
    -e 's#^[^@/]+@([^:/]+):(.+)$#\1/\2#; t done' \
    -e 's#^[a-z+]+://([^@/]+@)?([^/:]+)(:[0-9]+)?/(.+)$#\2/\4#I; t done' \
    -e 's/.*//' -e ':done' -e 's#/+$##; s/\.git$//' <<<"$url")
fi
if [[ -z $repo ]]; then
  top=$(git -C "$cwd" --no-optional-locks rev-parse --show-toplevel 2>/dev/null)
  repo=$(basename "${top:-${project_dir:-$cwd}}")
fi

# limits, same shape as the context group: "5h 42% (15:36)" and "7d 81% (5d)"
# the 5h window resets within hours so the clock answers "when", the 7d one is
# far enough out that days are all that matters; a rolled-over window shows a dash
now=$(date +%s)
rl_part() {
  local label=$1 pct=$2 reset=${3%.*} mode=$4 p s left
  [[ -n $pct ]] || return 0
  s=$(( ${reset:-0} - now ))
  if [[ -z $reset ]] || (( s <= 0 )); then
    printf '%s%s —%s' "$D" "$label" "$R"
    return 0
  fi
  p=$(round "$pct")
  case $mode in
    clock) left=$(date -d "@$reset" +%H:%M) ;;
    days) if (( s < 86400 )); then left="$(( (s + 3599) / 3600 ))h"; else left="$(( (s + 43200) / 86400 ))d"; fi ;;
  esac
  # last known values from the cache render fully dim to say they may be behind
  local col; col=$(color_for "$p"); [[ -n $stale ]] && col=$D
  printf '%s%s%s %s%s%%%s %s(%s)%s' "$D" "$label" "$R" "$col" "$p" "$R" "$D" "$left" "$R"
}

groups=()

session="${C}${model}${R} ${G}$(fmt "$used")/$(fmt "$total")${R}"
if [[ -n $ctx_pct ]]; then
  p=$(round "$ctx_pct")
  session+=" ${D}(${R}$(color_for "$p")${p}%${R}${D})${R}"
fi
groups+=("$session")

[[ -n $repo ]] && groups+=("${C}${repo}${R}")

# limits are only sent once the session has talked to the api
part=$(rl_part 5h "$five_pct" "$five_reset" clock); [[ -n $part ]] && groups+=("$part")
part=$(rl_part 7d "$seven_pct" "$seven_reset" days); [[ -n $part ]] && groups+=("$part")

# full session id so it can be pasted into claude --resume, dim and last
[[ -n $session_id ]] && groups+=("${D}${session_id}${R}")

sep=" ${D}│${R} "
out=""
for g in "${groups[@]}"; do out+="${out:+$sep}$g"; done
printf '%s\n' "$out"

# pinned dev links, opt-in per project: .claude/dev-links.json adds a second row
# a value is either "url" or {url, note}, note being a throwaway local credential
link_file=""
for d in "$project_dir" "$cwd"; do
  [[ -n $d && -f $d/.claude/dev-links.json ]] && { link_file=$d/.claude/dev-links.json; break; }
done
[[ -n $link_file ]] || exit 0

pins=$(jq -r '
  to_entries[]
  | { label: .key,
      url: (if (.value | type) == "string" then .value
            elif (.value | type) == "object" then .value.url else null end),
      note: (if (.value | type) == "object" and (.value.note | type) == "string" then .value.note else "" end) }
  | select((.url | type) == "string" and (.url | test("^https?://")))
  | [.label, .url, .note] | @tsv
' "$link_file" 2>/dev/null) || exit 0
[[ -n $pins ]] || exit 0

# bare urls rather than osc 8: claude code resolves plain http:// on ctrl+click
# itself; COLUMNS is the only readable width since stdout is captured
cols=${COLUMNS:-120}
[[ $cols =~ ^[0-9]+$ ]] || cols=120
gap=3
row="" width=0
while IFS=$'\t' read -r label url note; do
  len=$(( ${#label} + 1 + ${#url} + (${#note} > 0 ? ${#note} + 3 : 0) ))
  cost=$(( width ? len + gap : len ))
  if (( width && width + cost > cols - 4 )); then
    printf '%s\n' "$row"
    row="" width=$len
  else
    width=$(( width + cost ))
  fi
  cell="${C}${label}${R} ${D}${url}${R}"
  [[ -n $note ]] && cell+=" ${Y}${note}${R}"
  row+="${row:+${D} · ${R}}$cell"
done <<<"$pins"
[[ -n $row ]] && printf '%s\n' "$row"
exit 0
