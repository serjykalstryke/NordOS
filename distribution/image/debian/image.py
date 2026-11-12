#!/usr/bin/env python3
"""Package a staged foundation and prepare NoCloud media for a disposable VM.

This tool never installs into the host or writes a physical disk.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
PROVIDES = ["cutefish-core", "cutefish-framework", "cutefish-compositor",
            "cutefish-filemanager", "cutefish-settings", "cutefish-icon-theme",
            "cutefish-wallpapers", "xdg-desktop-portal-cutefish"]
RUNTIME_DIRS = ("usr/bin", "usr/libexec", "usr/lib")


def run(args, **kwargs):
    return subprocess.run(args, check=True, **kwargs)


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def runtime_elfs(root):
    for directory in RUNTIME_DIRS:
        for path in sorted((root / directory).glob("*")):
            if path.is_file() and not path.is_symlink():
                with path.open("rb") as stream:
                    if stream.read(4) == b"\x7fELF":
                        yield path


def dependencies_for(stage):
    stage = stage.resolve()
    binaries = list(runtime_elfs(stage))
    if not binaries:
        raise ValueError("No built executables or libraries found in the stage")
    with tempfile.TemporaryDirectory(prefix="nordos-shlibdeps-") as temp:
        debian = Path(temp) / "debian"
        debian.mkdir()
        (debian / "control").write_text(
            "Source: nordos-foundation\n\nPackage: nordos-foundation\nArchitecture: amd64\n")
        run(["dpkg-shlibdeps", "-O", "--ignore-missing-info", f"-l{stage / 'usr/lib'}",
             *(f"-e{path}" for path in binaries)], cwd=temp)


def package(stage, output, toolkit_version, dependencies, sources):
    stage, output = stage.resolve(), output.resolve()
    if output.exists():
        raise ValueError("Choose a new package output path")
    if not (stage / "usr/bin/cutefish-session").is_file():
        raise ValueError("The stage does not contain the built NordOS session")
    if not re.fullmatch(r"[A-Za-z0-9.+:~_-]+", toolkit_version):
        raise ValueError("Invalid toolkit package version")
    raw = dependencies.read_text().strip().removeprefix("shlibs:Depends=")
    runtime = [item.strip() for item in raw.split(",") if item.strip()
               and item.split()[0] not in PROVIDES + ["cutefish-toolkit"]]
    runtime += [f"cutefish-toolkit (= {toolkit_version})", "acl", "sudo"]
    with tempfile.TemporaryDirectory(prefix="nordos-package-") as temp:
        root = Path(temp) / "root"
        shutil.copytree(stage, root, symlinks=True)
        documentation = root / "usr/share/doc/nordos-foundation"
        documentation.mkdir(parents=True, exist_ok=True)
        for source in sources:
            name, separator, directory = source.partition("=")
            if not separator or not re.fullmatch(r"[a-z][a-z0-9-]*", name):
                raise ValueError("Sources must use name=directory")
            licenses = list(Path(directory).glob("LICENSE*")) + list(Path(directory).glob("COPYING*"))
            if not licenses:
                raise ValueError(f"No license found for {name}")
            destination = documentation / name
            destination.mkdir()
            for license_file in licenses:
                shutil.copy2(license_file, destination / license_file.name)
        shutil.copy2(HERE.parents[1] / "composition.json", documentation / "composition.json")
        # The development image carries runtime files. Source checkouts supply
        # headers and debug builds separately.
        for directory in [root / "usr/include", root / "usr/lib/cmake"]:
            if directory.exists():
                shutil.rmtree(directory)
        for path in runtime_elfs(root):
            run(["strip", "--strip-unneeded", str(path)])
        control = root / "DEBIAN"
        control.mkdir()
        (control / "control").write_text(
            "Package: nordos-foundation\nVersion: 0.1.0~development1\nArchitecture: amd64\n"
            "Maintainer: NordOS developers <noreply@example.invalid>\nSection: x11\nPriority: optional\n"
            + "Depends: " + ", ".join(runtime) + "\n"
            + "Provides: " + ", ".join(PROVIDES) + "\n"
            + "Conflicts: " + ", ".join(PROVIDES) + "\n"
            + "Replaces: " + ", ".join(PROVIDES) + "\n"
            + "Description: NordOS reorganized development system components\n"
            " Built core, framework, desktop and resources for the NordOS development image.\n")
        (control / "postinst").write_text("""#!/bin/sh
set -e
if [ "$1" = configure ]; then
    ldconfig
    install -d -m 2775 -o root -g sudo /Applications
    setfacl -m g:sudo:rwx -m d:g:sudo:rwx /Applications
    if command -v update-desktop-database >/dev/null; then update-desktop-database -q; fi
