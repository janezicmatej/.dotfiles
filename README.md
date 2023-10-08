# .dotfiles

## Alacritty

Install [alacritty](https://github.com/alacritty/alacritty) and `JetBrainsMono` font from [nerd-fonts](https://github.com/ryanoasis/nerd-fonts)

## ZSH 

Install [zsh](https://www.zsh.org/).

### $ZDOTDIR

To change the location of zsh config files run one of these

```sh
# for linux
echo 'export ZDOTDIR="$HOME/.config/zsh"' > /etc/zsh/zshenv 
# for macos
echo 'export ZDOTDIR="$HOME/.config/zsh"' > /etc/zshenv 
```

### Antigen

Install [antigen](https://github.com/zsh-users/antigen)

```sh
curl -L git.io/antigen > antigen.zsh
# or use git.io/antigen-nightly for the latest version
```

## Go

Install [go](https://go.dev/) as it is required for building `ggman`

## ggman

Create `$HOME/git` directory (`$GGROOT` is set to here) and install [ggman](https://github.com/tkw1536/ggman)

```sh
git clone https://github.com/tkw1536/ggman $HOME/git/ggman
cd $HOME/git/ggman
make
make install
```

## pyenv

Install [pyenv](https://github.com/pyenv/pyenv) to `$XDG_DATA_HOME/.pyenv` (this is already taken care for in `.zshenv`) using [pyenv-installer](https://github.com/pyenv/pyenv-installer) and install [build-dependencies](https://github.com/pyenv/pyenv/wiki#suggested-build-environment)

### pyenv-default-packages
Install [pyenv-default-packages](https://github.com/jawshooah/pyenv-default-packages.git) as pyenv plugin and symlink `.pyenv/default-packages` to `$PYENV_ROOT`

```sh
git clone https://github.com/jawshooah/pyenv-default-packages.git $(pyenv root)/plugins/pyenv-default-packages
ln -s "$XDG_CONFIG_HOME/.pyenv/default-packages" "$(pyenv root)/default-packages"
```

## neovim
Install [neovim](https://neovim.io/) and follow `README.md` in [git.janezic.dev/janezicmatej/nvim](https://git.janezic.dev/janezicmatej/nvim/)

## tmux
Install [tmux](https://github.com/tmux/tmux) and [`fzf`](https://github.com/junegunn/fzf) for `tmux-sessionizer`
