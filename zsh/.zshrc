# default configuration as per https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html
export XDG_CONFIG_HOME="$HOME/.config"
export XDG_CACHE_HOME="$HOME/.cache"
export XDG_DATA_HOME="$HOME/.local/share"
export XDG_STATE_HOME="$HOME/.local/state"

# Enable Powerlevel10k instant prompt. Should stay close to the top of ~/.config/zsh/.zshrc.
# Initialization code that may require console input (password prompts, [y/n]
# confirmations, etc.) must go above this block; everything else may go below.
if [[ -r "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh" ]]; then
  source "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh"
fi

# zsh history file 
export HISTFILE="$XDG_STATE_HOME/zsh/history"

# Path to your oh-my-zsh installation.
export ZSH="$HOME/.oh-my-zsh"

# Set name of the theme to load
ZSH_THEME="powerlevel10k/powerlevel10k"

# just remind me to update when it's time
zstyle ':omz:update' mode reminder  
zstyle ':omz:update' frequency 7

# pre plugin load
export NVM_COMPLETION=true
export NVM_AUTO_USE=true
# i don't lazy load nvm because neovim doesn't work well with it

# plugins
plugins=(zsh-nvm git zsh-autosuggestions zsh-syntax-highlighting)

# TODO: lose oh my zsh at some point

# oh my zsh
source $ZSH/oh-my-zsh.sh

# language environment
export LANG=en_US.UTF-8

# brew sbin
export PATH="/opt/homebrew/sbin:$PATH"

# pyenv
export PYENV_ROOT="$XDG_DATA_HOME/.pyenv"
command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"

# # nvim
export PATH="$HOME/neovim/bin:$PATH"

# go
export GOHOME="$XDG_DATA_HOME/go"
export GOMODCACHE="$XDG_CACHE_HOME/go/mod"
export PATH="$PATH:$GOHOME/bin"

# ggman
export GGROOT="$HOME/Desktop/git"
eval "$(ggman shellrc)"

# gpg
export GPG_TTY=$(tty)

# editor
export EDITOR=nvim

# custom functions and aliases
source "$ZDOTDIR/aliases.zsh"
source "$ZDOTDIR/functions.zsh"

# opam configuration
[[ ! -r /Users/janezicmatej/.opam/opam-init/init.zsh ]] || source /Users/janezicmatej/.opam/opam-init/init.zsh  > /dev/null 2> /dev/null

# To customize prompt, run `p10k configure` or edit ~/.config/zsh/.p10k.zsh.
[[ ! -f ~/.config/zsh/.p10k.zsh ]] || source ~/.config/zsh/.p10k.zsh
