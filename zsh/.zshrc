# shell options
bindkey -e                  # emacs line editing
unsetopt autocd             # don't cd into directories by name
setopt NO_BEEP              # no terminal bell
setopt AUTO_PUSHD           # cd pushes to directory stack
setopt PUSHD_IGNORE_DUPS    # no duplicates in directory stack
setopt EXTENDED_GLOB        # enable extended glob operators (#, ~, ^)

# history
HISTFILE="$XDG_STATE_HOME/zsh/history"
mkdir -p "${HISTFILE:h}"
HISTSIZE=10000
SAVEHIST=10000
setopt HIST_IGNORE_DUPS   # skip consecutive duplicates
setopt HIST_IGNORE_SPACE  # skip commands starting with space
setopt SHARE_HISTORY      # share history across sessions
setopt HIST_REDUCE_BLANKS # strip extra whitespace

# -- plugins --
# auto-cloned on first launch, auto-updated weekly in background
PLUGIN_DIR="$XDG_DATA_HOME/zsh/plugins"
_plugin_stamp="$XDG_CACHE_HOME/zsh/plugins-updated"
_plugin_needs_update=0

# check if a week (168h) has passed since last update
if [[ ! -f "$_plugin_stamp" ]] || [[ -n $_plugin_stamp(#qN.mh+168) ]]; then
    mkdir -p "${_plugin_stamp:h}"
    touch "$_plugin_stamp"
    _plugin_needs_update=1
fi

function ensure_plugin() {
    local repo=$1 dir="$PLUGIN_DIR/${1##*/}"
    # clone if missing, pull if update is due
    if [[ ! -d "$dir" ]]; then
        git clone --depth=1 "https://github.com/$repo.git" "$dir"
    elif (( _plugin_needs_update )); then
        git -C "$dir" pull --quiet &
    fi
    fpath=("$dir" $fpath)
    source "$dir/${dir##*/}.plugin.zsh" 2>/dev/null
}

ensure_plugin zsh-users/zsh-completions
ensure_plugin zsh-users/zsh-autosuggestions
ensure_plugin romkatv/zsh-no-ps2
(( _plugin_needs_update )) && wait
ZSH_AUTOSUGGEST_HIGHLIGHT_STYLE="fg=#ffffff,bg=cyan,bold,underline"

# line editing widgets
autoload -Uz up-line-or-beginning-search down-line-or-beginning-search bracketed-paste-magic
zle -N up-line-or-beginning-search
zle -N down-line-or-beginning-search
zle -N bracketed-paste bracketed-paste-magic
# only use builtin widgets during paste to avoid autosuggestions conflict
zstyle ':bracketed-paste-magic' active-widgets '.self-*'

# terminal application mode for correct terminfo sequences
if (( ${+terminfo[smkx]} && ${+terminfo[rmkx]} )); then
    autoload -Uz add-zle-hook-widget
    function zle_application_mode_start { echoti smkx }
    function zle_application_mode_stop { echoti rmkx }
    add-zle-hook-widget -Uz zle-line-init zle_application_mode_start
    add-zle-hook-widget -Uz zle-line-finish zle_application_mode_stop
fi

# key bindings
[[ -n "${terminfo[kcuu1]}" ]] && bindkey -- "${terminfo[kcuu1]}" up-line-or-beginning-search
[[ -n "${terminfo[kcud1]}" ]] && bindkey -- "${terminfo[kcud1]}" down-line-or-beginning-search
[[ -n "${terminfo[khome]}" ]] && bindkey -- "${terminfo[khome]}" beginning-of-line
[[ -n "${terminfo[kend]}" ]]  && bindkey -- "${terminfo[kend]}"  end-of-line
[[ -n "${terminfo[kdch1]}" ]] && bindkey -- "${terminfo[kdch1]}" delete-char
[[ -n "${terminfo[kcbt]}" ]]  && bindkey -- "${terminfo[kcbt]}"  reverse-menu-complete
bindkey -- '^[[1;5C' forward-word        # ctrl+right
bindkey -- '^[[1;5D' backward-word       # ctrl+left

# aliases and functions
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

# tool hooks
eval "$(ggman shellrc)"
eval "$(starship init zsh)"
eval "$(direnv hook zsh)"

# gnupg
export GPG_TTY=$(tty)
