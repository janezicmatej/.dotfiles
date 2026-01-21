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

if [[ "$OSTYPE" == "darwin"* ]]; then
    antidote load ${ZDOTDIR:-~}/.zsh_plugins_darwin.txt
fi

unsetopt autocd

if [[ "$OSTYPE" == "darwin"* ]]; then
    eval "$(pyenv init - zsh)"
    eval "$(pyenv virtualenv-init - zsh)"
fi

if [[ "$OSTYPE" == "darwin"* ]]; then
    export SSH_AUTH_SOCK=$(gpgconf --list-dirs agent-ssh-socket)
fi

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

# opam configuration
# [[ ! -r /Users/janezicmatej/.opam/opam-init/init.zsh ]] || source /Users/janezicmatej/.opam/opam-init/init.zsh  > /dev/null 2> /dev/null

eval "$(starship init zsh)"
