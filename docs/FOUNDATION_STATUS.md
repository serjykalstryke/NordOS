# NordOS foundation implementation status

November 11, 2026

## Implemented source structure

The inherited core is reorganized into four buildable areas. Shared environment helpers and service clients live in `system/library/core`. Session, application execution and placement, language, privacy, recording, and desktop services live under `system/services`. Authorization UI and session component selection live under `system/desktop`. Linux power and process implementations live under `system/platform/linux`.

The first explicit NordOS platform interface is `system/library/platform/power.h`. Session policy requests reboot, shutdown, or suspend through it. The Linux implementation preserves logind and interactive authorization behavior. Its result means a request was accepted, with completion observed separately.

Session composition now selects the compositor, resident file/desktop surface, authorization UI, application runtime, and desktop services at build time. Startup, autostart exclusion, and the login entry follow these choices. Existing executable names, service identifiers, and Linux installation paths remain the default while responsibilities are extracted.

The distribution driver composes selected implementations by architectural role and exact source revision. It accepts the modified local core, rejects mismatched external revisions, records source evidence, and installs into an unprivileged staging directory. The updated workflow uses the relocated test paths and includes the new platform, composition, and driver checks.

## Build results

All of the following were compiled or processed from the selected sources and installed into the same staged tree.

| Component | Source used | Result |
|---|---|---|
| NordOS core | Local modified tree based on `d3155540af5b` | Compiled and staged |
| File framework and system clients | `19712540d65e` | Compiled and staged |
| Compositor and shell | `97118a809447` | Compiled and staged |
| File Manager | `8f9da407826f` | Compiled and staged |
| Settings | `1012d911d0a0` | Compiled and staged |
| Desktop portal | `19765bcce468` | Compiled and staged |
| Icon resources | `a38be51fe7f6` | Processed and staged |
| Wallpapers and account pictures | `ba6fbf6bd965` | Processed and staged |

This validation reused the installed toolkit development package, recorded as `1.0~git20261111034643.6371e1b-1` at final validation. The toolkit and Skia were not rebuilt. The source composition also records the earlier toolkit Snap-integration pin for a future full source build. That entire source-only combination still needs validation together.

The build used Debian 13 development files extracted into a workspace-local overlay, plus installed SDK and runtime libraries. No build packages were installed into the running OS. The ordinary build instructions assume a development environment with those dependencies available. The staging tree contains project components and still depends on the host's base libraries.

## Verification

- The reorganized core's staged file inventory matches the untouched baseline's 29 installed files.
- All 33 CTest targets across 14 core/platform suites passed with the required private IPC and locale fixtures available.
- Two additional session-composition tests passed, including replacement executable selection and rejection of malformed choices.
- Nine build-driver tests passed, including an actual CMake install confined to a temporary staging directory.
- The alternate-compositor configuration was checked through the generated login entry.
- All five Xwayland/session integration cases passed against the newly built compositor. This exercised headless native Wayland startup/shutdown and Xwayland startup, readiness, client access, and shutdown.
- Shared-library resolution checks passed for 28 staged ELF executables and libraries against the staged framework and available host runtimes.

The locale fixture required locally generated `en_US.UTF-8` and `en_SG.UTF-8` data. The ordinary session suite leaves real compositor cases optional. Those cases were then run explicitly against the staged compositor in a private runtime directory with private configuration and D-Bus.

The installed compositor binary crashed during the no-Xwayland shutdown check with both the original and reorganized session tests. The compositor built from the pinned source passed that same check. This validates the staged binary for that scenario and does not establish the cause of the installed binary's failure.

## Remaining work

This is the first buildable foundation. Several inherited components still combine responsibilities internally. In particular, File Manager's persistent desktop and file-operation roles need further separation from its presentation application, and the toolkit/framework still contain host-specific mechanisms.

The full platform API, unified application identity, dependency storage, compatibility providers, and AI context/action services are not implemented by this reorganization. Existing app payloads have not been ported to the NordOS bundle model.

The [Debian image backend](../distribution/image/README.md) now supplies the kernel, base system, runtime packages, login manager, and boot configuration for the development VM. It boots the staged foundation into Wayland with the essential desktop tools. USB and physical hardware installation, migration, updates and recovery, and full self-hosted builds remain open.

See [the build guide](BUILDING.md), [system architecture](SYSTEM_ARCHITECTURE.md), and [composition driver](../distribution/README.md) for the actual source layout, commands, and further extraction plan.
