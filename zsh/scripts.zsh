function tmux_attach {
    local tmux_running
    tmux_running=$(pgrep tmux)

    if [[ -n ${TMUX} ]]; then
        echo "already attached; refreshing env"
        source <(tmux show-environment | sed -n 's/^\(.*\)=\(.*\)$/export \1="\2"/p')
        return 0
    fi

    if [[ -z $tmux_running ]]; then
        ~/.config/tmux/tmux-sessionizer ~
    else
        tmux a
    fi
}
