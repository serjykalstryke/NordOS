# Typewriter 0.2

Typewriter boots into one writing app. The installation USB offers both writing apps for preview and installs the selected app offline. The installed session starts the selected app with no desktop launcher.

## NordOS layer boundaries

| Layer | Source | Responsibility |
| --- | --- | --- |
| Desktop | `system/desktop` | Present app and drive choices, show consequences, and display progress and recovery actions. |
| System Library | `system/library` | Read app identity and execution metadata and expose installation and power requests to the desktop. |
| System Services | `system/services` | Validate an installation request, apply app selection, start the writing session, and request shutdown. |
| Source and execution adapters | `system/adapters` | Use the Debian package database for installed software and launch native Linux apps through their registered entry points. |
| Platform | `system/platform/linux` | Handle boot media, disk operations, EFI setup, X11 session composition, and logind. The power adapter and its interface come from NordOS foundation revision `d315554`. |
| Applications | `applications` | Register each writing app as an `.app` with a stable identity, publisher, source, and execution environment. |
| Distribution | `distribution`, `overlay` | Choose the platform and packages, stage the shared boot resources, and assemble the installer image. |

Debian package management owns the vendor payloads. The `.app` records under `/Applications` reference those payloads. Per-user app state and documents stay in the writer's home, and the selected app is recorded under `/etc/typewriter`. The app registry and installer interface have no dependency on X11 window-management calls or GRUB. Debian 13, Linux, the display backend, and EFI boot tooling are still required by this build.

To add a writing app, add its trusted package to the distribution build and an `.app` record with a launcher and metadata. Add a GRUB entry if the app should also have its own USB preview. The installer and writing session discover the app from its metadata.

## Build

Use an isolated Debian 13 amd64 VM with at least 4 GB RAM and 12 GB free disk space. Install `debootstrap g++ grub-efi-amd64-bin grub-common xorriso squashfs-tools dosfstools mtools rsync` on the build VM. The script installs the guest dependencies into the staged image.

Create an `inputs` directory. Place the official BYOK Studio 1.3.1 amd64 Debian package in `inputs/BYOK-Studio-linux-amd64.deb`. The vendor download endpoint serves its current release. [BYOK Studio downloads](https://byok.io/studio/desktop)

Place the official Obsidian 1.15.0 amd64 Debian package in `inputs/Obsidian-linux-amd64.deb`. [Obsidian 1.15.0 release](https://github.com/obsidianmd/obsidian-releases/releases/tag/v1.15.0)

Place the Cutefish Toolkit development package from the NordOS build (`6371e1b`) in `inputs/Cutefish-Toolkit-amd64.deb`. Use the locally staged package from the foundation build. See the [NordOS build guide](../../docs/BUILDING.md) for toolkit and build dependencies.

From this directory, verify the release inputs and build the image.

```sh
sha256sum --check distribution/inputs.sha256
sudo ./distribution/build
```

The resulting file is `Typewriter-0.2-amd64.iso`. Test from USB before installing on hardware. The installer erases the entire selected drive.
