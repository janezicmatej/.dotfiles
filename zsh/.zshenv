# default configuration as per https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html
export XDG_CONFIG_HOME="$HOME/.config"
export XDG_CACHE_HOME="$HOME/.cache"
export XDG_DATA_HOME="$HOME/.local/share"
export XDG_STATE_HOME="$HOME/.local/state"

# brew sbin
export PATH="/opt/homebrew/sbin:$PATH"

# brew lib
export LIBRARY_PATH="$LIBRARY_PATH:/opt/homebrew/lib"

# cargo 
source "$HOME/.cargo/env"

# language environment
export LANG=en_US.UTF-8

# editor
export EDITOR=nvim

# go
export GOHOME="$XDG_DATA_HOME/go"
export GOMODCACHE="$XDG_CACHE_HOME/go/mod"
export PATH="$GOHOME/bin:$PATH"

# ggman
export GGROOT="$HOME/git"

# neovim
export PATH="$XDG_DATA_HOME/neovim/bin:$PATH"

# pyenv
export PYENV_ROOT="$XDG_DATA_HOME/.pyenv"
command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"

# poetry
export POETRY_HOME="$XDG_DATA_HOME/poetry"
command -v poetry >/dev/null || export PATH="$POETRY_HOME/bin:$PATH"
