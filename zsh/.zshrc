# shell options
bindkey -e                  # emacs line editing
unsetopt autocd             # don't cd into directories by name
setopt NO_BEEP              # no terminal bell
setopt AUTO_PUSHD           # cd pushes to directory stack
setopt PUSHD_IGNORE_DUPS    # no duplicates in directory stack
setopt EXTENDED_GLOB        # enable extended glob operators (#, ~, ^)

# history
HISTFILE="$XDG_STATE_HOME/zsh/history"
HISTSIZE=10000
SAVEHIST=10000
setopt HIST_IGNORE_DUPS   # skip consecutive duplicates
setopt HIST_IGNORE_SPACE  # skip commands starting with space
setopt SHARE_HISTORY      # share history across sessions
setopt HIST_REDUCE_BLANKS # strip extra whitespace

# plugins
local _plugins="$XDG_DATA_HOME/zsh/plugins"
local _stamp="$XDG_CACHE_HOME/zsh/plugins-updated"
local _repos=(
    "https://github.com/zsh-users/zsh-completions"
    "https://github.com/zsh-users/zsh-autosuggestions"
    "https://github.com/romkatv/zsh-no-ps2"
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
source "$_plugins/zsh-no-ps2/zsh-no-ps2.plugin.zsh"

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
