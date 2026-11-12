#!/usr/bin/python3
from pathlib import Path
import subprocess
import sys
import threading

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gdk, GdkPixbuf, GLib, Gtk

sys.path.insert(0, "/usr/local/lib/typewriter")
from library import install_client, session
from library.applications import DEFAULT_APP, applications

LOGO = "/usr/share/plymouth/themes/typewriter/logo.png"
STYLESHEET = Path("/usr/local/share/typewriter/installer.css")


def label(text, style=None, centered=False):
    widget = Gtk.Label(label=text, xalign=0.5 if centered else 0)
    widget.set_line_wrap(True)
    if centered:
        widget.set_justify(Gtk.Justification.CENTER)
    if style:
        widget.get_style_context().add_class(style)
    return widget


class Installer(Gtk.Window):
    def __init__(self):
        super().__init__(title="Install Typewriter")
        self.set_default_size(760, 640)
        self.connect("delete-event", lambda *_: True)
        self.drives = {}
        self.options = {}
        self.busy = False

        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.add(scroll)
        canvas = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        canvas.set_name("canvas")
        scroll.add(canvas)
        body = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        body.set_size_request(480, -1)
        body.set_halign(Gtk.Align.CENTER)
        body.set_valign(Gtk.Align.CENTER)
        canvas.pack_start(body, True, True, 24)

        mark = Gtk.Image.new_from_file(LOGO)
        mark.set_from_pixbuf(mark.get_pixbuf().scale_simple(60, 60, GdkPixbuf.InterpType.BILINEAR))
        body.pack_start(mark, False, False, 0)
        body.pack_start(label("Install Typewriter", "heading", centered=True), False, False, 0)
        self.message = label("Choose a writing app and where to install Typewriter.", "muted", centered=True)
        self.message.set_max_width_chars(56)
        body.pack_start(self.message, False, False, 0)

        self.form = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        body.pack_start(self.form, False, False, 0)
        apps = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.form.pack_start(apps, False, False, 0)
        apps.pack_start(label("Writing app", "section"), False, False, 0)
        apps.pack_start(label("Typewriter opens this app at startup.", "muted"), False, False, 0)
        previous = None
        for app in applications().values():
            option = Gtk.RadioButton.new_with_label_from_widget(previous, app.name)
            option.get_accessible().set_description(app.summary)
            self.options[app.id] = (option, app)
            previous = option
            row = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=3)
            row.get_style_context().add_class("app-choice")
            row.pack_start(option, False, False, 0)
            summary = label(app.summary, "muted")
            summary.set_margin_start(26)
            row.pack_start(summary, False, False, 0)
            apps.pack_start(row, False, False, 0)
        if DEFAULT_APP in self.options:
            self.options[DEFAULT_APP][0].set_active(True)

        drive_section = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.form.pack_start(drive_section, False, False, 0)
        drive_label = label("Installation drive", "section")
        self.choices = Gtk.ComboBoxText()
        self.choices.get_accessible().set_name("Installation drive")
        self.choices.connect("changed", self.selection_changed)
        drive_section.pack_start(drive_label, False, False, 0)
        drive_section.pack_start(self.choices, False, False, 0)
        drive_section.pack_start(
            label("Installation erases everything on the selected drive.", "warning"), False, False, 0
        )

        buttons = Gtk.Box(spacing=8)
        buttons.set_halign(Gtk.Align.CENTER)
        body.pack_start(buttons, False, False, 0)
        self.shutdown = Gtk.Button.new_with_label("Shut Down")
        self.shutdown.connect("clicked", self.power)
        buttons.pack_start(self.shutdown, False, False, 0)
        self.refresh_button = Gtk.Button.new_with_label("Refresh Drives")
        self.refresh_button.connect("clicked", lambda *_: self.refresh())
        buttons.pack_start(self.refresh_button, False, False, 0)
        self.continue_button = Gtk.Button.new_with_label("Continue")
        self.continue_button.get_style_context().add_class("suggested-action")
        self.continue_button.connect("clicked", lambda *_: self.confirm())
        buttons.pack_start(self.continue_button, False, False, 0)

        self.progress = Gtk.ProgressBar()
        body.pack_start(self.progress, False, False, 0)
        css = Gtk.CssProvider()
        css.load_from_path(str(STYLESHEET))
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(), css, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
        self.show_all()
        self.progress.hide()
        self.refresh()

    def refresh(self):
        previous = self.choices.get_active_id()
        self.choices.remove_all()
        self.drives = {}
        try:
            self.drives = install_client.drives()
        except (OSError, RuntimeError, subprocess.CalledProcessError):
            self.message.set_text("The installer could not identify its boot drive. Restart from the installation USB.")
        else:
            if self.drives:
                self.message.set_text("Choose a writing app and where to install Typewriter.")
                for path, drive in self.drives.items():
                    self.choices.append(path, install_client.drive_label(drive))
                if not self.choices.set_active_id(previous or ""):
                    self.choices.set_active(0)
            else:
                self.message.set_text("No available drive found. Connect a drive of at least 9 GB, then refresh.")
        self.selection_changed()

    def selection_changed(self, *_):
        self.continue_button.set_sensitive(bool(self.options and self.choices.get_active_id()))

    def confirm(self):
        drive = self.drives.get(self.choices.get_active_id())
        app = next((app for option, app in self.options.values() if option.get_active()), None)
        if drive is None or app is None:
            return

        dialog = Gtk.Dialog(title="Erase the selected drive?", transient_for=self, modal=True)
        dialog.set_decorated(False)
        dialog.add_button("Cancel", Gtk.ResponseType.CANCEL)
        erase = dialog.add_button("Erase and Install", Gtk.ResponseType.OK)
        erase.get_style_context().add_class("destructive-action")
        erase.set_sensitive(False)
        panel = dialog.get_content_area()
        panel.set_border_width(20)
        panel.set_spacing(10)
        panel.pack_start(label("Erase the selected drive?", "section"), False, False, 0)
        panel.pack_start(label(install_client.drive_label(drive)), False, False, 0)
        panel.pack_start(label(f"Writing app · {app.name}"), False, False, 0)
        panel.pack_start(label("All data on this drive will be erased.", "warning"), False, False, 0)
        panel.pack_start(label("Type ERASE to continue."), False, False, 0)
        entry = Gtk.Entry()
        entry.get_accessible().set_name("Type ERASE to continue")
        entry.set_activates_default(True)
        entry.connect("changed", lambda widget: erase.set_sensitive(widget.get_text() == "ERASE"))
        panel.pack_start(entry, False, False, 0)
        dialog.set_default_response(Gtk.ResponseType.OK)
        dialog.show_all()
        entry.grab_focus()
        confirmed = dialog.run() == Gtk.ResponseType.OK and entry.get_text() == "ERASE"
        dialog.destroy()
        if confirmed:
            self.start(drive, app)

    def start(self, drive, app):
        for widget in (self.shutdown, self.refresh_button, self.continue_button):
            widget.set_sensitive(False)
        self.form.hide()
        self.message.set_text(f"Starting installation with {app.name}…")
        self.progress.show()
        self.busy = True
        GLib.timeout_add(90, self.pulse)
        threading.Thread(target=self.run_install, args=(drive, app), daemon=True).start()

    def pulse(self):
        if self.busy:
            self.progress.pulse()
        return self.busy

    def run_install(self, drive, app):
        def update(message):
            GLib.idle_add(self.message.set_text, message)

        code, details = install_client.install(drive, app, update)
        GLib.idle_add(self.finish, app, code, details)

    def finish(self, app, code, details):
        self.busy = False
        self.shutdown.set_sensitive(True)
        if code:
            self.progress.hide()
            self.form.show()
            self.refresh_button.set_sensitive(True)
            self.refresh()
            self.show_error("Installation stopped", "Review the details before trying again.\n\n" + details)
        else:
            self.progress.set_fraction(1)
            self.refresh_button.hide()
            self.continue_button.hide()
            self.message.set_text(
                f"{app.name} is ready. Shut down, remove the installation USB, then restart your system. "
                "Press Ctrl+Alt+W after startup to connect to Wi-Fi."
            )
        return False

    def show_error(self, title, details):
        dialog = Gtk.MessageDialog(
            transient_for=self, modal=True, message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.CLOSE, text=title,
        )
        dialog.format_secondary_text(details)
        dialog.run()
        dialog.destroy()

    def power(self, *_):
        try:
            session.power_off()
        except (OSError, subprocess.CalledProcessError):
            self.show_error("Shutdown could not start", "Try Shut Down again.")


if __name__ == "__main__":
    Installer()
    Gtk.main()
