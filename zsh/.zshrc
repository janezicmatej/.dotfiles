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

# completion
fpath=($ZDOTDIR/completions $fpath)
autoload -Uz compinit
compinit -d $XDG_CACHE_HOME/zsh/zcompdump-$ZSH_VERSION
zstyle ':completion:*' cache-path $XDG_CACHE_HOME/zsh/zcompcache

# zsh history file 
export HISTFILE="$XDG_STATE_HOME/zsh/history"

# pre plugin load
export NVM_COMPLETION=true
export NVM_AUTO_USE=true

# load antigen
typeset -a ANTIGEN_CHECK_FILES=(${ZDOTDIR:-~}/.zshrc ${ZDOTDIR:-~}/antigen.zsh)
source $ZDOTDIR/antigen.zsh

# oh-my-zsh library and git plugin
antigen use oh-my-zsh
antigen bundle git

# zsh users plugin
antigen bundle zsh-users/zsh-syntax-highlighting
antigen bundle zsh-users/zsh-autosuggestions
antigen bundle zsh-users/zsh-completions

# other
antigen bundle lukechilds/zsh-nvm

# theme
antigen theme romkatv/powerlevel10k

# apply plugin load
antigen apply

# # language environment
export LANG=en_US.UTF-8

# brew sbin
export PATH="/opt/homebrew/sbin:$PATH"

# pyenv
export PYENV_ROOT="$XDG_DATA_HOME/.pyenv"
command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"

# poetry
export POETRY_HOME="$XDG_DATA_HOME/poetry"
export PATH="/Users/janezicmatej/.local/share/poetry/bin:$PATH"

# neovim
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
source "$ZDOTDIR/scripts.zsh"

# opam configuration
[[ ! -r /Users/janezicmatej/.opam/opam-init/init.zsh ]] || source /Users/janezicmatej/.opam/opam-init/init.zsh  > /dev/null 2> /dev/null

# To customize prompt, run `p10k configure` or edit ~/.config/zsh/.p10k.zsh.
[[ ! -f ~/.config/zsh/.p10k.zsh ]] || source ~/.config/zsh/.p10k.zsh
