# NordOS system baseline

**Status update, November 10, 2026.** This page records a package-selection experiment. The current task is sorting existing code and system responsibilities into the [NordOS system architecture](SYSTEM_ARCHITECTURE.md). The package profile does not implement that structure and is not the next development milestone.

The first NordOS system profile uses the Cutefish toolkit and the components needed for a usable graphical session. The toolkit provides the starting point for interface development. The rest of the Cutefish session provides working implementations while NordOS develops its own system structure and behavior.

The [`nordos-desktop` package](../packaging/nordos-desktop/DEBIAN/control) selects the baseline on Debian 13. Debian supplies the Linux kernel, drivers, system services, and base system. The package uses the existing **Cutefish (Wayland)** login entry and expects a display manager that can launch it. The future image can select its own login manager and boot assets.

| Part of the baseline | Packages | What they provide |
|---|---|---|
| Toolkit and shared clients | `cutefish-toolkit`, `cutefish-framework` | Rendering, controls, and access to services such as audio, networking, and power |
| Session and system integration | `cutefish-core`, `xdg-desktop-portal-cutefish` | Session startup, application launch, authorization prompts, and desktop portals |
| Desktop surface | `cutefish-compositor`, `cutefish-filemanager` | Windows, launcher, dock, lock screen, desktop, and file browsing. The session starts File Manager to provide the desktop surface. |
| Settings and assets | `cutefish-settings`, `cutefish-icon-theme`, `cutefish-wallpapers` | Graphical system controls, icons, and wallpaper resources required by Settings |

Calculator, Calendar, System Monitor, Text Editor, Video Player, Terminal, and App Center are separate application choices. Qt integration, WebKit, and computer-use tooling can be added when a workload needs them. The display manager, installer, and boot artwork belong to the image configuration. The baseline profile selects its dependencies directly, so the full `cutefish-desktop` suite and its Firefox policy stay outside the installation.

## Where NordOS development starts

Keep the current session working as its responsibilities become explicit. The core starts the session and provides services, the compositor provides the graphical shell, and File Manager currently provides both desktop and browsing functions. A future NordOS desktop can replace those parts independently once it provides the behaviors their callers need.

Use the design bible to define the new system interfaces. The first boundary is between platform services, the desktop experience, and application management. The desktop should work for ordinary file, window, and settings tasks without depending on an AI interaction. A shared application service can then expose installed applications to the launcher, File Manager, and App Center while preserving their sources. Native `.app` packaging and compatibility environments can build on that foundation in later work.

## Build the profile package

Run these commands from the NordOS repository on Debian. They build the package and show what APT would install.

```sh
dpkg-deb --root-owner-group --build packaging/nordos-desktop /tmp/nordos-desktop_0.1.0_all.deb
dpkg-deb --info /tmp/nordos-desktop_0.1.0_all.deb
apt-get --simulate install /tmp/nordos-desktop_0.1.0_all.deb
```

For the first VM test, start with Debian 13, a Wayland-capable login manager, and a package source containing a coherent set of the selected Cutefish packages. Check login, logout, desktop rendering, file browsing, Settings, network, audio, locking, and portal file selection. A NordOS image build will need pinned component sources and its own package and image configuration. See [the initial release plan](INITIAL_RELEASE.md).
