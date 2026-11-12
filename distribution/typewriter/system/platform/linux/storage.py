from contextlib import contextmanager
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys
import tempfile
import time

from platform_linux.boot import LIVE_MEDIUM, LIVE_ROOT

MIN_DISK_BYTES = 8 * 1024**3


def descendants(device):
    yield device
    for child in device.get("children", []):
        yield from descendants(child)


def install_disks():
    medium = subprocess.check_output(
        ["findmnt", "-nro", "MAJ:MIN", "--mountpoint", str(LIVE_MEDIUM)], text=True
    ).strip()
    if not medium or not Path("/sys/dev/block", medium).exists():
        raise RuntimeError("The installer could not identify its boot drive.")

    result = subprocess.check_output(
        ["lsblk", "--json", "--bytes", "--output",
         "NAME,PATH,TYPE,SIZE,MODEL,SERIAL,RO,MAJ:MIN,MOUNTPOINTS"],
        text=True,
    )
    for disk in json.loads(result)["blockdevices"]:
        if disk["type"] != "disk" or disk["ro"] or disk["size"] < MIN_DISK_BYTES:
            continue
        if any(
            node["maj:min"] == medium or any(node["mountpoints"] or [])
            for node in descendants(disk)
        ):
            continue
        yield disk


def fingerprint(disk):
    return "|".join(str(disk[key] or "") for key in ("maj:min", "size", "serial"))


def description(disk):
    model = (disk["model"] or "Drive").strip()
    size = disk["size"] / 10**9
    serial = (disk["serial"] or "").strip()
    detail = f"{serial} · " if serial else ""
    return f"{model} · {size:.1f} GB · {detail}{os.path.basename(disk['path'])}"


def run(*command, **kwargs):
    print(shlex.join(command), file=sys.stderr, flush=True)
    return subprocess.run(command, check=True, text=True, stdout=sys.stderr, **kwargs)


def partitions(disk):
    parent = Path("/sys/class/block", Path(disk).name).resolve()
    for _ in range(20):
        devices = {
            (child / "partition").read_text().strip(): Path("/dev", child.name)
            for child in parent.iterdir() if (child / "partition").is_file()
        }
        if devices.keys() == {"1", "2"} and all(path.is_block_device() for path in devices.values()):
            return str(devices["1"]), str(devices["2"])
        time.sleep(0.5)
    raise RuntimeError("The new partitions did not appear.")


def uuid(device):
    return subprocess.check_output(["blkid", "-s", "UUID", "-o", "value", device], text=True).strip()


@contextmanager
def install_target(disk, progress):
    progress("Preparing the selected drive…")
    table = "label: gpt\n\nsize=512MiB, type=uefi\ntype=linux\n"
    run("sfdisk", "--wipe", "always", "--wipe-partitions", "always", disk, input=table)
    run("udevadm", "settle")
    efi, linux = partitions(disk)
    run("mkfs.vfat", "-F", "32", "-n", "TYPEWRITER", efi)
    run("mkfs.ext4", "-q", "-F", "-L", "Typewriter", linux)

    with tempfile.TemporaryDirectory(prefix="typewriter-install-", dir="/run") as mountdir:
        target = Path(mountdir)
        run("mount", linux, mountdir)
        try:
            progress("Copying the system to the drive…")
            run("rsync", "-aHAX", "--numeric-ids", f"{LIVE_ROOT}/", f"{target}/")
            (target / "etc/fstab").write_text(
                f"UUID={uuid(linux)} / ext4 defaults,errors=remount-ro 0 1\n"
                f"UUID={uuid(efi)} /boot/efi vfat umask=0077 0 2\n"
            )
            (target / "etc/machine-id").write_text("")
            (target / "var/lib/systemd/random-seed").unlink(missing_ok=True)

            (target / "boot/efi").mkdir(exist_ok=True)
            run("mount", efi, str(target / "boot/efi"))
            for path in ("dev", "proc", "sys"):
                destination = str(target / path)
                run("mount", "--rbind", f"/{path}", destination)
                run("mount", "--make-rslave", destination)
            yield target
            os.sync()
        finally:
            run("umount", "--recursive", mountdir)


def make_bootable(target):
    run(
        "chroot", str(target), "grub-install", "--target=x86_64-efi",
        "--efi-directory=/boot/efi", "--removable", "--no-nvram",
    )
    run("chroot", str(target), "update-grub")
