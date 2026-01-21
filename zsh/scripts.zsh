function nvim_ve {
    if [[ -e $VIRTUAL_ENV && -f "$VIRTUAL_ENV/bin/activate" ]]; then
        source "$VIRTUAL_ENV/bin/activate"
        command nvim $@
        deactivate
    else
        command nvim $@
    fi
}

alias nvim=nvim_ve

function afm {
    RES=$(curl -s "https://$1/api/monitoring/requirements")
    COUNT=$(echo "$RES" | grep -c $2)
    if [[ $COUNT -ge 0 ]]; then
        VER=$(echo "$RES" | jq '.[] | select(.name | contains("'"$2"'")).version')
        # OP=$(echo "$RES" | jq '.[] | select(.name | contains("'"$2"'")).requirement?[0][0]')
        # echo "$2""$(echo "$OP" | tr -d '"')""$(echo "$VER" | tr -d '"')"
        echo "${2}==$(echo "$VER" | tr -d '"')"
    fi
}

function nukepip {
    pip uninstall $(pip freeze) -y
    pip install -r $(pyenv root)/default-packages
}

function pyinit {
    if [[ -f .python-version ]]; then
        echo "found .python-version, stopping"
        return
    fi

    DIRNAME=$(basename "$PWD")

    if [[ $(pyenv versions | grep -E "/${DIRNAME}$") ]]; then
        echo "found existing version with this name, setting..."
        pyenv local "$DIRNAME"
        return
    fi

    if [[ -z $1 ]]; then
        echo "no python version provided, defaulting to $(pyenv version-name)"
        VERSION=$(pyenv version-name)
    else
        VERSION=$1
    fi

    pyenv virtualenv "$VERSION" "$DIRNAME"
    pyenv local "$DIRNAME"

}

function lh {
    if [[ -z $1 ]]; then
        PORT=7999
    else
        PORT=$1
    fi

    open "http://localhost:$PORT"
}

function dps {
    if [[ -z $1 ]]; then
        docker ps --format table'{{ .ID }}\t{{ .Image }}\t{{ .Ports}}\t{{ .Names }}'
    else
        docker ps --format table'{{ .ID }}\t{{ .Image }}\t{{ .Ports}}\t{{ .Names }}' | grep $1
    fi
}

function tssh {
    if [[ -z $1 ]]; then
        echo "provide ssh host"
        return
    fi

    ssh -t "$@" "command -v tmux && (tmux a || tmux new-session -s gorazd -c ~) || bash"
}


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
