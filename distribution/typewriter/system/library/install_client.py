from collections import deque
import subprocess

from platform_linux.storage import description, fingerprint, install_disks

INSTALLER = "/usr/local/sbin/typewriter-install"


def drives():
    return {disk["path"]: disk for disk in install_disks()}


def drive_label(disk):
    return description(disk)


def install(disk, app, update):
    lines = deque(maxlen=12)
    code = 1
    try:
        with subprocess.Popen(
            ["sudo", "-n", INSTALLER, disk["path"], fingerprint(disk), app.id, "ERASE"],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, errors="replace",
        ) as process:
            for line in process.stdout:
                line = line.strip()
                if not line:
                    continue
                lines.append(line)
                print(line, flush=True)
                if line.startswith("Progress: "):
                    update(line.removeprefix("Progress: "))
            code = process.wait()
    except OSError as error:
        lines.append(str(error))
    return code, "\n".join(lines)
