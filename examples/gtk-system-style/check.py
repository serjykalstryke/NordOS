#!/usr/bin/python3
# SPDX-License-Identifier: BSD-3-Clause
"""Check generated styles with real GTK parsers and verify backup restoration."""
import importlib.util
from pathlib import Path
import subprocess
import tempfile


HERE = Path(__file__).resolve().parent


def module(name):
    spec = importlib.util.spec_from_file_location(name, HERE / f"{name}.py")
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


bridge = module("sync")
installer = module("install")
parser = '''
import gi, sys
gi.require_version("Gtk", sys.argv[1])
from gi.repository import Gtk
errors = []
provider = Gtk.CssProvider()
provider.connect("parsing-error", lambda p, section, error: errors.append(str(error)))
provider.load_from_path(sys.argv[2])
if errors:
    raise SystemExit("\\n".join(errors))
'''

with tempfile.TemporaryDirectory(prefix="nordos-gtk-check-") as tmp:
    root = Path(tmp)
    for dark in (False, True):
        for accent in range(len(bridge.ACCENTS)):
            target = root / f"style-{dark}-{accent}"
            bridge.render({"isDarkMode": dark, "accentColor": accent,
                           "systemFont": 'A "quoted" font', "systemFontPointSize": 9}, target)
            for version in ("3.0", "4.0"):
                subprocess.run(["/usr/bin/python3", "-c", parser, version,
                                str(target / f"gtk-{version}.css")], check=True)
    original = root / "existing.css"
    absent = root / "absent.ini"
    original.write_text("/* original user stylesheet */\n")
    records = installer.backup_files([original, absent], root / "backup")
    original.write_text("replacement")
    absent.write_text("created")
    installer.restore_files(records)
    assert original.read_text() == "/* original user stylesheet */\n"
    assert not absent.exists()

print("Passed: both GTK parsers, all 7 accents in both modes, backup/restore.")
