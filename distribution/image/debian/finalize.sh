#!/bin/sh
# Run as root in the newly built guest before exporting the development disk.
set -eu
test -f /var/lib/nordos/image-ready
test -f /etc/cloud/cloud-init.disabled
if mountpoint -q /mnt/nordos-build; then
    umount /mnt/nordos-build
fi
# The seed supplied the build key and temporary passwordless sudo.
rm -f /home/nordos/.ssh/authorized_keys /etc/sudoers.d/90-cloud-init-users
systemctl disable ssh.service ssh.socket
cloud-init clean --logs
systemctl poweroff
