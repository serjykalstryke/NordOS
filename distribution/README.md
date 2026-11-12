# Building the NordOS system composition

This directory composes selected Cutefish implementations with the reorganized local NordOS core. `composition.json` assigns architectural roles and pins external source revisions. Some inherited repositories still supply several roles. The build composition keeps those dependencies usable while source responsibilities are extracted.

The result is an install tree for development. The [image backend](image/README.md) packages that tree and boots it in a development VM. Use an ordinary user account for the source build. CMake configuration and building execute the selected source code, so build trusted sources in an appropriate development environment.

## Build the reorganized core now

From the NordOS repository, with the Cutefish toolkit/framework SDK and core development dependencies available, run

```sh
python3 distribution/compose.py plan --only core
python3 distribution/compose.py check --only core
python3 distribution/compose.py build --only core --jobs 2
```

The core is this repository's current working tree, including the source reorganization being developed. `--only` uses just the named components and relies on an installed or previously staged SDK for their prerequisites. Add `--with-dependencies` to build their source dependencies too. Select several components with a comma, for example `--only core,compositor`.

Builds use `build/system/` by default. `stage/` contains the installed files, `build/` the component build trees, and `records/` the source receipt and host package versions. `--workspace /absolute/path/to/new-output` changes that location. The driver refuses to adopt an unrelated nonempty output directory or a directory marked as belonging to another repository. It does not clean output or reset source checkouts.

The default generator is Unix Makefiles. `--generator Ninja` selects Ninja. Existing `CC`, `CXX`, `CMAKE_PREFIX_PATH`, and `PKG_CONFIG_PATH` settings can supply a workspace-local compiler or development SDK. The staged `/usr` prefix is prepended for subsequent components. The driver does not introduce a global pkg-config sysroot that would incorrectly relocate unrelated host libraries.

## Compose the selected system from source

The order includes toolkit, framework, core, compositor, File Manager, Settings, portal, icons, and wallpapers. File Manager supplies a presentation application and currently also hosts desktop and file-service responsibilities. Keeping that implementation available does not assign ownership of saved-data concepts to the application.

```sh
python3 distribution/compose.py plan
python3 distribution/compose.py fetch
bash build/system/sources/toolkit/scripts/fetch-skia.sh
python3 distribution/compose.py check
python3 distribution/compose.py build --jobs 2
```

`fetch` is the explicit network step for component sources. It creates separate shallow checkouts at the recorded commits, retaining those commits' identity and license files. It refuses a source at another revision or with local changes. The toolkit uses the previously recorded Snap-integration commit. Wallpapers use the pinned upstream source while that fork remains pending.

Skia is prepared separately with the pinned toolkit's helper, which also obtains its GN tool. The driver checks the Skia revision and records the GN file hash. It does not automatically execute source-provided download helpers. The full component set and its pins still require an integration build and runtime validation before becoming a release baseline.

A preexisting clean source checkout can be supplied explicitly

```sh
python3 distribution/compose.py check --only framework --source framework=/path/to/cutefish-framework
```

External overrides must match the composition pin. Change the reviewed pin when adopting another revision. The core is deliberately different because it is the NordOS development source and can have local edits.

## Prerequisites and evidence

The initial host baseline is Debian 13. `check` reports missing build tools, pkg-config development dependencies, source pins, and toolkit vendor inputs before compilation. CMake then checks remaining headers, libraries, and exported SDK packages. The component recipes in the Cutefish packaging repository remain the reference for host build dependencies, including dependencies without pkg-config metadata such as PAM, LZFSE, and libzip.

Every install uses `/usr` as its target prefix with `DESTDIR` set to the staging tree. Existing Linux paths and service identifiers remain available while NordOS interfaces are separated. The Debian image backend supplies the kernel, base, login manager, host services, runtime dependencies, and boot configuration. Distribution updates and recovery remain separate work.

`records/build.json` records the selected source commits, roles, local core diff hash, hashes of untracked core files, and components completed in that invocation. `records/host-packages.txt` records installed Debian package versions where available. These are build receipts, not a claim of bit-for-bit reproducibility. Preserve or commit local core changes to reproduce them. A fresh output directory is recommended when changing composition pins, because old staged files are retained and the receipt covers the current invocation.

Run the offline driver checks with

```sh
python3 -m unittest discover -s distribution -p 'test_*.py' -v
```

The checks cover dependency selection, invalid and dirty sources, output ownership, staging environment behavior, and an actual CMake install into a temporary stage. They do not substitute for building the selected Cutefish components or testing boot and login.
