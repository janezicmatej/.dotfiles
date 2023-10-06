# zsh history file 
export HISTFILE="$XDG_STATE_HOME/zsh/history"
export HISTSIZE=100

# Enable Powerlevel10k instant prompt. Should stay close to the top of ~/.config/zsh/.zshrc.
# Initialization code that may require console input (password prompts, [y/n]
# confirmations, etc.) must go above this block; everything else may go below.
if [[ -r "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh" ]]; then
  source "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh"
fi

# pre plugin load
export NVM_COMPLETION=true

# load antigen
typeset -a ANTIGEN_CHECK_FILES=(${ZDOTDIR:-~}/.zshrc ${ZDOTDIR:-~}/antigen.zsh)
source $ZDOTDIR/antigen.zsh

# oh-my-zsh library and git plugin
antigen use oh-my-zsh
antigen bundle git

# zsh users plugin
antigen bundle zsh-users/zsh-autosuggestions

# other
antigen bundle lukechilds/zsh-nvm

# theme
antigen theme romkatv/powerlevel10k

# apply plugin load
antigen apply

# pyenv
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"

# ggman
eval "$(ggman shellrc)"

# gpg
export GPG_TTY=$(tty)

# custom functions and aliases
source "$ZDOTDIR/aliases.zsh"
source "$ZDOTDIR/scripts.zsh"

# completion
fpath=($ZDOTDIR/completions $fpath)
autoload -Uz compinit
compinit -d $XDG_CACHE_HOME/zsh/zcompdump-$ZSH_VERSION
zstyle ':completion:*' cache-path $XDG_CACHE_HOME/zsh/zcompcache

# opam configuration
# [[ ! -r /Users/janezicmatej/.opam/opam-init/init.zsh ]] || source /Users/janezicmatej/.opam/opam-init/init.zsh  > /dev/null 2> /dev/null

# To customize prompt, run `p10k configure` or edit ~/.config/zsh/.p10k.zsh.
[[ ! -f ~/.config/zsh/.p10k.zsh ]] || source ~/.config/zsh/.p10k.zsh
