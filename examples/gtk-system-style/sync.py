#!/usr/bin/python3
# SPDX-License-Identifier: BSD-3-Clause
"""Keep user-priority GTK styling in step with Cutefish's Appearance service."""
import argparse
import configparser
import json
import os
from pathlib import Path

from gi.repository import Gio, GLib

ROOT = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "cutefish-gtk-style"
BUS_NAME = "org.cutefish.Services"
OBJECT = "/org/cutefish/Services/Appearance"
IFACE = "org.cutefish.Services.Appearance"
ACCENTS = ["#3385ff", "#ff5c6d", "#35bf56", "#8266ff", "#ca64ac", "#fea042", "#4f596b"]


def write_changed(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.read_text() == content:
        return
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(content)
    temporary.replace(path)


def palette(dark, accent):
    return dict(zip(
        ("bg", "view", "alt", "text", "muted", "border", "hover", "pressed", "danger"),
        ("#1c1c1d", "#2c2c2d", "#3c3c3d", "#ffffff", "#888888", "rgba(255,255,255,0.12)", "#484849", "#424243", "#ff453a")
        if dark else
        ("#f5f6fa", "#ffffff", "#f2f4f5", "#323238", "#64646e", "rgba(50,50,56,0.08)", "#dcdee0", "#cacccd", "#d92d20")
    ), accent=accent)


COMMON = """
/* These rules sit at GTK's user priority, above application styles. */
window.background, .background { background-color: @cf_bg; color: @cf_text; }
headerbar, .titlebar:not(headerbar), .toolbar, toolbar {
  background-color: @cf_bg; background-image: none; color: @cf_text;
  box-shadow: none; border-color: @cf_border;
}
window.csd, window.csd decoration { border-radius: 14px; }
window.maximized, window.fullscreen, window.tiled,
window.maximized decoration, window.fullscreen decoration { border-radius: 0; }
.view, textview text, treeview.view, iconview.view {
  background-color: @cf_view; color: @cf_text;
}
.sidebar, .navigation-sidebar, placessidebar {
  background-color: @cf_bg; color: @cf_text;
}
list.boxed-list, list.content, .card {
  background-color: @cf_view; color: @cf_text; border-radius: 10px;
  border-color: @cf_border;
}
list.boxed-list > row, list.content > row { border-color: @cf_border; }
row:selected, .navigation-sidebar > row:selected, .sidebar row:selected {
  background-color: alpha(@cf_accent, 0.16); color: @cf_text;
}
selection, .view:selected, treeview.view:selected {
  background-color: @cf_accent; color: white;
}
button {
  background-image: none; background-color: @cf_alt; color: @cf_text;
  border: 1px solid transparent; border-radius: 10px;
  box-shadow: none; text-shadow: none; -gtk-icon-shadow: none;
  min-height: 18px; padding: 6px 12px;
}
/* A normal 16px icon has a 32px target; headers use the native 26px controls. */
button.image-button:not(.titlebutton) { min-width: 18px; padding: 6px; }
headerbar button:not(.titlebutton) { min-height: 18px; padding: 3px 6px; }
/* Adjacent segmented controls share their inner edges. */
.linked > button:not(:only-child) { border-radius: 0; }
.linked > button:first-child { border-top-left-radius: 8px; border-bottom-left-radius: 8px; }
.linked > button:last-child { border-top-right-radius: 8px; border-bottom-right-radius: 8px; }
button:hover { background-color: @cf_hover; }
button:active, button:checked { background-color: @cf_pressed; }
button.flat, .flat > button, headerbar button, toolbar button {
  background-color: transparent; border-color: transparent; box-shadow: none;
}
button.flat:hover, .flat > button:hover, headerbar button:hover, toolbar button:hover {
  background-color: alpha(@cf_text, 0.10);
}
button.flat:checked, .flat > button:checked, headerbar button:checked {
  background-color: alpha(@cf_text, 0.14);
}
button.suggested-action, button.suggested-action:hover,
button.suggested-action:checked, button.suggested-action:active {
  background-color: @cf_accent; color: white; border-color: transparent;
}
button.destructive-action, button.destructive-action:hover,
button.destructive-action:checked, button.destructive-action:active {
  background-color: @cf_danger; color: white; border-color: transparent;
}
button:disabled { color: @cf_muted; }
entry, spinbutton:not(.vertical), searchentry {
  background-color: @cf_view; background-image: none; color: @cf_text;
  border: 1px solid @cf_border; border-radius: 8px; box-shadow: none;
}
entry:focus, entry:focus-within, spinbutton:focus-within {
  border-color: @cf_accent; box-shadow: 0 0 0 2px alpha(@cf_accent, 0.20);
}
entry selection { background-color: @cf_accent; color: white; }
checkbutton check, radiobutton radio {
  background-image: none; background-color: @cf_view;
  color: @cf_text; border: 1px solid alpha(@cf_text, 0.20); box-shadow: none;
}
checkbutton check { border-radius: 5px; }
checkbutton radio, radiobutton radio { border-radius: 50%; }
checkbutton check:checked, checkbutton check:indeterminate,
checkbutton radio:checked, radiobutton radio:checked {
  background-color: @cf_accent; color: white; border-color: @cf_accent;
}
switch {
  background-image: none; background-color: alpha(@cf_text, 0.20);
  border: 1px solid transparent; border-radius: 999px; box-shadow: none;
}
switch:checked { background-color: @cf_accent; }
switch slider {
  background-image: none; background-color: white;
  border: none; border-radius: 999px; box-shadow: 0 1px 3px rgba(0,0,0,0.15);
}
scale trough, progressbar trough {
  background-color: alpha(@cf_text, 0.12); border: none; border-radius: 999px;
}
scale highlight, progressbar progress {
  background-image: none; background-color: @cf_accent; border: none; border-radius: 999px;
}
scale slider { background-image: none; background-color: white; border-color: @cf_border; }
scrollbar slider { background-color: alpha(@cf_text, 0.4); border-radius: 999px; }
notebook > header { background-color: @cf_bg; border-color: @cf_border; }
notebook > header > tabs > tab { border-radius: 8px; border-color: transparent; }
notebook > header > tabs > tab:checked { background-color: @cf_view; box-shadow: none; }
popover > contents, popover.background, menu, .menu, tooltip, tooltip.background {
  background-color: @cf_view; color: @cf_text; background-image: none;
  border: 1px solid @cf_border; border-radius: 10px;
}
popover modelbutton, menu menuitem { border-radius: 6px; }
popover modelbutton:hover, menu menuitem:hover {
  background-color: @cf_accent; color: white;
}
separator { background-color: @cf_border; min-width: 1px; min-height: 1px; }
link, button.link, .accent { color: @cf_accent; }
/* Keep semantic states distinct, even when app palettes differ. */
.error { color: @cf_danger; }
.warning { color: #a86b00; }
"""


GTK4_VARS = """
:root {
  --accent-bg-color: @cf_accent;
  --accent-fg-color: white;
  --accent-color: @cf_accent;
  --window-bg-color: @cf_bg;
  --window-fg-color: @cf_text;
  --view-bg-color: @cf_view;
  --view-fg-color: @cf_text;
  --headerbar-bg-color: @cf_bg;
  --headerbar-fg-color: @cf_text;
  --headerbar-backdrop-color: @cf_bg;
  --headerbar-shade-color: @cf_border;
  --headerbar-darker-shade-color: @cf_border;
  --sidebar-bg-color: @cf_bg;
  --sidebar-fg-color: @cf_text;
  --sidebar-backdrop-color: @cf_bg;
  --sidebar-shade-color: @cf_border;
  --secondary-sidebar-bg-color: @cf_alt;
  --secondary-sidebar-fg-color: @cf_text;
  --secondary-sidebar-backdrop-color: @cf_alt;
  --card-bg-color: @cf_view;
  --card-fg-color: @cf_text;
  --card-shade-color: @cf_border;
  --dialog-bg-color: @cf_bg;
  --dialog-fg-color: @cf_text;
  --popover-bg-color: @cf_view;
  --popover-fg-color: @cf_text;
  --popover-shade-color: @cf_border;
  --thumbnail-bg-color: @cf_alt;
  --thumbnail-fg-color: @cf_text;
  --shade-color: @cf_border;
  --borders: @cf_border;
  --destructive-bg-color: @cf_danger;
  --destructive-fg-color: white;
  --destructive-color: @cf_danger;
}
/* Some apps set a local color scheme. Pin the palette on those surfaces too. */
.background, .sidebar, .navigation-sidebar {
  --window-bg-color: @cf_bg; --window-fg-color: @cf_text;
  --view-bg-color: @cf_view; --view-fg-color: @cf_text;
  --headerbar-bg-color: @cf_bg; --headerbar-fg-color: @cf_text;
  --accent-bg-color: @cf_accent; --accent-fg-color: white; --accent-color: @cf_accent;
}
"""


def controls_css(version):
    base = "headerbar windowcontrols > button" if version == 4 else "headerbar button.titlebutton, .titlebar button.titlebutton"
    selectors = base.split(", ")
    rules = [f"{base} {{ min-width: 26px; min-height: 26px; padding: 0; border: none; border-radius: 0; background-color: transparent; background-size: 26px 26px; background-position: center; background-repeat: no-repeat; box-shadow: none; }}"]
    rules.append(", ".join(s + " > image" for s in selectors) + " { opacity: 0; background-color: transparent; padding: 5px; min-width: 16px; min-height: 16px; }")
    rules.append(", ".join(s + ":hover > image" for s in selectors) + " { opacity: 0.65; color: black; background-color: transparent; }")
    rules.append(", ".join(s + ":active > image" for s in selectors) + " { opacity: 0.8; background-color: transparent; }")
    for action in ("close", "minimize", "maximize"):
        names = ", ".join(s + "." + action for s in selectors)
        rules.append(f'{names} {{ background-image: url("assets/{action}.svg"); }}')
        names = ", ".join(s + "." + action + ":backdrop" for s in selectors)
        rules.append(f'{names} {{ background-image: url("assets/inactive.svg"); }}')
        names = ", ".join(s + "." + action + ":backdrop:hover" for s in selectors)
        rules.append(f'{names} {{ background-image: url("assets/{action}.svg"); }}')
    return "\n".join(rules)


def render(properties, destination=ROOT):
    dark = properties.get("isDarkMode", False)
    index = properties.get("accentColor", 0)
    colors = palette(dark, ACCENTS[index if index in range(len(ACCENTS)) else 0])
    family = properties.get("systemFont", "Inter").replace("\\", "\\\\").replace('"', '\\"')
    size = float(properties.get("systemFontPointSize", 9))
    defines = "\n".join(f"@define-color cf_{key} {value};" for key, value in colors.items())
    # Compatibility names are still used by GTK 3 applications and some GTK 4 apps.
    aliases = {"theme_bg_color": "bg", "theme_fg_color": "text", "theme_base_color": "view",
               "theme_text_color": "text", "theme_selected_bg_color": "accent", "theme_unfocused_bg_color": "bg",
               "theme_unfocused_fg_color": "text", "theme_unfocused_base_color": "view",
               "theme_unfocused_text_color": "text", "insensitive_fg_color": "muted",
               "borders": "border", "accent_bg_color": "accent", "accent_color": "accent",
               "window_bg_color": "bg", "window_fg_color": "text", "view_bg_color": "view",
               "view_fg_color": "text", "headerbar_bg_color": "bg", "headerbar_fg_color": "text",
               "card_bg_color": "view", "card_fg_color": "text", "popover_bg_color": "view",
               "popover_fg_color": "text", "dialog_bg_color": "bg", "dialog_fg_color": "text"}
    defines += "\n" + "\n".join(f"@define-color {name} @cf_{key};" for name, key in aliases.items())
    defines += "\n@define-color theme_selected_fg_color white;\n@define-color accent_fg_color white;\n"
    for version in (3, 4):
        geometry = Path(f"/usr/share/cutefish-services/gtk/gtk-{version}.0.css")
        # Inline upstream's spacing so Flatpak applications don't need host /usr.
        spacing = geometry.read_text() if geometry.exists() else ""
        css = "/* Cutefish GTK integration; generated by cutefish-gtk-style.py. */\n" + defines
        css += GTK4_VARS if version == 4 else ""
        css += f'\nwindow {{ font-family: "{family}"; font-size: {size:g}pt; }}\n'
        css += COMMON + "\n/* Cutefish's installed header metrics. */\n" + spacing
        css += "\n/* Cutefish window controls. */\n" + controls_css(version) + "\n"
        write_changed(destination / f"gtk-{version}.0.css", css)
    for action, color in {"close": "#ee5a6a", "minimize": "#f4b63f", "maximize": "#3cc68a",
                          "inactive": "#686869" if dark else "#c3c3c5"}.items():
        svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="26" height="26" viewBox="0 0 26 26"><circle cx="13" cy="13" r="7" fill="{color}" stroke="#000" stroke-opacity="0.12" stroke-width="0.5"/></svg>\n'
        write_changed(destination / "assets" / f"{action}.svg", svg)
    write_changed(destination / "state.json", json.dumps(properties, indent=2) + "\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--once", action="store_true")
    parser.add_argument("--preview", type=Path)
    parser.add_argument("--dark", action="store_true")
    args = parser.parse_args()
    if args.preview:
        render({"isDarkMode": args.dark, "accentColor": 0, "systemFont": "Inter", "systemFontPointSize": 9}, args.preview)
        return
    bus = Gio.bus_get_sync(Gio.BusType.SESSION, None)

    def sync(*_args):
        try:
            result = bus.call_sync(BUS_NAME, OBJECT, "org.freedesktop.DBus.Properties", "GetAll",
                                   GLib.Variant("(s)", (IFACE,)), GLib.VariantType.new("(a{sv})"),
                                   Gio.DBusCallFlags.NONE, 3000, None)
            properties = result.unpack()[0]
            render(properties)
            # The core may prepend its host-only /usr import at login. Keep the
            # bridge entry points relative so they also resolve in Flatpak.
            for version in (3, 4):
                write_changed(ROOT.parent / f"gtk-{version}.0" / "gtk.css",
                              '/* Follow the Cutefish desktop appearance. */\n'
                              f'@import url("../cutefish-gtk-style/gtk-{version}.0.css");\n')
            # GTK 3 is maintained by cutefish-services; give GTK 4 the same defaults.
            gtk3 = ROOT.parent / "gtk-3.0" / "settings.ini"
            if gtk3.exists():
                cfg = configparser.ConfigParser(interpolation=None)
                cfg.optionxform = str
                cfg.read(gtk3)
                if cfg.has_section("Settings"):
                    # libadwaita obtains light/dark from the appearance portal.
                    cfg.remove_option("Settings", "gtk-application-prefer-dark-theme")
                    import io
                    out = io.StringIO()
                    cfg.write(out, space_around_delimiters=False)
                    write_changed(ROOT.parent / "gtk-4.0" / "settings.ini", out.getvalue())
            print("Cutefish GTK style updated: " + ("dark" if properties.get("isDarkMode") else "light"), flush=True)
        except GLib.Error as error:
            if args.once:
                raise SystemExit(error.message)
            print(f"Waiting for Cutefish appearance: {error.message}", flush=True)
        return GLib.SOURCE_REMOVE

    if args.once:
        sync()
        return

    pending = 0

    def changed(*_args):
        nonlocal pending
        if pending:
            GLib.source_remove(pending)

        def apply():
            nonlocal pending
            pending = 0
            return sync()

        pending = GLib.timeout_add(150, apply)

    bus.signal_subscribe(BUS_NAME, IFACE, None, OBJECT, None, Gio.DBusSignalFlags.NONE, changed)
    bus.signal_subscribe(BUS_NAME, "org.freedesktop.DBus.Properties", "PropertiesChanged", OBJECT,
                         None, Gio.DBusSignalFlags.NONE, changed)
    Gio.bus_watch_name_on_connection(bus, BUS_NAME, Gio.BusNameWatcherFlags.NONE, changed, None)
    sync()
    GLib.MainLoop().run()


if __name__ == "__main__":
    main()
