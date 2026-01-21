# default configuration as per https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html
export XDG_CONFIG_HOME="$HOME/.config"
export XDG_CACHE_HOME="$HOME/.cache"
export XDG_DATA_HOME="$HOME/.local/share"
export XDG_STATE_HOME="$HOME/.local/state"

# ~/.local/bin
export PATH="$HOME/.local/bin:$PATH"

# brew sbin
export PATH="/opt/homebrew/sbin:$PATH"

# brew lib
export LIBRARY_PATH="$LIBRARY_PATH:/opt/homebrew/lib"

# cargo 
if [[ "$OSTYPE" == "darwin"* ]]; then
        source "$HOME/.cargo/env"
fi

# language environment
export LANG=en_US.UTF-8

# editor
export EDITOR=nvim

# go
export GOPATH="$XDG_DATA_HOME/go"
export GOMODCACHE="$XDG_CACHE_HOME/go/mod"
export PATH="$GOPATH/bin:$PATH"

# ggman
export GGROOT="$HOME/git"

# neovim
export PATH="$XDG_DATA_HOME/neovim/bin:$PATH"

# pyenv
export PYENV_ROOT="$XDG_DATA_HOME/.pyenv"
command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"

# pyenv-virtualenv
# leave python promt to starship
export PYENV_VIRTUALENV_DISABLE_PROMPT=1

# poetry
export POETRY_HOME="$XDG_DATA_HOME/poetry"
command -v poetry >/dev/null || export PATH="$POETRY_HOME/bin:$PATH"

# gnupg
export GPG_TTY=$(tty)

# aflabs
export USER_UID=$(id -u)
export USER_GID=$(id -g)

# name
export NAME="Matej Janežič"

# starship nest config into a folder, default is ~/.config/startship.toml
export STARSHIP_CONFIG="$XDG_CONFIG_HOME/starship/config.toml"
