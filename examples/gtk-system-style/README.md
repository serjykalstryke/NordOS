# GTK inherits the system appearance

This working prototype bridges Cutefish's appearance service to GTK 3 and
GTK 4/libadwaita. It demonstrates a NordOS integration direction: **the system
owns the style; applications receive it without a second theme selection**.

## What it does

`sync.py` reads `org.cutefish.Services.Appearance` and listens for its changes.
It derives GTK user-priority CSS from the system's dark mode, accent index,
font family, and font size. GTK defaults also inherit the system icons, cursor,
window-button placement, and font rendering through Cutefish's existing settings.

The CSS uses Cutefish's native palette, 8/10/14 px corner metrics, rounded
controls, and red/yellow/green window buttons. It translates common application
surfaces: windows, header bars, lists, cards, entries, buttons, switches, menus,
tabs, and selection. GTK 4 receives libadwaita color variables as well as
widget rules; GTK 3 receives named colors and widget rules. The installed core's
header-spacing CSS is included, retaining its sizing work and attribution in
the existing project license. Native colors and window-button measurements
come from the Cutefish toolkit's `theme.cpp`, `theme.h`, `toolkit_colors.cpp`,
and `window_controls.cpp` (BSD-3-Clause).

Ordinary buttons use an 18px content minimum with 6px vertical padding,
giving a 32px target including borders. Header buttons use more compact
padding, alongside the existing native window-control metrics. Application
size requests and expansion still take precedence over these minimums.

## Try it

Run in an ordinary Cutefish Wayland session on Debian 13, as the desktop user:

```sh
# Runtime dependency, if not already installed:
sudo apt install python3-gi

/usr/bin/python3 examples/gtk-system-style/install.py
```

Close and reopen GTK apps. No system library replacement or rebuilding is
required. A user systemd service keeps the generated files synchronized and
starts at login. The installed files are under `$XDG_CONFIG_HOME` (normally
`~/.config`); the original files are backed up under `$XDG_STATE_HOME`
(normally `~/.local/state`). Running the installer again updates the bridge
while preserving the first backup.

If Flatpak is installed, the installer grants applications read-only access
to just the two GTK configuration directories and the bridge directory. The
relative imports work in Flatpak's per-app config mount; application data is
not moved or shared. This also prepares future installations. Flatpak apps
have not been visually verified in the initial desktop trial because none
were installed.

Uninstall and restore the saved configuration:

```sh
/usr/bin/python3 examples/gtk-system-style/install.py --uninstall
```

The installer is also kept with the installed bridge, so removing the checkout
does not remove the undo command:

```sh
/usr/bin/python3 ~/.config/cutefish-gtk-style/install.py --uninstall
```

The installer owns these GTK configuration files while enabled. Uninstall
restores their saved pre-installation versions, including the Flatpak override
file. Backups remain in the state directory. Existing managed symlinks require
manual review before installation.

## Current boundaries

This is a GTK appearance bridge, not a conversion of every application to the
Cutefish toolkit. Custom canvases, web/Electron interfaces, Qt widgets, game
artwork, and application layouts have separate styling mechanisms. GTK rules
can override app styles, so application-specific selectors need ongoing
validation as apps and GTK evolve. It is not an official libadwaita theming API.

The synchronizer updates files automatically when the system appearance
changes. **Already-open apps may need reopening**: GTK 4.18 reads user CSS at
startup and does not provide a general live-reload contract for it. This
prototype never closes apps automatically. Light/dark preference and typography
already have system integration paths, but replacing the complete widget style
has a different lifecycle. Older GTK 4 runtimes without CSS variables are not
covered by this initial implementation.

### Quadrapassel's application layout

Debian 13's Quadrapassel 40.2 explicitly assigns a 30px margin to a play button
that fills two grid rows and uses a dialog-size icon. Those widget properties
cannot be replaced cleanly with a system stylesheet. The separate
[compact control patch](patches/quadrapassel-40.2-compact-controls.patch) changes
the app to center that control, use 12px margins, and use a standard button-size
icon. It applies to the upstream 40.2 source; it is supplied as a source-level
follow-up, has not been compiled or installed in this trial, and does not alter
the game's board or scoring.

The patch contains context from `src/quadrapassel.vala`, copyright 2010–2013
Robert Ancell, licensed GPL-2.0-or-later. Its license is retained in
[`patches/COPYING`](patches/COPYING); the bridge itself follows the core
repository's BSD-3-Clause license.

```sh
# From a Quadrapassel 40.2 source checkout:
git apply /path/to/NordOS/examples/gtk-system-style/patches/quadrapassel-40.2-compact-controls.patch
```

This is an example of an application needing to honor system density in
addition to inheriting system colors and widget styling. Its grid-based side
panel retains the application's own layout.

## Path toward native system inheritance

The source of truth already exists: Cutefish's appearance service and native
toolkit palette. Move this translation into `cutefish-services/appearance`,
alongside `writeGtkSettings()`, rather than shipping another permanent theme
picker. Generate GTK 3 and GTK 4 adapters from shared system appearance tokens
so the system palette, controls, font, and mode stay aligned.

The next step should address running-app refresh through supported GTK
interfaces where available, and retain an explicit restart boundary where
they are not. Package the shared files and narrow Flatpak integration at the
distribution layer. This standalone service is a reversible trial of that
behavior; it is not yet part of the default NordOS build.

## Validation

The initial desktop trial used GTK 3.24.49, GTK 4.18.6, and libadwaita 1.7.6.
Both light and dark generated styles parsed without GTK errors. Mines
(GTK 4/libadwaita) displayed the Cutefish background, typography, rounded cards,
and window buttons. The live mode-change check confirmed regenerated files
and the need to reopen an existing app to refresh the custom palette.

Run the included parser and backup-restore checks:

```sh
# Test-only introspection dependencies, if unavailable:
sudo apt install gir1.2-gtk-3.0 gir1.2-gtk-4.0
/usr/bin/python3 examples/gtk-system-style/check.py
```

Also inspect a representative GTK 3 app, a GTK 4/libadwaita app, menus, checked
and disabled controls, keyboard focus, and the application's own content. Test
light/dark and accent changes, reopen the apps, and inspect Flatpak versions
before enabling the integration in a distribution image.
