# composable nix devshell from matej.nix
# usage in .envrc: use dev uv_14 pg_18
use_dev() {
  for component in "$@"; do
    use flake "dev#${component}"
  done
}
