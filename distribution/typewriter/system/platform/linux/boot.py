from pathlib import Path

LIVE_MEDIUM = Path("/run/live/medium")
LIVE_ROOT = Path("/run/live/rootfs/filesystem.squashfs")


def boot_option(name):
    for option in Path("/proc/cmdline").read_text().split():
        key, _, value = option.partition("=")
        if key == name:
            return value
    return None


def installer_boot():
    return (
        boot_option("typewriter.install") == "1"
        and Path("/sys/firmware/efi").is_dir()
        and LIVE_ROOT.is_mount()
    )


def preview_app():
    if LIVE_ROOT.is_mount():
        return boot_option("typewriter.app")
    return None
