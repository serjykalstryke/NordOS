#!/bin/sh
# Run as root inside the Debian-based NordOS guest.
set -eu
umask 022

exchange=${1:-/mnt/nordos-exchange}
source_root=/usr/src/nordos

if [ "$(id -u)" -ne 0 ]; then
    echo "Run this script as root inside the NordOS guest." >&2
    exit 1
fi

install -d /usr/src
staging=$(mktemp -d /usr/src/.nordos-development.XXXXXX)
trap 'rm -rf -- "$staging"' EXIT
tar --no-same-owner --no-same-permissions -xzf "$exchange/nordos-source.tar.gz" -C "$staging"
tar --no-same-owner --no-same-permissions -xzf "$exchange/nordos-sdk.tar.gz" -C "$staging"
test -f "$staging/nordos/CMakeLists.txt"
test -f "$staging/sdk/usr/lib/cmake/CutefishClients/CutefishClientsConfig.cmake"
test -f "$staging/sdk/usr/include/cutefish/display/display_client.h"

if [ -e "$source_root" ] || [ -L "$source_root" ]; then
    if [ -L "$source_root" ] || ! diff -qr "$source_root" "$staging/nordos"; then
        echo "$source_root already contains a different source snapshot." >&2
        exit 1
    fi
fi

export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y --no-install-recommends \
    build-essential cmake git pkgconf python3 gettext libgtest-dev dbus-daemon \
    libwayland-bin libwayland-dev wayland-protocols \
    libavcodec-dev libavformat-dev libavutil-dev libswscale-dev \
    libva-dev libdrm-dev libgbm-dev libsystemd-dev libfontconfig-dev libicu-dev \
    libpipewire-0.3-dev libspa-0.2-dev

version=$(dpkg-query -W -f='${Version}' nordos-foundation)
install -d "$staging/sdk/DEBIAN"
cat > "$staging/sdk/DEBIAN/control" <<EOF
Package: nordos-foundation-sdk
Version: $version
Architecture: amd64
Maintainer: NordOS developers <noreply@example.invalid>
Depends: nordos-foundation (= $version)
Description: NordOS development framework headers and CMake exports
EOF
dpkg-deb --root-owner-group --build "$staging/sdk" "$staging/nordos-foundation-sdk.deb"
dpkg -i "$staging/nordos-foundation-sdk.deb"
if [ ! -e "$source_root" ]; then
    mv -T "$staging/nordos" "$source_root"
fi
