# default configuration as per https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html
export XDG_CONFIG_HOME="$HOME/.config"
export XDG_CACHE_HOME="$HOME/.cache"
export XDG_DATA_HOME="$HOME/.local/share"
export XDG_STATE_HOME="$HOME/.local/state"

# ~/.local/bin
export PATH="$HOME/.local/bin:$PATH"

# editor
export EDITOR=nvim

# go
export GOPATH="$XDG_DATA_HOME/go"
export GOMODCACHE="$XDG_CACHE_HOME/go/mod"
export PATH="$GOPATH/bin:$PATH"

# ggman
export GGROOT="$HOME/git"


# name
export NAME="Matej Janežič"

# starship nest config into a folder, default is ~/.config/startship.toml
export STARSHIP_CONFIG="$XDG_CONFIG_HOME/starship/config.toml"
