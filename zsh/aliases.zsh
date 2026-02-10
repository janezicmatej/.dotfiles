alias z="exec zsh"
alias t=tmux_attach

if [[ "$OSTYPE" == "darwin"* ]]; then
        alias n=nvim_ve
        alias vim=nvim_ve
elif [[ "$OSTYPE" == "linux"* ]]; then
        alias n=nvim
fi

alias s="ssh-menu"

# docker
alias dp="docker ps --format 'table {{.Names}}\t{{.Ports}}'"
alias dcp="docker compose ps --format 'table {{.Name}}\t{{.Ports}}'"

# navigation
alias cdgit="cd $GGROOT"
alias icloud="cd $HOME/Library/Mobile\ Documents/com\~apple\~CloudDocs"
alias temp="cd $HOME/Desktop/temp"

# apple specific
alias accenton="defaults write -g ApplePressAndHoldEnabled -bool true"
alias accentoff="defaults write -g ApplePressAndHoldEnabled -bool false"

# git
alias gpo="git push origin"
alias gros="git reset origin/$(git_current_branch) --soft"
alias gcan="git commit -v --amend --no-edit"
alias glogaa="git log --oneline --graph --all --pretty=format:\"%C(auto)%h %C(blue)(%aL/%cL)%C(auto)%(decorate) %s%Creset\""

# unsorted
alias ci="glab ci list"
alias bm=batman
alias grow="~/.local/bin/cbonsai -liWC -M 15 -t 2 -w 60 -s $(date +%s)"
alias clean_ds_store='find . -name ".DS_Store" -type f -delete -print'

# ruff
alias ruffme="ruff check --fix && ruff format"

# clipboard
alias xcp="xclip -selection c"
