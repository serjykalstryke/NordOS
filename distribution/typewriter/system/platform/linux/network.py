from dataclasses import dataclass
from uuid import uuid4

import gi

gi.require_version("NM", "1.0")
from gi.repository import GLib, NM


@dataclass(frozen=True)
class Network:
    name: str
    security: str
    strength: int
    connected: bool
    saved: object
    device: object
    access_point: object

    @property
    def key(self):
        return self.access_point.get_ssid().get_data(), self.security

    @property
    def needs_password(self):
        return self.security in ("wpa-psk", "sae") and self.saved is None


def security_type(ap):
    flags = ap.get_wpa_flags() | ap.get_rsn_flags()
    security = getattr(NM, "80211ApSecurityFlags")
    if flags & security.KEY_MGMT_PSK:
        return "wpa-psk"
    if flags & security.KEY_MGMT_SAE:
        return "sae"
    if flags & (security.KEY_MGMT_OWE | security.KEY_MGMT_OWE_TM):
        return "owe"
    if flags or ap.get_flags() & getattr(NM, "80211ApFlags").PRIVACY:
        return "unsupported"
    return "open"


class NetworkService:
    def __init__(self):
        self.client = NM.Client.new(None)

    @property
    def available(self):
        return self.client.get_nm_running()

    @property
    def wifi_devices(self):
        return [d for d in self.client.get_devices() if isinstance(d, NM.DeviceWifi)]

    @property
    def wifi_enabled(self):
        return self.client.wireless_get_enabled()

    def set_wifi_enabled(self, enabled):
        self.client.wireless_set_enabled(enabled)

    def scan(self):
        if self.wifi_enabled:
            for device in self.wifi_devices:
                device.request_scan_async(None, None, None)

    def status(self):
        connection = self.client.get_primary_connection()
        state = self.client.get_connectivity()
        if state == NM.ConnectivityState.PORTAL:
            return "Network sign-in is required.", True
        if connection:
            if state == NM.ConnectivityState.FULL:
                return f"Online · {connection.get_id()}", False
            return f"Connected to {connection.get_id()} · Internet access unconfirmed", False
        return "Offline", False

    def networks(self):
        unique = {}
        for device in self.wifi_devices:
            current = device.get_active_access_point()
            profiles = device.filter_connections(self.client.get_connections())
            for ap in device.get_access_points():
                ssid = ap.get_ssid()
                if not ssid or not ssid.get_size():
                    continue
                network = Network(
                    name=NM.utils_ssid_to_utf8(ssid.get_data()),
                    security=security_type(ap),
                    strength=ap.get_strength(),
                    connected=current is not None and current.get_path() == ap.get_path(),
                    saved=next((profile for profile in profiles if ap.connection_valid(profile)), None),
                    device=device,
                    access_point=ap,
                )
                other = unique.get(network.key)
                if other is None or (network.connected, network.strength) > (other.connected, other.strength):
                    unique[network.key] = network
        return sorted(unique.values(), key=lambda item: (not item.connected, -item.strength, item.name.casefold()))

    def join(self, network, password, finished):
        device, ap = network.device, network.access_point
        if network.saved:
            def existing(client, result, *_):
                try:
                    active = client.activate_connection_finish(result)
                except GLib.Error as error:
                    finished(error.message)
                    return
                self.wait_for_connection(active, False, finished)
            self.client.activate_connection_async(network.saved, device, ap.get_path(), None, existing, None)
            return

        connection = NM.SimpleConnection.new()
        general = NM.SettingConnection.new()
        general.set_property("id", network.name)
        general.set_property("uuid", str(uuid4()))
        general.set_property("type", "802-11-wireless")
        general.add_permission("user", GLib.get_user_name(), None)
        connection.add_setting(general)
        wireless = NM.SettingWireless.new()
        wireless.set_property("ssid", ap.get_ssid())
        wireless.set_property("mode", "infrastructure")
        connection.add_setting(wireless)
        if network.security != "open":
            setting = NM.SettingWirelessSecurity.new()
            setting.set_property("key-mgmt", network.security)
            if password:
                setting.set_property("psk", password)
            connection.add_setting(setting)

        def added(client, result, *_):
            try:
                active = client.add_and_activate_connection_finish(result)
            except GLib.Error as error:
                finished(error.message)
                return
            self.wait_for_connection(active, True, finished)

        self.client.add_and_activate_connection_async(connection, device, ap.get_path(), None, added, None)

    def wait_for_connection(self, active, is_new, finished):
        def resolve(error, expired=False):
            active.disconnect(handler)
            if not expired:
                GLib.source_remove(timer)
            if error and is_new:
                profile = active.get_connection()
                if profile:
                    profile.delete_async(None, None, None)
            finished(error)

        def state_changed(*_):
            state = active.get_state()
            if state == NM.ActiveConnectionState.ACTIVATED:
                resolve(None)
            elif state == NM.ActiveConnectionState.DEACTIVATED:
                resolve("Check the Wi-Fi password and signal, then try again.")

        def timeout():
            self.client.deactivate_connection_async(active, None, None, None)
            resolve("The network did not respond. Try again closer to the access point.", expired=True)
            return GLib.SOURCE_REMOVE

        handler = active.connect("notify::state", state_changed)
        timer = GLib.timeout_add_seconds(45, timeout)
        state_changed()

    def forget(self, network, finished):
        def removed(profile, result, *_):
            try:
                profile.delete_finish(result)
            except GLib.Error as error:
                finished(error.message)
            else:
                finished(None)
        network.saved.delete_async(None, removed, None)
