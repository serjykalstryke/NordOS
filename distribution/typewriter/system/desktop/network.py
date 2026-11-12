#!/usr/bin/python3
import subprocess
import sys

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gdk, Gio, GLib, Gtk

sys.path.insert(0, "/usr/local/lib/typewriter")
from library.network import NetworkService

SECURITY_NAMES = {
    "open": "Open network",
    "owe": "Enhanced Open",
    "wpa-psk": "Password protected",
    "sae": "WPA3 Personal",
    "unsupported": "Security type unsupported",
}


class NetworkWindow(Gtk.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app, title="Network")
        self.set_type_hint(Gdk.WindowTypeHint.DIALOG)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_default_size(480, 420)
        self.service = NetworkService()
        self.busy = False
        self.signature = None

        header = Gtk.HeaderBar(title="Network", show_close_button=True)
        self.set_titlebar(header)
        body = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12, margin=18)
        self.add(body)
        self.status = Gtk.Label(xalign=0, wrap=True)
        body.pack_start(self.status, False, False, 0)
        self.portal = Gtk.Button(label="Open Network Sign-In")
        self.portal.set_no_show_all(True)
        self.portal.connect("clicked", lambda *_: subprocess.Popen([
            "xdg-open", "http://network-test.debian.org/nm"
        ]))
        body.pack_start(self.portal, False, False, 0)

        controls = Gtk.Box(spacing=8)
        body.pack_start(controls, False, False, 0)
        controls.pack_start(Gtk.Label(label="Wi-Fi", xalign=0), True, True, 0)
        self.switch = Gtk.Switch(valign=Gtk.Align.CENTER)
        self.switch.get_accessible().set_name("Wi-Fi")
        self.switch_handler = self.switch.connect("notify::active", self.toggle)
        controls.pack_start(self.switch, False, False, 0)
        self.rescan = Gtk.Button(label="Refresh")
        self.rescan.connect("clicked", lambda *_: self.service.scan())
        controls.pack_start(self.rescan, False, False, 0)

        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        body.pack_start(scroll, True, True, 0)
        self.rows = Gtk.ListBox(selection_mode=Gtk.SelectionMode.SINGLE)
        self.rows.connect("row-selected", lambda *_: self.update_buttons())
        self.rows.connect("row-activated", lambda *_: self.join())
        scroll.add(self.rows)
        self.placeholder = Gtk.Label(label="Looking for nearby networks…", margin=18, wrap=True)
        self.placeholder.show()
        self.rows.set_placeholder(self.placeholder)

        self.message = Gtk.Label(xalign=0, wrap=True)
        body.pack_start(self.message, False, False, 0)
        buttons = Gtk.ButtonBox(layout_style=Gtk.ButtonBoxStyle.END, spacing=8)
        body.pack_start(buttons, False, False, 0)
        self.forget_button = Gtk.Button(label="Forget Network")
        self.forget_button.connect("clicked", lambda *_: self.forget())
        buttons.add(self.forget_button)
        self.join_button = Gtk.Button(label="Join Network")
        self.join_button.get_style_context().add_class("suggested-action")
        self.join_button.connect("clicked", lambda *_: self.join())
        buttons.add(self.join_button)
        self.show_all()
        self.refresh()
        self.service.scan()
        self.timer = GLib.timeout_add_seconds(2, self.refresh)
        self.connect("destroy", lambda *_: GLib.source_remove(self.timer))

    def selected(self):
        row = self.rows.get_selected_row()
        return row.network if row else None

    def refresh(self):
        status, portal = self.service.status()
        self.status.set_text(status if self.service.available else "Network service unavailable")
        self.portal.set_visible(portal)
        enabled = self.service.wifi_enabled
        self.switch.handler_block(self.switch_handler)
        self.switch.set_active(enabled)
        self.switch.handler_unblock(self.switch_handler)
        devices = self.service.wifi_devices
        self.switch.set_sensitive(bool(devices) and not self.busy)
        self.rescan.set_sensitive(bool(devices) and enabled and not self.busy)
        if not devices:
            self.placeholder.set_text("No Wi-Fi adapter found. A wired connection connects automatically.")
        elif not enabled:
            self.placeholder.set_text("Wi-Fi is off.")
        else:
            self.placeholder.set_text("No nearby Wi-Fi networks yet. Try Refresh.")
        networks = self.service.networks() if enabled else []
        signature = [(n.key, n.connected, bool(n.saved), n.strength // 20) for n in networks]
        if self.signature != signature:
            self.signature = signature
            previous = self.selected()
            for row in self.rows.get_children():
                self.rows.remove(row)
            self.rows.set_placeholder(self.placeholder)
            for network in networks:
                row = Gtk.ListBoxRow()
                row.network = network
                detail = "Connected" if network.connected else SECURITY_NAMES[network.security]
                if network.saved and not network.connected:
                    detail += " · Saved"
                label = Gtk.Label(label=f"{network.name}\n{detail} · {network.strength}%",
                                  xalign=0, wrap=True, margin=9)
                row.add(label)
                self.rows.add(row)
                row.show_all()
                if previous and previous.key == network.key:
                    self.rows.select_row(row)
        self.update_buttons()
        return GLib.SOURCE_CONTINUE

    def update_buttons(self):
        network = self.selected()
        available = bool(network) and not self.busy
        self.join_button.set_sensitive(
            available and not network.connected and network.security != "unsupported"
        )
        self.forget_button.set_sensitive(available and network.saved is not None)

    def toggle(self, switch, *_):
        self.service.set_wifi_enabled(switch.get_active())
        self.service.scan()

    def join(self):
        network = self.selected()
        if self.busy or not network or network.connected or network.security == "unsupported":
            return
        password = None
        if network.needs_password:
            dialog = Gtk.Dialog(title="Wi-Fi password", transient_for=self, modal=True)
            dialog.add_button("Cancel", Gtk.ResponseType.CANCEL)
            dialog.add_button("Join", Gtk.ResponseType.OK)
            dialog.set_default_response(Gtk.ResponseType.OK)
            panel = dialog.get_content_area()
            panel.set_border_width(16)
            panel.set_spacing(8)
            panel.add(Gtk.Label(label=f"Enter the password for {network.name}.", wrap=True))
            entry = Gtk.Entry(visibility=False, activates_default=True,
                              input_purpose=Gtk.InputPurpose.PASSWORD)
            entry.get_accessible().set_name("Wi-Fi password")
            panel.add(entry)
            dialog.show_all()
            entry.grab_focus()
            if dialog.run() == Gtk.ResponseType.OK:
                password = entry.get_text()
            dialog.destroy()
            if not password:
                return
        self.begin(f"Joining {network.name}…")
        self.service.join(network, password, self.finished)

    def forget(self):
        network = self.selected()
        if self.busy or not network or not network.saved:
            return
        self.begin(f"Forgetting {network.name}…")
        self.service.forget(network, self.finished)

    def begin(self, message):
        self.busy = True
        self.message.set_text(message)
        self.update_buttons()

    def finished(self, error):
        self.busy = False
        self.message.set_text(error or "")
        self.refresh()


class NetworkApplication(Gtk.Application):
    def do_activate(self):
        window = self.get_active_window() or NetworkWindow(self)
        window.present()


if __name__ == "__main__":
    app = NetworkApplication(application_id="org.nordos.Typewriter.Network",
                             flags=Gio.ApplicationFlags.FLAGS_NONE)
    sys.exit(app.run())
