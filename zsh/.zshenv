# default configuration as per https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html
export XDG_CONFIG_HOME="$HOME/.config"
export XDG_CACHE_HOME="$HOME/.cache"
export XDG_DATA_HOME="$HOME/.local/share"
export XDG_STATE_HOME="$HOME/.local/state"

# deduplicate path
typeset -U path

# editor
export EDITOR=nvim

# go
export GOPATH="$XDG_DATA_HOME/go"
export GOMODCACHE="$XDG_CACHE_HOME/go/mod"

# ggman
export GGROOT="$HOME/git"

# name
export NAME="Matej Janežič"

# starship nest config into a folder, default is ~/.config/starship.toml
export STARSHIP_CONFIG="$XDG_CONFIG_HOME/starship/config.toml"

# cliphist
export CLIPHIST_DB_PATH="/tmp/cliphist-db"

# fzf
export FZF_DEFAULT_OPTS="--cycle --bind 'tab:toggle-up,btab:toggle-down' --pointer '>' --color '16' --border 'double' --ansi --highlight-line --header 'Navigate with ARROW KEYS or TAB/S-TAB. Select with ENTER.'"
