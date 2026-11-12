from pathlib import Path
import plistlib
import subprocess
import sys

root = Path(sys.argv[1])
for manifest in (root / "Applications").glob("*.app/Contents/Info.plist"):
    data = plistlib.loads(manifest.read_bytes())
    data["CFBundleShortVersionString"] = subprocess.check_output(
        ["dpkg-query", f"--admindir={root / 'var/lib/dpkg'}", "-W",
         "-f=${Version}", data["TypewriterSource"]["package"]],
        text=True,
    )
    manifest.write_bytes(plistlib.dumps(data))
