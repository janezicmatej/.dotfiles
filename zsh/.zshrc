# zsh history file 
export HISTFILE="$XDG_STATE_HOME/zsh/history"
export HISTSIZE=100

## pre plugin load
# nvm
export NVM_COMPLETION=true
# zsh autosugestions
export ZSH_AUTOSUGGEST_HIGHLIGHT_STYLE="fg=#ffffff,bg=cyan,bold,underline"

# source antidote
source $ZDOTDIR/.antidote/antidote.zsh
antidote load

unsetopt autocd

# ggman
eval "$(ggman shellrc)"

# custom functions and aliases
source "$ZDOTDIR/aliases.zsh"
source "$ZDOTDIR/scripts.zsh"

# completion
fpath=($ZDOTDIR/completions $fpath)
autoload -Uz compinit
compinit -d $XDG_CACHE_HOME/zsh/zcompdump-$ZSH_VERSION
zstyle ':completion:*' cache-path $XDG_CACHE_HOME/zsh/zcompcache

eval "$(starship init zsh)"
eval "$(direnv hook zsh)"
