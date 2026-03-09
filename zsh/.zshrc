# history
HISTFILE="$XDG_STATE_HOME/zsh/history"
HISTSIZE=10000
SAVEHIST=10000
setopt HIST_IGNORE_DUPS   # skip consecutive duplicates
setopt HIST_IGNORE_SPACE  # skip commands starting with space
setopt SHARE_HISTORY      # share history across sessions
setopt HIST_REDUCE_BLANKS # strip extra whitespace

# gnupg
export GPG_TTY=$(tty)

# plugins
local _plugins="$XDG_DATA_HOME/zsh/plugins"
local _stamp="$XDG_CACHE_HOME/zsh/plugins-updated"
local _repos=(
    "https://github.com/zsh-users/zsh-completions"
    "https://github.com/zsh-users/zsh-autosuggestions"
)
local _needs_update=0

if [[ ! -f "$_stamp" ]] || [[ -n $_stamp(#qN.mh+168) ]]; then
    mkdir -p "${_stamp:h}"
    touch "$_stamp"
    _needs_update=1
fi

for _repo in $_repos; do
    if [[ ! -d "$_plugins/${_repo:t}" ]]; then
        git clone "$_repo" "$_plugins/${_repo:t}"
    elif (( _needs_update )); then
        git -C "$_plugins/${_repo:t}" pull --quiet &
    fi
done
(( _needs_update )) && wait

fpath=("$_plugins/zsh-completions/src" $fpath)
ZSH_AUTOSUGGEST_HIGHLIGHT_STYLE="fg=#ffffff,bg=cyan,bold,underline"
source "$_plugins/zsh-autosuggestions/zsh-autosuggestions.zsh"

# shell options
unsetopt autocd             # don't cd into directories by name
setopt NO_BEEP              # no terminal bell
setopt AUTO_PUSHD           # cd pushes to directory stack
setopt PUSHD_IGNORE_DUPS    # no duplicates in directory stack
setopt EXTENDED_GLOB        # enable extended glob operators (#, ~, ^)

# ggman
eval "$(ggman shellrc)"

# custom functions and aliases
source "$ZDOTDIR/aliases.zsh"
source "$ZDOTDIR/scripts.zsh"

# completion
fpath=("$XDG_DATA_HOME/zsh/completions" $fpath)
autoload -Uz compinit
# only regenerate dump once per day
local _zcompdump="$XDG_CACHE_HOME/zsh/zcompdump-$ZSH_VERSION"
if [[ -n $_zcompdump(#qN.mh+24) ]]; then
    compinit -d "$_zcompdump"
else
    compinit -C -d "$_zcompdump"
fi
zstyle ':completion:*' cache-path "$XDG_CACHE_HOME/zsh/zcompcache"
zstyle ':completion:*' menu select
zstyle ':completion:*' matcher-list 'm:{a-z}={A-Z}'

eval "$(starship init zsh)"
eval "$(direnv hook zsh)"
