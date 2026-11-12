#!/bin/sh
# Run in a disposable NordOS builder VM.
set -eu
export DEBIAN_FRONTEND=noninteractive
for sources in /etc/apt/sources.list.d/*.sources; do
    [ -f "$sources" ] || continue
    sed -i 's/^Components: main$/Components: main non-free-firmware/' "$sources"
done
apt-get update
apt-get install -y --no-install-recommends \
    linux-image-amd64 live-boot live-config live-config-systemd \
    calamares calamares-settings-debian qt6-wayland squashfs-tools \
    grub-pc-bin grub-efi-amd64-bin grub2-common efibootmgr dosfstools e2fsprogs \
    cryptsetup-initramfs keyutils ntfs-3g os-prober \
    wpasupplicant wireless-regdb firmware-iwlwifi firmware-realtek \
    firmware-intel-graphics firmware-intel-misc firmware-intel-sound \
    firmware-sof-signed firmware-nvidia-graphics intel-microcode
