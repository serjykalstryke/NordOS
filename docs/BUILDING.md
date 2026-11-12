# Building the NordOS foundation

The core now builds from the NordOS source structure. The selected external Cutefish components remain separately pinned inputs while their responsibilities are gradually extracted. The build produces a staged development system that can be packaged into a [bootable VM disk](../distribution/image/README.md).

The core, framework, compositor, File Manager, Settings, portal, and resources have been built and staged using the installed toolkit SDK. See [the validation record](FOUNDATION_STATUS.md) for tested revisions, results, and limitations.

## Source ownership

```text
system/
  library/
    core/                         shared environment helpers and service clients
    platform/power.h              platform power request contract
  services/
    session/                      lifecycle, startup and shutdown policy
    applications/runtime/         application execution service
    applications/placement/       shared application-folder authority
    desktop/                      inherited appearance, power, permission and other services
    locales/                      locale management
    privacy/                      device privacy management
    capture/                      screen recording service
  desktop/
    authorization/                graphical authorization agent
    session/                      selected desktop component roles
  platform/linux/
    power.cpp                     logind implementation of power requests
    process.cpp                   inherited Linux process-launch implementation
distribution/
  composition.json                selected external components, roles and source pins
  compose.py                      source checks, build order and staged installation
```

The initial pass preserves executable names, service names, installed Linux paths, and source attribution. Several inherited services still contain presentation or Linux-specific code. The source structure identifies responsibility, and further interface extractions will narrow those dependencies. The power contract is the first explicit NordOS interface backed by Linux.

## Build and stage the core

Use a Debian 13 development environment with CMake, a C++20 compiler, pkg-config, the Cutefish toolkit and framework development files, and the core development dependencies. These include ICU, Fontconfig, systemd, Wayland and its scanner/protocols, GBM, FFmpeg, libva, libdrm, and PipeWire. The recorder and desktop services are included in the ordinary build. `distribution/compose.py check --only core` reports missing development inputs, with remaining SDK checks handled by CMake.

From the NordOS repository run

```sh
python3 distribution/compose.py check --only core
python3 distribution/compose.py build --only core --jobs 4
```

This uses the local working tree and an installed or previously staged toolkit/framework SDK. The installed files are written under `build/system/stage/`. The driver records the source revision, local changes, component roles, and completion in `build/system/records/`. No administrator access is needed for staging.

For the equivalent direct CMake build

```sh
cmake -S . -B build/core -DCMAKE_INSTALL_PREFIX=/usr -DCMAKE_BUILD_TYPE=RelWithDebInfo
cmake --build build/core --parallel 4
DESTDIR="$PWD/build/core-stage" cmake --install build/core
```

`/usr` is the target system prefix. `DESTDIR` keeps installation inside the development directory. A staged core requires the rest of the selected desktop and Debian runtime services to operate.

## Compose the essential desktop

The [composition driver](../distribution/README.md) brings together the toolkit, framework, local NordOS core, compositor, File Manager, Settings, portal, icons, and wallpapers. It supports explicit source fetching, pinned local source overrides, and individual component builds. Source selection is distinct from the architecture boundaries inside those repositories.

```sh
python3 distribution/compose.py plan
python3 distribution/compose.py fetch
bash build/system/sources/toolkit/scripts/fetch-skia.sh
python3 distribution/compose.py check
python3 distribution/compose.py build --jobs 4
```

Toolkit preparation obtains the pinned Skia source and GN build tool. The build checks that pin and records the GN hash. Full system builds need the development packages listed by each component's upstream Debian recipe, including dependencies that have no pkg-config metadata. The source lock describes the intended composition and must be validated together before it is a release baseline.

## Choose the session implementations

`system/desktop/session/` defines build-time roles for the compositor, resident file/desktop surface, authorization agent, application runtime, and desktop services. The defaults preserve the inherited Cutefish session. For example, a compatible replacement compositor can be selected with

```sh
cmake -S . -B build/core -DCMAKE_INSTALL_PREFIX=/usr \
  -DNORDOS_COMPOSITOR=/usr/bin/nordos-compositor
```

The session startup and login entry use that selection. The other options are `NORDOS_FILE_SURFACE`, `NORDOS_AUTHORIZATION_AGENT`, `NORDOS_APPLICATION_RUNTIME`, and `NORDOS_DESKTOP_SERVICES`. Values are executable names or paths without arguments. Replacements must supply the existing readiness, private Wayland connection, and service interfaces until those contracts are changed deliberately. This is a composition boundary, not arbitrary interchangeability.

## Run the tests

Test projects remain independently configurable. Their current locations are listed in `.github/workflows/build.yml`. GoogleTest is required for most inherited suites. For example

```sh
cmake -S system/services/session/tests -B build/session-tests -DCMAKE_INSTALL_PREFIX=/usr
cmake --build build/session-tests --parallel 4
ctest --test-dir build/session-tests --output-on-failure

cmake -S tests/platform-power -B build/platform-power
cmake --build build/platform-power --parallel 4
ctest --test-dir build/platform-power --output-on-failure

cmake -S tests/session-composition -B build/session-composition
cmake --build build/session-composition --parallel 4
ctest --test-dir build/session-composition --output-on-failure

python3 -m unittest discover -s distribution -p 'test_*.py' -v
```

Private D-Bus and Wayland fixtures require permission to create local sockets. They use isolated service instances. The language fixture also needs `en_US.UTF-8` and `en_SG.UTF-8`, which can be generated in a development directory and supplied through `LOCPATH`. Live compositor cases are opt-in through `CUTEFISH_TEST_COMPOSITOR` and start a separate headless instance. GPU-dependent cases may skip if suitable hardware is unavailable. Record skipped cases alongside results.

## Integration still required

Follow the [system architecture](SYSTEM_ARCHITECTURE.md) for further sorting. File Manager is a presentation application over system-owned capabilities. Its current desktop and file-operation coupling needs its own extraction. Shared application identity, managed dependency storage, compatibility providers, and AI context/action interfaces remain later implementation work.

The [Debian image backend](../distribution/image/debian/README.md) provides the initial boot platform and runtime packages. Boot and login are verified separately from staging. Hardware installation, migration, updates, and recovery remain open.