fi
""")
        (control / "postinst").chmod(0o755)
        (root / "etc/nordos-release").write_text(
            'NAME="NordOS"\nPRETTY_NAME="NordOS Development"\nID=nordos\nID_LIKE=debian\n'
            'VERSION="0.1 Development (Debian 13 base)"\nVERSION_ID=0.1\nVERSION_CODENAME=trixie\n')
        desktop = root / "usr/share/wayland-sessions/cutefish-wayland.desktop"
        desktop.write_text(desktop.read_text().replace("Name=Cutefish (Wayland)", "Name=NordOS (Wayland)")
                           .replace("Comment=Cutefish desktop session", "Comment=NordOS development session"))
        # Keep upstream conffiles editable and package-owned.
        (control / "conffiles").write_text("".join("/" + str(p.relative_to(root)) + "\n"
                                                   for p in sorted((root / "etc").rglob("*")) if p.is_file()))
        output.parent.mkdir(parents=True, exist_ok=True)
        run(["dpkg-deb", "--root-owner-group", "--build", str(root), str(output)])
    return {"package": output.name, "sha256": digest(output), "toolkit_version": toolkit_version}


def seed(output, packages, public_key, password_hash, manifest, xorriso):
    output = output.resolve()
    if output.exists():
        raise ValueError("Choose a new seed ISO output path")
    key = public_key.read_text().strip()
    password = password_hash.read_text().strip()
    if not key.startswith("ssh-ed25519 ") or not password.startswith("$6$"):
        raise ValueError("Expected an Ed25519 public key and a SHA-512 password hash")
    with tempfile.TemporaryDirectory(prefix="nordos-seed-") as temp:
        root = Path(temp)
        (root / "packages").mkdir()
        for package_path in packages:
            shutil.copy2(package_path, root / "packages" / package_path.name)
        shutil.copy2(HERE / "guest-setup.sh", root / "guest-setup.sh")
        shutil.copy2(manifest, root / "build-manifest.json")
        # JSON strings are valid YAML scalars and safely quote passwords/keys.
        (root / "user-data").write_text(
            '#cloud-config\nhostname: nordos\nmanage_etc_hosts: true\nssh_pwauth: false\n'
            'disable_root: true\nusers:\n  - name: nordos\n    gecos: NordOS Developer\n'
            '    shell: /bin/bash\n    groups: [sudo]\n'
            '    lock_passwd: false\n    passwd: ' + json.dumps(password) + '\n'
            '    sudo: ["ALL=(ALL) NOPASSWD:ALL"]\n    ssh_authorized_keys:\n      - '
            + json.dumps(key) + '\n'
            'runcmd:\n  - [mkdir, -p, /mnt/nordos-build]\n'
            '  - [mount, -o, ro, /dev/disk/by-label/CIDATA, /mnt/nordos-build]\n'
            '  - [bash, /mnt/nordos-build/guest-setup.sh]\n')
        (root / "meta-data").write_text('instance-id: nordos-development-1\nlocal-hostname: nordos\n')
        output.parent.mkdir(parents=True, exist_ok=True)
        run([str(xorriso), "-as", "mkisofs", "-quiet", "-volid", "CIDATA", "-joliet", "-rock",
             "-o", str(output), str(root)])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    deps = sub.add_parser("dependencies")
    deps.add_argument("--stage", type=Path, required=True)
    pkg = sub.add_parser("package")
    pkg.add_argument("--stage", type=Path, required=True)
    pkg.add_argument("--output", type=Path, required=True)
    pkg.add_argument("--toolkit-version", required=True)
    pkg.add_argument("--dependencies", type=Path, required=True)
    pkg.add_argument("--source", action="append", required=True,
                     help="Component name=source directory, repeated to preserve licenses")
    media = sub.add_parser("seed")
    media.add_argument("--output", type=Path, required=True)
    media.add_argument("--package", type=Path, action="append", required=True)
    media.add_argument("--public-key", type=Path, required=True)
    media.add_argument("--password-hash", type=Path, required=True)
    media.add_argument("--manifest", type=Path, required=True)
    media.add_argument("--xorriso", type=Path, default=Path("xorriso"))
    args = parser.parse_args()
    if args.action == "dependencies":
        dependencies_for(args.stage)
    elif args.action == "package":
        print(json.dumps(package(args.stage, args.output, args.toolkit_version, args.dependencies, args.source), indent=2))
    else:
        seed(args.output, args.package, args.public_key, args.password_hash, args.manifest, args.xorriso)


if __name__ == "__main__":
    main()
