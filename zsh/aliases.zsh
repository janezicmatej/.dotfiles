alias z="exec zsh"
alias t="tmux a || ~/.config/tmux/tmux-sessionizer ~"
alias n=nvim_ve
# alias vim=nvim_ve
alias s="ssh-menu"

# navigation
alias cdgit="cd $GGROOT"
alias icloud="cd $HOME/Library/Mobile\ Documents/com\~apple\~CloudDocs"
alias temp="cd $HOME/Desktop/temp"

# apple specific
alias accenton="defaults write -g ApplePressAndHoldEnabled -bool true"
alias accentoff="defaults write -g ApplePressAndHoldEnabled -bool false"

# git
alias gros="git reset origin/$(git_current_branch) --soft"
alias gcan="git commit -v --amend --no-edit"

# unsorted
alias ci="glab ci list"
alias bm=batman
alias grow="~/.local/bin/cbonsai -liWC -M 15 -t 2 -w 60 -s $(date +%s)"
alias clean_ds_store='find . -name ".DS_Store" -type f -delete -print'

# ruff
alias ruffme="ruff format && ruff check --fix"

# clipboard
alias xcp="xclip -selection c"
