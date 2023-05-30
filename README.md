# .dotfiles

## setup cheat sheet

1. install [zsh](https://www.zsh.org/)
2. install [oh-my-zsh](https://ohmyz.sh/)
    - install [zsh-nvm](https://github.com/lukechilds/zsh-nvm)
    - install [zsh-autosuggestions](https://github.com/zsh-users/zsh-autosuggestions)
    - install [zsh-syntax-highlighting](https://github.com/zsh-users/zsh-syntax-highlighting)
3. install [go](https://go.dev/)
4. install [ggman](https://github.com/tkw1536/ggman)
5. install [pyenv](https://github.com/pyenv/pyenv) to $XDG_DATA_HOME/.pyenv
    - set `PYENV_ROOT` and use [pyenv-installer](https://github.com/pyenv/pyenv-installer)
    - install [pyenv-default-packages](git clone https://github.com/jawshooah/pyenv-default-packages.git $(pyenv root)/plugins/pyenv-default-packages)
    - symlink `.pyenv/default-packages` to `$PYENV_ROOT/default-packages`
6. install [neovim](https://neovim.io/)
    - follow `README.md` in [janezicmatej/nvim](https://github.com/janezicmatej/nvim/)
