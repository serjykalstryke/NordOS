import subprocess


def power_off():
    subprocess.run(["/usr/local/bin/typewriter-power", "poweroff"], check=True)
