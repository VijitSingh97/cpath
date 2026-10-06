#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
version=$(cat VERSION)
package=$(mktemp -d)
trap 'rm -rf "$package"' EXIT
make install DESTDIR="$package" PREFIX=/usr ZSH_COMPLETION_DIR=/usr/share/zsh/vendor-completions
install -d "$package/DEBIAN" "$package/usr/share/doc/cpath"
install -m 644 LICENSE "$package/usr/share/doc/cpath/copyright"
cat > "$package/DEBIAN/control" <<CONTROL
Package: cpath
Version: $version
Section: utils
Priority: optional
Architecture: all
Maintainer: Vijit Singh <VijitSingh97@users.noreply.github.com>
Depends: coreutils
Recommends: wl-clipboard, xclip
Homepage: https://github.com/VijitSingh97/cpath
Description: Copy a file's absolute path to the desktop clipboard
 A small shell command for Wayland and X11 desktop sessions.
 Includes zsh filename completion; bash completes filenames by default.
CONTROL
mkdir -p dist
dpkg-deb --root-owner-group --build "$package" "dist/cpath_${version}_all.deb"
