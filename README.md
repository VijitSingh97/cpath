# cpath

**Copy a file's absolute path to your clipboard.**

[![CI](https://github.com/VijitSingh97/cpath/actions/workflows/ci.yml/badge.svg)](https://github.com/VijitSingh97/cpath/actions/workflows/ci.yml)
[![Release](https://img.shields.io/github/v/release/VijitSingh97/cpath)](https://github.com/VijitSingh97/cpath/releases)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

```console
$ cpath "project notes.txt"
copied: /home/you/project notes.txt
```

A small POSIX shell command for **macOS, Ubuntu, and Debian**. Works with files,
directories, and symbolic links. Paths with spaces are supported; symbolic links
resolve to their targets. The clipboard contains only the path, with no added
newline.

## Install

### macOS — Homebrew

Add this repository as a tap, then install:

```sh
brew tap vijitsingh97/cpath https://github.com/VijitSingh97/cpath.git
brew install vijitsingh97/cpath/cpath
```

Homebrew installs the command and zsh completion. macOS uses its built-in
`pbcopy` clipboard utility.

### Ubuntu / Debian — APT

Add the signed package repository once:

```sh
sudo apt-get update
sudo apt-get install -y ca-certificates curl
sudo install -d -m 0755 /etc/apt/keyrings
sudo curl -fsSL https://vijitsingh97.github.io/cpath/cpath.asc \
  -o /etc/apt/keyrings/cpath.asc
sudo chmod 0644 /etc/apt/keyrings/cpath.asc

sudo tee /etc/apt/sources.list.d/cpath.sources >/dev/null <<'APT'
Types: deb
URIs: https://vijitsingh97.github.io/cpath/
Suites: ./
Signed-By: /etc/apt/keyrings/cpath.asc
APT

sudo apt-get update
sudo apt-get install cpath
```

This is an APT package feed hosted on GitHub Pages. A Git clone URL cannot be
used as an APT source. The signing key is scoped to this feed with `Signed-By`.
The signing key fingerprint is `0CC3 C39C A957 4C9B 1F52 C2E8 A8EB 1080 B99F F3C0`.
The package recommends `wl-clipboard` and `xclip` for Wayland and X11 support.

Prefer a direct download? Install the `.deb` from the release:

```sh
curl -fL -O https://github.com/VijitSingh97/cpath/releases/download/v0.0.1/cpath_0.0.1_all.deb
sudo apt-get install ./cpath_0.0.1_all.deb
```

### From source

Requires `git`, `make`, and `realpath`. Recent macOS includes `realpath`;
Ubuntu and Debian provide it through `coreutils`.

```sh
git clone https://github.com/VijitSingh97/cpath.git
cd cpath
git checkout v0.0.1
make install PREFIX="$HOME/.local"
```

Ensure `~/.local/bin` is on your PATH. If needed, add this to `~/.zshrc` or
`~/.bashrc`, then start a new terminal:

```sh
export PATH="$HOME/.local/bin:$PATH"
```

On Linux, install a clipboard utility for your desktop:

```sh
sudo apt-get install wl-clipboard xclip
```

## Usage

```sh
cpath filename.txt
cpath "a filename with spaces.txt"
cpath ./some-directory
cpath --help
cpath --version
```

A successful copy prints `copied: /absolute/path`. A missing file prints
`cpath: file doesn't exist: ...`, exits with an error, and leaves the clipboard
unchanged. Clipboard failures also return an error and never print `copied:`.
The command copies a path; it does not copy file contents.

Linux uses `wl-copy` when a Wayland session is available, otherwise `xclip`
(or `xsel`) with the X11 clipboard selection. A graphical session is required;
headless terminals and ordinary SSH sessions have no desktop clipboard.

## Tab completion

### Bash

Bash completes filenames by default. Type `cpath fil` and press **Tab**.
No plugin or completion script is required. If your Bash configuration disables
default filename completion, add `complete -f cpath` to `~/.bashrc`.

### Zsh

Homebrew and the Debian package install `_cpath` in their standard zsh
completion directories. Start a new terminal after installing.

If zsh completion is not configured yet, put the appropriate directory in
`fpath` **before** loading `compinit` in `~/.zshrc`:

```zsh
# Choose the line for your installation:
fpath=("$(brew --prefix)/share/zsh/site-functions" $fpath)  # Homebrew
# fpath=(/usr/share/zsh/vendor-completions $fpath)          # Debian package
# fpath=("$HOME/.local/share/zsh/site-functions" $fpath)    # Source install

autoload -Uz compinit
compinit
```

If you use Oh My Zsh, put the `fpath` line before
`source "$ZSH/oh-my-zsh.sh"`; Oh My Zsh loads `compinit` itself.
For an already-open terminal, filename completion can be enabled immediately:

```zsh
compdef _files cpath
```

## Update or remove

```sh
# Homebrew
brew update
brew upgrade vijitsingh97/cpath/cpath
brew uninstall vijitsingh97/cpath/cpath

# APT
sudo apt-get update
sudo apt-get install --only-upgrade cpath
sudo apt-get remove cpath
```

To remove the APT source as well:

```sh
sudo rm -f /etc/apt/sources.list.d/cpath.sources /etc/apt/keyrings/cpath.asc
sudo apt-get update
```

For a source install, run `make uninstall PREFIX="$HOME/.local"` in the checkout.

## Development and releases

```sh
make test   # Python standard-library tests; clipboard backends are mocked
make lint   # ShellCheck
make deb    # Build dist/cpath_<version>_all.deb on Debian/Ubuntu
```

CI tests macOS, Ubuntu, and Debian, including package layout and zsh completion.
Tests never touch the real clipboard. Desktop clipboard integration still needs
a manual check in a graphical session.

To release, update `VERSION`, the version in `bin/cpath`, and `CHANGELOG.md`;
then push a matching `v<version>` tag. The release workflow builds the Debian
package, publishes GitHub release assets, and deploys the signed APT feed.
Repository administrators must configure GitHub Pages to use GitHub Actions
and provide the ASCII-armored signing key as the `APT_SIGNING_KEY` Actions secret.
Update `Formula/cpath.rb` with the new tag URL and its SHA-256 checksum.

## License

[MIT](LICENSE) © 2026 Vijit Singh.
