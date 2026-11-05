#!/usr/bin/python3
# SPDX-License-Identifier: BSD-3-Clause
"""Install or remove the per-user GTK system-appearance bridge."""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shutil
import subprocess


CONFIG = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
STATE = Path(os.environ.get("XDG_STATE_HOME", Path.home() / ".local/state")) / "cutefish-gtk-style"
DATA = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local/share"))
ROOT = CONFIG / "cutefish-gtk-style"
UNIT = CONFIG / "systemd/user/cutefish-gtk-style.service"
RECORD = STATE / "installation.json"
SERVICE = "cutefish-gtk-style.service"


def command(*args):
    subprocess.run(args, check=True)


def backup_files(paths, directory):
    directory.mkdir(parents=True)
    records = []
    for index, path in enumerate(paths):
        if path.is_symlink():
            raise RuntimeError(f"Review the managed symlink before installing: {path}")
        saved = directory / str(index)
        if path.exists():
            shutil.copy2(path, saved)
        records.append({"path": str(path), "backup": str(saved) if path.exists() else None})
    return records


def restore_files(records):
    for record in records:
        path = Path(record["path"])
        if record["backup"]:
            path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(record["backup"], path)
        else:
            path.unlink(missing_ok=True)


def uninstall():
    if not RECORD.exists():
        raise SystemExit("No installation record found; no files changed.")
    records = json.loads(RECORD.read_text())
    command("systemctl", "--user", "disable", "--now", SERVICE)
    restore_files(records)
    shutil.rmtree(ROOT, ignore_errors=True)
    command("systemctl", "--user", "daemon-reload")
    RECORD.unlink()
    print("Previous GTK configuration restored. Close and reopen apps to refresh it.")


def install():
    # Check dependencies and the live desktop before modifying configuration.
    if os.getuid() == 0:
        raise SystemExit("Run as the desktop user, without sudo.")
    from gi.repository import Gio, GLib
    bus = Gio.bus_get_sync(Gio.BusType.SESSION, None)
    bus.call_sync("org.cutefish.Services", "/org/cutefish/Services/Appearance",
                  "org.freedesktop.DBus.Properties", "GetAll",
                  GLib.Variant("(s)", ("org.cutefish.Services.Appearance",)),
                  GLib.VariantType.new("(a{sv})"), Gio.DBusCallFlags.NONE, 3000, None)
    command("systemctl", "--user", "is-active", "default.target")
    source = Path(__file__).resolve().with_name("sync.py")
    if ROOT.exists() and not RECORD.exists():
        raise SystemExit(f"Review the existing directory before installing: {ROOT}")
    flatpak = shutil.which("flatpak")
    if not RECORD.exists():
        paths = [CONFIG / "gtk-3.0/gtk.css", CONFIG / "gtk-4.0/gtk.css",
                 CONFIG / "gtk-4.0/settings.ini", UNIT]
        if flatpak:
            paths.append(DATA / "flatpak/overrides/global")
        stamp = datetime.now(timezone.utc).strftime("backup-%Y%m%dT%H%M%SZ")
        records = backup_files(paths, STATE / stamp)
        RECORD.write_text(json.dumps(records, indent=2) + "\n")
    ROOT.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, ROOT / "sync.py")
    installed_installer = ROOT / "install.py"
    if Path(__file__).resolve() != installed_installer.resolve():
        shutil.copy2(__file__, installed_installer)
    command("/usr/bin/python3", str(ROOT / "sync.py"), "--once")
    for version in (3, 4):
        gtk = CONFIG / f"gtk-{version}.0/gtk.css"
        gtk.parent.mkdir(parents=True, exist_ok=True)
        gtk.write_text('/* Follow the Cutefish desktop appearance. */\n'
                       f'@import url("../cutefish-gtk-style/gtk-{version}.0.css");\n')
    UNIT.parent.mkdir(parents=True, exist_ok=True)
    # systemd specifiers and quoting are escaped even for unusual config paths.
    script = str(ROOT / "sync.py").replace("%", "%%").replace("\\", "\\\\").replace('"', '\\"')
    UNIT.write_text('[Unit]\nDescription=Match GTK application styling to Cutefish\n\n'
                    '[Service]\nType=simple\n'
                    f'ExecStart=/usr/bin/python3 "{script}"\n'
                    'Restart=on-failure\nRestartSec=3\n\n'
                    '[Install]\nWantedBy=default.target\n')
    if flatpak:
        command(flatpak, "override", "--user", "--filesystem=xdg-config/gtk-3.0:ro",
                "--filesystem=xdg-config/gtk-4.0:ro", "--filesystem=xdg-config/cutefish-gtk-style:ro")
    command("systemctl", "--user", "daemon-reload")
    command("systemctl", "--user", "enable", SERVICE)
    command("systemctl", "--user", "restart", SERVICE)
    print("GTK now follows Cutefish. Close and reopen apps to load the styling.")
    print(f"Original files are recorded in {RECORD}; use --uninstall to restore them.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--uninstall", action="store_true", help="restore the saved pre-installation configuration")
    args = parser.parse_args()
    uninstall() if args.uninstall else install()
