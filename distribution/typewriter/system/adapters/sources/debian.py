from pathlib import Path
import subprocess


def installed(app, root=Path("/")):
    status = subprocess.run(
        ["dpkg-query", f"--admindir={root / 'var/lib/dpkg'}",
         "-W", "-f=${db:Status-Status}", app.package],
        capture_output=True, text=True, check=False,
    )
    return status.returncode == 0 and status.stdout == "installed"


def remove(app, root):
    subprocess.run(
        ["chroot", str(root), "dpkg", "--purge", app.package],
        check=True,
    )
