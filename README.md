# NordOS

An operating-system project with an attractive default desktop and an integrated conversational assistant—a super-powered Spotlight for finding things, controlling applications, understanding the system, and making changes.

The first-run chat helps users select their initial desktop and software. NordOS recommends its default experience while offering alternatives such as GNOME and KDE Plasma. Everyday use starts in the selected desktop, with a compact assistant that can expand into a full chat window for longer tasks.

The assistant starts with screenshot, keyboard, mouse, and window-control capabilities, then grows direct tools for reading system state and hardware and performing native system actions. Over time, inherited components will be replaced one at a time with NordOS-owned native implementations, keeping a usable system throughout the transition.

## Current foundation

This repository is a fork of **[Cutefish core](https://github.com/cutefishos/cutefish-core)**, renamed NordOS. It currently contains the inherited session and system-services code plus the NordOS project documents. The original component instructions are preserved in [README.Cutefish.md](README.Cutefish.md).

The first-run setup experience, integrated assistant, system-state tools, alternative-desktop integration, and NordOS distribution image are planned work. Their direction is recorded in [docs/VISION.md](docs/VISION.md).

**Source setup status:** 9 component forks are verified. Another 13 components are inventoried and pinned to upstream commits; their forks are pending because GitHub temporarily blocked further repository creation.

## Start here

- [Project vision and incremental replacement strategy](docs/VISION.md)
- [Build baseline and development layout](docs/BUILDING.md)
- [Upstream history and license inventory](docs/UPSTREAM.md)
- [Machine-readable component inventory](components.json)

## Clone this starting point

```sh
git clone https://github.com/serjykalstryke/NordOS.git cutefish-core
git -C cutefish-core remote add upstream https://github.com/cutefishos/cutefish-core.git
```

The checkout name `cutefish-core` preserves the directory layout expected by the existing Cutefish packaging tools. Other components are separate repositories.

## Component collection

The inventory captures the starting commits on 2026-11-04. Forks keep their upstream history and branches. A pending entry links to the original source until its fork can be created.

| Component | Original source | NordOS project fork | GitHub license label |
|---|---|---|---|
| cutefish-core | [upstream](https://github.com/cutefishos/cutefish-core) | [NordOS](https://github.com/serjykalstryke/NordOS) | BSD-3-Clause |
| cutefish-toolkit | [upstream](https://github.com/cutefishos/cutefish-toolkit) | [cutefish-toolkit](https://github.com/serjykalstryke/cutefish-toolkit) | BSD-3-Clause |
| filemanager | [upstream](https://github.com/cutefishos/filemanager) | [filemanager](https://github.com/serjykalstryke/filemanager) | BSD-3-Clause |
| cutefish-compositor | [upstream](https://github.com/cutefishos/cutefish-compositor) | [cutefish-compositor](https://github.com/serjykalstryke/cutefish-compositor) | BSD-3-Clause |
| settings | [upstream](https://github.com/cutefishos/settings) | [settings](https://github.com/serjykalstryke/settings) | BSD-3-Clause |
| wallpapers | [upstream](https://github.com/cutefishos/wallpapers) | Pending GitHub creation limit | NOASSERTION |
| terminal | [upstream](https://github.com/cutefishos/terminal) | [terminal](https://github.com/serjykalstryke/terminal) | GPL-3.0 |
| cutefish-dm | [upstream](https://github.com/cutefishos/cutefish-dm) | [cutefish-dm](https://github.com/serjykalstryke/cutefish-dm) | BSD-3-Clause |
| icons | [upstream](https://github.com/cutefishos/icons) | Pending GitHub creation limit | GPL-3.0 |
| getting-started | [upstream](https://github.com/cutefishos/getting-started) | Pending GitHub creation limit | BSD-3-Clause |
| cutefish-framework | [upstream](https://github.com/cutefishos/cutefish-framework) | [cutefish-framework](https://github.com/serjykalstryke/cutefish-framework) | BSD-3-Clause |
| text-editor | [upstream](https://github.com/cutefishos/text-editor) | Pending GitHub creation limit | BSD-3-Clause |
| qt-plugins | [upstream](https://github.com/cutefishos/qt-plugins) | Pending GitHub creation limit | BSD-3-Clause |
| calculator | [upstream](https://github.com/cutefishos/calculator) | Pending GitHub creation limit | BSD-3-Clause |
| video-player | [upstream](https://github.com/cutefishos/video-player) | Pending GitHub creation limit | BSD-3-Clause |
| plymouth-theme | [upstream](https://github.com/cutefishos/plymouth-theme) | Pending GitHub creation limit | See upstream files |
| cutefish-installer | [upstream](https://github.com/cutefishos/cutefish-installer) | Pending GitHub creation limit | BSD-3-Clause |
| packaging | [upstream](https://github.com/cutefishos/packaging) | Pending GitHub creation limit | See upstream files |
| cutefish-computer-use | [upstream](https://github.com/cutefishos/cutefish-computer-use) | Pending GitHub creation limit | BSD-3-Clause |
| xdg-desktop-portal-cutefish | [upstream](https://github.com/cutefishos/xdg-desktop-portal-cutefish) | [xdg-desktop-portal-cutefish](https://github.com/serjykalstryke/xdg-desktop-portal-cutefish) | BSD-3-Clause |
| system-monitor | [upstream](https://github.com/cutefishos/system-monitor) | Pending GitHub creation limit | BSD-3-Clause |
| calendar | [upstream](https://github.com/cutefishos/calendar) | Pending GitHub creation limit | BSD-3-Clause |

## First implementation direction

1. Reproduce the upstream desktop in a development VM.
2. Prototype a Spotlight-style assistant with an expandable chat window in that desktop.
3. Connect screenshot/input control and add structured system-state and hardware queries.
4. Add useful native system actions and application control with visible results.
5. Build conversational first-run desktop/software selection and test GNOME/KDE alternatives.
6. Replace inherited components progressively while preserving working interfaces.

The existing upstream Debian 13 build path is the initial development baseline. The long-term distribution base, implementation languages, and model providers remain open design decisions.

## Project notes

- [GTK system appearance bridge](examples/gtk-system-style/README.md) is a reversible working prototype that makes GTK 3 and GTK 4/libadwaita apps inherit Cutefish's system appearance. It records the running-app refresh limitation and the path toward native service integration.
- [Snap desktop integration](docs/SNAP_SUPPORT.md) documents the toolkit change for discovering Snap applications, its runtime requirements, and validation steps.
- [MSI Raider audio workaround](https://github.com/serjykalstryke/msi-raider-linux-audio-fix) is a separately verified hardware repair. It is hardware-specific and is not installed globally by this repository.
- This repository retains the upstream core [BSD-3-Clause license](LICENSE). Each other component and its bundled dependencies retains its own license and attribution.
