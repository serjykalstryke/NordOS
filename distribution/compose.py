#!/usr/bin/env python3
"""Build the NordOS source composition into an unprivileged staging directory."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import sys


HERE = Path(__file__).resolve().parent
REPOSITORY = HERE.parent
MARKER = ".nordos-build-root.json"


class BuildError(Exception):
    pass


def run(command, *, cwd=None, env=None, capture=False):
    result = subprocess.run(command, cwd=cwd, env=env, text=True,
                            stdout=subprocess.PIPE if capture else None,
                            stderr=subprocess.PIPE if capture else None)
    if result.returncode:
        detail = (result.stderr or result.stdout or "").strip() if capture else ""
        raise BuildError(f"Command failed ({result.returncode}): {shlex.join(map(str, command))}\n{detail}")
    return result.stdout.strip() if capture else ""


def read_composition(path):
    data = json.loads(path.read_text())
    if data.get("format") != 1:
        raise BuildError("Unsupported composition format")
    result = {}
    for entry in data["components"]:
        name = entry["name"]
        if not re.fullmatch(r"[a-z][a-z0-9-]*", name) or name in result:
            raise BuildError(f"Invalid or duplicate component name: {name}")
        if "local" not in entry:
            if not re.fullmatch(r"[0-9a-f]{40}", entry.get("revision", "")):
                raise BuildError(f"{name} needs a full commit pin")
            if not entry.get("url", "").startswith("https://"):
                raise BuildError(f"{name} needs an HTTPS source URL")
        result[name] = entry
    select_components(result, None, False)  # Validate dependencies and cycles.
    return result


def select_components(components, only, with_dependencies):
    wanted = list(components) if not only else only.split(",")
    if any(name not in components for name in wanted):
        raise BuildError("Unknown component selection. Choose from: " + ", ".join(components))
    order, visiting, visited = [], set(), set()

    def visit(name):
        if name in visiting:
            raise BuildError(f"Dependency cycle at {name}")
        if name in visited:
            return
        visiting.add(name)
        for dependency in components[name].get("requires", []):
            if dependency not in components:
                raise BuildError(f"{name} has unknown dependency {dependency}")
            visit(dependency)
        visiting.remove(name)
        visited.add(name)
        if not only or with_dependencies or name in wanted:
            order.append(name)

    for name in wanted:
        visit(name)
    return order


def source_overrides(values, components):
    overrides = {}
    for value in values:
        name, separator, path = value.partition("=")
        if not separator or name not in components or not path or name in overrides:
            raise BuildError(f"Invalid or duplicate source override: {value}")
        overrides[name] = Path(path).expanduser().resolve()
    return overrides


def source_path(name, entry, workspace, overrides):
    if name in overrides:
        return overrides[name]
    if "local" in entry:
        return (HERE / entry["local"]).resolve()
    return workspace / "sources" / name


def ensure_workspace(workspace):
    workspace = workspace.resolve()
    if workspace == REPOSITORY or workspace in REPOSITORY.parents:
        raise BuildError("Build output must not be the repository or one of its parent directories")
    if workspace.is_relative_to(REPOSITORY) and not workspace.is_relative_to(REPOSITORY / "build"):
        raise BuildError("In-repository output must be under build/")
    marker = workspace / MARKER
    if workspace.exists() and not marker.is_file() and any(workspace.iterdir()):
        raise BuildError(f"Refusing to use nonempty, unowned output directory: {workspace}")
    expected = {"repository": str(REPOSITORY), "format": 1}
    if marker.exists() and json.loads(marker.read_text()) != expected:
        raise BuildError(f"Output directory belongs to another build: {workspace}")
    for name in ("sources", "build", "stage", "records"):
        if (workspace / name).is_symlink():
            raise BuildError(f"Build output directory must not be a symlink: {workspace / name}")
    workspace.mkdir(parents=True, exist_ok=True)
    marker.write_text(json.dumps(expected, indent=2) + "\n")
    return workspace


def git(path, *arguments):
    return run(["git", "-C", str(path), *arguments], capture=True)


def source_record(name, entry, path, *, check_vendor=True):
    if not (path / "CMakeLists.txt").is_file():
        raise BuildError(f"{name}: source missing at {path}. Fetch it or provide --source {name}=PATH")
    if Path(git(path, "rev-parse", "--show-toplevel")).resolve() != path.resolve():
        raise BuildError(f"{name}: source must be the root of its own Git checkout")
    head = git(path, "rev-parse", "HEAD")
    # Include untracked source additions, while respecting .gitignore build output.
    status = git(path, "status", "--porcelain", "--untracked-files=all")
    record = {"name": name, "path": str(path), "roles": entry.get("roles", []),
              "commit": head, "working_tree_modified": bool(status)}
    if "local" not in entry:
        if head != entry["revision"]:
            raise BuildError(f"{name}: expected commit {entry['revision']}, found {head} at {path}")
        if status:
            raise BuildError(f"{name}: external source has local changes. Use a clean checkout of its pinned revision")
        record["url"] = entry["url"]
    else:
        record["tracked_diff_sha256"] = hashlib.sha256(
            git(path, "diff", "HEAD", "--binary").encode()).hexdigest()
        untracked = git(path, "ls-files", "--others", "--exclude-standard", "-z")
        record["untracked_files"] = {}
        for name in filter(None, untracked.split("\0")):
            item = path / name
            payload = os.readlink(item).encode() if item.is_symlink() else item.read_bytes()
            record["untracked_files"][name] = hashlib.sha256(payload).hexdigest()
    vendor = entry.get("vendor")
    if vendor and check_vendor:
        vendor_path = path / vendor["path"]
        if not (vendor_path / "BUILD.gn").is_file() or not (vendor_path / "bin/gn").is_file():
            raise BuildError(f"{entry['name']}: pinned Skia/GN inputs are missing. Prepare this source with: bash {shlex.quote(str(path / vendor['prepare']))}")
        if git(vendor_path, "rev-parse", "HEAD") != vendor["revision"]:
            raise BuildError(f"{entry['name']}: Skia must be at {vendor['revision']}")
        if git(vendor_path, "status", "--porcelain", "--untracked-files=no"):
            raise BuildError(f"{entry['name']}: pinned Skia has tracked local changes")
        record["vendor"] = {"revision": vendor["revision"],
                            "gn_sha256": hashlib.sha256((vendor_path / "bin/gn").read_bytes()).hexdigest()}
    return record


def build_environment(workspace):
    env = dict(os.environ)
    prefix = workspace / "stage/usr"
    # A prefix is sufficient for Cutefish's relocatable CMake exports. Do not
    # set PKG_CONFIG_SYSROOT_DIR: Debian's other dependencies remain on the host.
    env["CMAKE_PREFIX_PATH"] = str(prefix) + (os.pathsep + env["CMAKE_PREFIX_PATH"] if env.get("CMAKE_PREFIX_PATH") else "")
    pkg_dirs = [prefix / "lib/pkgconfig", prefix / "share/pkgconfig"]
    pkg_dirs.extend(sorted((prefix / "lib").glob("*/pkgconfig")))
    env["PKG_CONFIG_PATH"] = os.pathsep.join(map(str, pkg_dirs)) + (os.pathsep + env["PKG_CONFIG_PATH"] if env.get("PKG_CONFIG_PATH") else "")
    env.pop("DESTDIR", None)
    return env


def check_requirements(entries, generator, env):
    commands = {"git", "cmake", "pkg-config"}
    commands.add(shlex.split(env.get("CXX") or "c++")[0])
    commands.add(shlex.split(env.get("CC") or "cc")[0])
    commands.add("ninja" if generator == "Ninja" else "make")
    for entry in entries:
        commands.update(entry.get("tools", []))
    missing = [command for command in sorted(commands) if not shutil.which(command, path=env.get("PATH"))]
    problems = ["Missing build tools: " + ", ".join(missing)] if missing else []
    if "pkg-config" not in missing:
        requirements = sorted({item for entry in entries for item in entry.get("pkg_config", [])})
        for requirement in requirements:
            result = subprocess.run(["pkg-config", "--exists", requirement], env=env,
                                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if result.returncode:
                problems.append("Missing development dependency: " + requirement)
    return problems


def fetch_source(name, entry, path):
    if "local" in entry or path.exists():
        source_record(name, entry, path, check_vendor=False)
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    run(["git", "init", "--quiet", str(path)])
    run(["git", "-C", str(path), "remote", "add", "origin", entry["url"]])
    run(["git", "-C", str(path), "fetch", "--depth=1", "origin", entry["revision"]])
    run(["git", "-C", str(path), "checkout", "--detach", "FETCH_HEAD"])
    source_record(name, entry, path, check_vendor=False)


def build_component(name, path, workspace, generator, jobs, env):
    build = workspace / "build" / name
    if build.is_symlink():
        raise BuildError(f"Component build directory must not be a symlink: {build}")
    run(["cmake", "-S", str(path), "-B", str(build), "-G", generator,
         "-DCMAKE_BUILD_TYPE=RelWithDebInfo", "-DCMAKE_INSTALL_PREFIX=/usr",
         "-DCMAKE_INSTALL_LIBDIR=lib", "-DBUILD_TESTING=OFF"], env=env)
    run(["cmake", "--build", str(build), "--parallel", str(jobs)], env=env)
    stage = workspace / "stage"
    for item in stage.rglob("*"):
        if item.is_symlink() and not item.resolve().is_relative_to(stage.resolve()):
            raise BuildError(f"Staging contains a symlink outside its tree: {item}")
    install_env = dict(env, DESTDIR=str(workspace / "stage"))
    run(["cmake", "--install", str(build)], env=install_env)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("plan", "check", "fetch", "build"))
    parser.add_argument("--only", help="Comma-separated components. Dependencies must already be installed/staged unless --with-dependencies is used")
    parser.add_argument("--with-dependencies", action="store_true")
    parser.add_argument("--source", action="append", default=[], metavar="NAME=PATH")
    parser.add_argument("--workspace", type=Path, default=REPOSITORY / "build/system")
    parser.add_argument("--generator", choices=("Unix Makefiles", "Ninja"), default="Unix Makefiles")
    parser.add_argument("--jobs", type=int, default=2)
    args = parser.parse_args(argv)
    if args.jobs < 1:
        raise BuildError("--jobs must be positive")
    components = read_composition(HERE / "composition.json")
    order = select_components(components, args.only, args.with_dependencies)
    overrides = source_overrides(args.source, components)
    workspace = args.workspace.expanduser().resolve()
    paths = {name: source_path(name, components[name], workspace, overrides) for name in order}
    for name in order:
        print(f"{name}: {paths[name]} [{', '.join(components[name]['roles'])}]", flush=True)
    if args.only and not args.with_dependencies:
        print("Unselected prerequisites must be supplied by the existing SDK or staging tree.", flush=True)
    if args.action == "plan":
        return 0
    if args.action in ("fetch", "build"):
        ensure_workspace(workspace)
    if args.action == "fetch":
        for name in order:
            if name in overrides:
                source_record(name, components[name], paths[name], check_vendor=False)
            else:
                fetch_source(name, components[name], paths[name])
        print("Pinned component sources are ready. Toolkit vendor inputs are prepared separately.")
        return 0
    env = build_environment(workspace)
    problems = check_requirements([components[name] for name in order], args.generator, env)
    records = []
    for name in order:
        try:
            records.append(source_record(name, components[name], paths[name]))
        except BuildError as error:
            problems.append(str(error))
    if problems:
        raise BuildError("Preflight failed:\n- " + "\n- ".join(problems))
    if args.action == "check":
        print("Source and basic dependency checks passed. CMake configuration validates remaining SDK and header requirements.")
        return 0
    records_dir = workspace / "records"
    records_dir.mkdir(parents=True, exist_ok=True)
    receipt = {"composition": json.loads((HERE / "composition.json").read_text()),
               "sources": records, "generator": args.generator, "completed": []}
    receipt_path = records_dir / "build.json"
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n")
    if shutil.which("dpkg-query"):
        (records_dir / "host-packages.txt").write_text(run(["dpkg-query", "-W"], capture=True) + "\n")
    for name in order:
        print(f"Building and staging {name}", flush=True)
        build_component(name, paths[name], workspace, args.generator, args.jobs,
                        build_environment(workspace))
        receipt["completed"].append(name)
        receipt_path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(f"Staged system files: {workspace / 'stage'}")
    print("This is a staged development composition. Boot, login, and installation still require validation in a disposable system.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (BuildError, OSError, ValueError, KeyError) as error:
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)
