#!/bin/sh
# Requires apt-utils, GnuPG, and the repository signing key in GNUPGHOME.
set -eu
cd "$(dirname "$0")/.."
version=$(cat VERSION)
mkdir -p public
cp "dist/cpath_${version}_all.deb" public/
cd public
gpg --batch --armor --export > cpath.asc
apt-ftparchive packages . > Packages
gzip -n -k -f Packages
apt-ftparchive -o APT::FTPArchive::Release::Origin=cpath \
    -o APT::FTPArchive::Release::Label=cpath \
    -o 'APT::FTPArchive::Release::Architectures=amd64 arm64 armhf all' \
    release . > Release
gpg --batch --yes --armor --detach-sign --output Release.gpg Release
gpg --batch --yes --clearsign --output InRelease Release
