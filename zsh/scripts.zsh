
function nvim_ve {
  if [[ -e "$VIRTUAL_ENV" && -f "$VIRTUAL_ENV/bin/activate" ]]; then
    source "$VIRTUAL_ENV/bin/activate"
    command nvim $@
    deactivate
  else
    command nvim $@
  fi
}

alias nvim=nvim_ve

function ffb {
  if ! [[ -f package.json ]]; then
    echo "no package.json"
    return
  fi

  if [[ -f yarn.lock ]]; then
    PACKAGE_MANAGER=yarn
  else
    PACKAGE_MANAGER=npm
  fi

  if [[ -n $(grep "react-scripts" package.json) ]]; then
    BROWSER=none FORCE_COLOR=true "$PACKAGE_MANAGER" start | cat
  fi
}

function afm {
  RES=$(curl -s "https://$1/api/monitoring/requirements")
  COUNT=$(echo "$RES" | grep -c $2)
  if [[ $COUNT -ge 0 ]]; then
    VER=$(echo "$RES" | jq '.[] | select(.name | contains("'"$2"'")).version')
    # OP=$(echo "$RES" | jq '.[] | select(.name | contains("'"$2"'")).requirement?[0][0]')
    # echo "$2""$(echo "$OP" | tr -d '"')""$(echo "$VER" | tr -d '"')"
    echo "$2""==""$(echo "$VER" | tr -d '"')"
  fi
}


function nukepip {
  pip uninstall $(pip freeze) -y
  pip install -r $(pyenv root)/default-packages
}
