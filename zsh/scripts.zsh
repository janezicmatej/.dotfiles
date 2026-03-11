# git helpers for aliases
function git_current_branch {
    command git rev-parse --abbrev-ref HEAD 2>/dev/null
}

function git_main_branch {
    command git rev-parse --git-dir &>/dev/null || return
    local ref
    for ref in refs/{heads,remotes/{origin,upstream}}/{main,master,trunk}; do
        if command git show-ref -q --verify "$ref"; then
            echo ${ref:t}
            return 0
        fi
    done
    echo main
}

function tmux_attach {
    local tmux_running
    tmux_running=$(pgrep tmux)

    if [[ -n ${TMUX} ]]; then
        echo "already attached; refreshing env"
        source <(tmux show-environment | sed -n 's/^\(.*\)=\(.*\)$/export \1="\2"/p')
        return 0
    fi

    if [[ -z $tmux_running ]]; then
        ~/.config/tmux/scripts/tmux-sessionizer ~
    else
        tmux a
    fi
}
