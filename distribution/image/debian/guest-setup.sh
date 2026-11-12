#!/bin/sh
# Runs only inside the image guest, from its attached build medium.
set -eu
exec > /var/log/nordos-image-build.log 2>&1
export DEBIAN_FRONTEND=noninteractive
mkdir -p /mnt/nordos-build /var/lib/nordos
mountpoint -q /mnt/nordos-build || mount -o ro /dev/disk/by-label/CIDATA /mnt/nordos-build
# Prevent the display manager starting until configuration is complete.
if [ -e /usr/sbin/policy-rc.d ] || [ -L /usr/sbin/policy-rc.d ]; then
    echo "The base image already has a service-start policy" >&2
    exit 1
fi
trap 'rm -f /usr/sbin/policy-rc.d' EXIT
printf '#!/bin/sh\nexit 101\n' > /usr/sbin/policy-rc.d
chmod 755 /usr/sbin/policy-rc.d
apt-get update
apt-get install -y --no-install-recommends /mnt/nordos-build/packages/*.deb \
    dbus-user-session libpam-systemd libnss-systemd polkitd pkexec acl \
    network-manager bluez upower accountsservice udisks2 power-profiles-daemon \
    pipewire-audio wireplumber rtkit xwayland xdg-desktop-portal xdg-user-dirs \
    shared-mime-info desktop-file-utils fonts-inter fonts-noto-core fonts-noto-mono \
    fonts-noto-color-emoji libgl1-mesa-dri libegl-mesa0 libglx-mesa0 xkb-data \
    locales sudo nano git build-essential cmake pkg-config openssh-client xterm \
    qemu-guest-agent systemd-timesyncd fuse3
rm /usr/sbin/policy-rc.d
trap - EXIT
printf 'en_US.UTF-8 UTF-8\n' > /etc/locale.gen
locale-gen
update-locale LANG=en_US.UTF-8
# OS identity is a conffile owned by the foundation package; Debian remains ID_LIKE.
ln -sfn /etc/nordos-release /etc/os-release
cat > /etc/cutefish-dm.conf <<'DM'
[Autologin]
User=nordos
DM
systemctl enable cutefish-dm.service
systemctl set-default graphical.target
systemctl enable NetworkManager.service
# Switch from cloud networking on the next boot, keeping the build connection alive.
rm -f /etc/netplan/50-cloud-init.yaml
systemctl disable systemd-networkd.service systemd-networkd.socket systemd-networkd-wait-online.service
usermod -aG audio,video,render,netdev nordos
install -d -o nordos -g nordos /home/nordos/Desktop /home/nordos/Documents /home/nordos/Downloads
# Development setup can run offline on later boots.
touch /etc/cloud/cloud-init.disabled
apt-mark hold nordos-foundation cutefish-toolkit cutefish-dm
cp /mnt/nordos-build/build-manifest.json /var/lib/nordos/build-manifest.json
dpkg-query -W > /var/lib/nordos/installed-packages.txt
apt-get clean
printf 'NordOS image installation completed\n' > /var/lib/nordos/image-ready
sync
