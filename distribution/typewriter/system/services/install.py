#!/usr/bin/python3
import fcntl
import os
import shutil
import subprocess
import sys

sys.path.insert(0, "/usr/local/lib/typewriter")
from adapters.sources import debian
from library.applications import STARTUP_APP, applications
from platform_linux.boot import installer_boot
from platform_linux.storage import fingerprint, install_disks, install_target, make_bootable


def progress(message):
    print(f"Progress: {message}", flush=True)


def install(disk, selected, registered):
    with install_target(disk, progress) as target:
        progress(f"Setting up {selected.name}…")
        for app in registered.values():
            if app.id != selected.id:
                debian.remove(app, target)
                shutil.rmtree(target / app.bundle.relative_to("/"))
        if not debian.installed(selected, target):
            raise RuntimeError(f"The installed copy of {selected.name} could not be verified.")
        (target / STARTUP_APP.relative_to("/")).write_text(selected.id + "\n")

        for path in (
            "etc/sudoers.d/typewriter-install", "usr/local/bin/typewriter-installer",
            "usr/local/sbin/typewriter-install",
        ):
            (target / path).unlink()
        progress("Setting up system startup…")
        make_bootable(target)


def main():
    if os.geteuid() != 0 or len(sys.argv) != 5 or sys.argv[4] != "ERASE" or not installer_boot():
        raise RuntimeError("Start the installer from the Typewriter USB in EFI mode.")

    disk_path, expected_disk, app_id = sys.argv[1:4]
    registered = applications()
    selected = registered.get(app_id)
    if selected is None or not os.access(selected.launcher, os.X_OK) or not debian.installed(selected):
        raise RuntimeError("The selected writing app is unavailable. Choose another app or recreate the installation USB.")

    with open("/run/typewriter-install.lock", "w") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as error:
            raise RuntimeError("Another installation is in progress.") from error
        disk = next((d for d in install_disks() if d["path"] == disk_path), None)
        if disk is None or fingerprint(disk) != expected_disk:
            raise RuntimeError("The selected drive changed or is in use. Choose a drive again.")
        install(disk["path"], selected, registered)
    progress("Installation complete.")


if __name__ == "__main__":
    try:
        main()
    except (OSError, RuntimeError, subprocess.CalledProcessError) as error:
        sys.exit(str(error))
