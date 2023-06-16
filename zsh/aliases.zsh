alias z="exec zsh"
alias t="tmux a || tmux new-session -s janezicmatej -c ~"
alias n=nvim_ve
alias vim=nvim_ve

# navigation
alias cdgit="cd $GGROOT"
alias icloud="cd $HOME/Library/Mobile\ Documents/com\~apple\~CloudDocs"
alias temp="cd $HOME/Desktop/temp"

# apple specific
alias accenton="defaults write -g ApplePressAndHoldEnabled -bool true"
alias accentoff="defaults write -g ApplePressAndHoldEnabled -bool false"

# docker
alias dps="docker ps --format table'{{ .ID }}\t{{ .Image }}\t{{ .Ports}}\t{{ .Names }}'"

alias gros="git reset origin/$(git_current_branch) --soft"

# unsorted
alias ci="glab ci list"
alias bm=batman
alias grow="~/.local/bin/cbonsai -liWC -M 15 -t 2 -w 60 -s $(date +%s)"
alias clean_ds_store='find . -name ".DS_Store" -type f -delete -print'
