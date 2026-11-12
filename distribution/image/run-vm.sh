#!/bin/bash
set -euo pipefail

if [[ $# -ne 1 || ! -f $1 ]]; then
    printf 'Usage: %s path-to-nordos.qcow2\n' "$0" >&2
    exit 2
fi

disk=$(realpath -- "$1")
# QEMU doubles literal commas in the value of a drive option.
disk=${disk//,/,,}
if [[ -r /dev/kvm && -w /dev/kvm ]]; then
    acceleration=(-accel kvm -cpu host)
else
    acceleration=(-accel tcg -cpu max)
fi

qemu=${QEMU_BIN:-qemu-system-x86_64}
firmware=()
if [[ -n ${NORDOS_QEMU_ROOT:-} ]]; then
    qemu="$NORDOS_QEMU_ROOT/usr/bin/qemu-system-x86_64"
    libdir="$NORDOS_QEMU_ROOT/usr/lib/x86_64-linux-gnu"
    export LD_LIBRARY_PATH="$libdir${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
    export QEMU_MODULE_DIR="$libdir/qemu"
    firmware=(-L "$NORDOS_QEMU_ROOT/usr/share/qemu" -L "$NORDOS_QEMU_ROOT/usr/share/seabios"
              -bios "$NORDOS_QEMU_ROOT/usr/share/seabios/bios.bin")
fi

exec "$qemu" -machine q35 "${acceleration[@]}" "${firmware[@]}" \
    -smp 4 -m 4G -vga virtio -display "${NORDOS_VM_DISPLAY:-gtk,gl=off}" \
    -netdev user,id=network -device virtio-net-pci,netdev=network,romfile= \
    -drive "file=$disk,format=qcow2,if=virtio"
