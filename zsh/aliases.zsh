alias z="exec zsh"
alias t=tmux_attach

alias n=nvim

alias s="ssh-menu"

# docker
alias dp="docker ps --format 'table {{.Names}}\t{{.Ports}}'"
alias dcp="docker compose ps --format 'table {{.Name}}\t{{.Ports}}'"

# navigation
alias cdgit="cd $GGROOT"

# git
alias gpo="git push origin"
alias gros="git reset origin/$(git_current_branch) --soft"
alias gcan="git commit -v --amend --no-edit"
alias glogaa="git log --oneline --graph --all --pretty=format:\"%C(auto)%h %C(blue)(%aL/%cL)%C(auto)%(decorate) %s%Creset\""

# ruff
alias ruffme="ruff check --fix && ruff format"
