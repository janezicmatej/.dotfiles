alias z="exec zsh"
alias t=tmux_attach

alias n=nvim

alias s="ssh-menu"

# docker
alias dp="docker ps --format 'table {{.Names}}\t{{.Ports}}'"
alias dcp="docker compose ps --format 'table {{.Name}}\t{{.Ports}}'"

# navigation
alias cdgit='cd $GGROOT'

# git status/diff
alias gst="git status"
alias gd="git diff"
alias gds="git diff --staged"
alias gdup="git diff @{upstream}"
alias glog="git log --oneline --decorate --graph"
alias gloga="git log --oneline --decorate --graph --all"
alias glogaa="git log --oneline --graph --all --pretty=format:\"%C(auto)%h %C(blue)(%aL/%cL)%C(auto)%(decorate) %s%Creset\""

# git staging/commit
alias ga="git add"
alias gc="git commit -v"
alias gc!="git commit -v --amend"
alias gcan="git commit -v --amend --no-edit"
alias gcan!="git commit -v --all --no-edit --amend"
alias grs="git restore"

# git branch/checkout
alias gb="git branch"
alias gco="git checkout"
alias gcm='git checkout $(git_main_branch)'
alias gsw="git switch"

# git fetch/pull/push
alias gfa="git fetch --all --prune"
alias gl="git pull"
alias gp="git push"
alias gpf="git push --force-with-lease"
alias gpf!="git push --force"
alias gpo="git push origin"

# git rebase
alias grb="git rebase"
alias grba="git rebase --abort"
alias grbc="git rebase --continue"
alias grbi="git rebase -i"
grbm() { git rebase "$(git_main_branch)" }

# git merge
alias gm="git merge"
alias gma="git merge --abort"
alias gmc="git merge --continue"

# git cherry-pick
alias gcp="git cherry-pick"
alias gcpa="git cherry-pick --abort"
alias gcpc="git cherry-pick --continue"

# git stash/reset
alias gstp="git stash pop"
gros() { git reset "origin/$(git_current_branch)" --soft }

# ruff
alias ruffme="ruff check --fix && ruff format"
