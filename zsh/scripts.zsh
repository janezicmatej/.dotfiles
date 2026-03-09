function tmux_attach {
    tmux_running=$(pgrep tmux)

    if ! [[ -z ${TMUX} ]]; then
        echo "already attached; refreshing env"
        source <(tmux show-environment | sed -n 's/^\(.*\)=\(.*\)$/export \1="\2"/p')
        return 1
    fi

    if [[ -z $tmux_running ]]; then
        ~/.config/tmux/tmux-sessionizer ~
    else
        tmux a
    fi
}
