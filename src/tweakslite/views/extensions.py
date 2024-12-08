import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, Gio, GLib
import sys
import os
import json
import dbus

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from tweakslite.views.base import BaseView
from tweakslite.utils import is_flatpak, run_command


class ExtensionState:
    """Enum-like class defining possible states of GNOME Shell extensions"""

    ENABLED = 1
    DISABLED = 2
    ERROR = 3
    OUT_OF_DATE = 4
    DOWNLOADING = 5
    INITIALIZED = 6
    UNINSTALLED = 7


class View(BaseView):
    """View for managing GNOME Shell extensions"""

    def __init__(self, dconf, autostart_manager):
        # Initialize properties before parent class to avoid attribute errors
        self.extensions = {}  # Dictionary to store extension metadata
        self.proxy = None  # D-Bus proxy for communicating with GNOME Shell

        # Initialize base class after properties are set
        super().__init__(dconf, autostart_manager)

        # Load extensions after view is built
        self.load_extensions()

    def _get_extensions_flatpak(self):
        """Get extensions list using dbus-python in Flatpak environment"""
        try:
            # Connect to the session bus
            bus = dbus.SessionBus()

            # Get the GNOME Shell object
            shell_object = bus.get_object("org.gnome.Shell", "/org/gnome/Shell")

            # Get the extensions interface
            extensions_iface = dbus.Interface(
                shell_object, "org.gnome.Shell.Extensions"
            )

            # Call ListExtensions method
            raw_extensions = extensions_iface.ListExtensions()

            # Convert dbus types to Python native types
            extensions = {}
            for uuid, ext_data in raw_extensions.items():
                # Convert D-Bus types to Python native types
                ext_dict = {}
                for key, value in ext_data.items():
                    if isinstance(value, dbus.Boolean):
                        ext_dict[key] = bool(value)
                    elif isinstance(value, dbus.Int32) or isinstance(value, dbus.Int64):
                        ext_dict[key] = int(value)
                    elif isinstance(value, dbus.Double):
                        ext_dict[key] = float(value)
                    else:
                        ext_dict[key] = str(value)
                extensions[str(uuid)] = ext_dict

            print(f"Found {len(extensions)} extensions")
            return extensions

        except Exception as e:
            print(f"Error getting extensions via D-Bus: {e}")
            return {}

    def _toggle_extension_flatpak(self, uuid, enable):
        """Toggle extension state using dbus-python in Flatpak environment"""
        try:
            bus = dbus.SessionBus()
            shell_object = bus.get_object("org.gnome.Shell", "/org/gnome/Shell")
            extensions_iface = dbus.Interface(
                shell_object, "org.gnome.Shell.Extensions"
            )

            if enable:
                extensions_iface.EnableExtension(uuid)
            else:
                extensions_iface.DisableExtension(uuid)
            return True
        except Exception as e:
            print(f"Error toggling extension {uuid}: {e}")
            return False

    def _open_prefs_flatpak(self, uuid):
        """Open extension preferences using dbus-python in Flatpak environment"""
        try:
            bus = dbus.SessionBus()
            shell_object = bus.get_object("org.gnome.Shell", "/org/gnome/Shell")
            extensions_iface = dbus.Interface(
                shell_object, "org.gnome.Shell.Extensions"
            )

            extensions_iface.LaunchExtensionPrefs(uuid)
            return True
        except Exception as e:
            print(f"Error opening preferences for {uuid}: {e}")
            return False

    def load_extensions(self):
        """Loads installed GNOME Shell extensions via D-Bus"""
        try:
            print("Starting to load extensions...")

            # Get list of currently enabled extensions from dconf
            settings = Gio.Settings.new("org.gnome.shell")
            enabled_extensions = settings.get_strv("enabled-extensions")

            if is_flatpak():
                shell_extensions = self._get_extensions_flatpak()
            else:
                # Connect to GNOME Shell extensions interface via D-Bus
                self.proxy = Gio.DBusProxy.new_for_bus_sync(
                    Gio.BusType.SESSION,
                    Gio.DBusProxyFlags.NONE,
                    None,
                    "org.gnome.Shell",
                    "/org/gnome/Shell",
                    "org.gnome.Shell.Extensions",
                    None,
                )

                # Get all installed extensions from GNOME Shell
                result = self.proxy.call_sync(
                    "ListExtensions", None, Gio.DBusCallFlags.NONE, -1, None
                )

                if result:
                    shell_extensions = result.unpack()[0]
                else:
                    shell_extensions = {}

            # Process each extension and store its metadata
            for uuid, data in shell_extensions.items():
                ext_data = {
                    "uuid": uuid,
                    "name": data.get(
                        "name", uuid.split("@")[0].replace("-", " ").title()
                    ),
                    "description": data.get("description", "").split("\n")[0],
                    "state": ExtensionState.ENABLED
                    if uuid in enabled_extensions
                    else ExtensionState.DISABLED,
                    "version": str(data.get("version", "")),
                    "type": data.get("type", 0),
                    "path": data.get("path", ""),
                    "hasPrefs": data.get("hasPrefs", False),
                    "enabled": data.get("enabled", False),
                    "canChange": data.get("canChange", True),
                    "error": data.get("error", ""),
                }
                self.extensions[uuid] = ext_data

            # Schedule view update on the main thread
            GLib.idle_add(self.update_view)

        except Exception as e:
            print(f"Error loading extensions: {e}")
            self.extensions = {}
            GLib.idle_add(self.build)

    def update_view(self):
        """Updates the view with loaded extensions data"""
        # Clear existing content
        while True:
            child = self.content_box.get_first_child()
            if child is None:
                break
            self.content_box.remove(child)

        # Rebuild the view with current data
        self.build()
        return False

    def _toggle_global_extensions_flatpak(self, enable):
        """Toggle global extensions state using dbus-python in Flatpak environment"""
        try:
            bus = dbus.SessionBus()
            shell_object = bus.get_object("org.gnome.Shell", "/org/gnome/Shell")
            extensions_iface = dbus.Interface(
                shell_object, "org.gnome.Shell.Extensions"
            )

            # Get all extensions
            extensions = extensions_iface.ListExtensions()

            # Toggle each extension
            for uuid in extensions:
                if enable:
                    try:
                        extensions_iface.EnableExtension(str(uuid))
                    except:
                        pass  # Skip if extension can't be enabled
                else:
                    try:
                        extensions_iface.DisableExtension(str(uuid))
                    except:
                        pass  # Skip if extension can't be disabled

            # Update dconf setting
            settings = Gio.Settings.new("org.gnome.shell")
            settings.set_boolean("disable-user-extensions", not enable)
            return True
        except Exception as e:
            print(f"Error toggling global extensions state: {e}")
            return False

    def build(self):
        """Builds the extensions view interface"""
        # Create global switch section for enabling/disabling all extensions
        global_group = self.create_section()

        # Add global switch for all extensions
        global_switch_row = Adw.ActionRow(
            title="User Extensions",
            subtitle="Enable or disable all user extensions",
            css_classes=["global-switch-row"],
        )

        # Get current global state from dconf
        settings = Gio.Settings.new("org.gnome.shell")
        global_state = not settings.get_boolean("disable-user-extensions")

        global_switch = Gtk.Switch(valign=Gtk.Align.CENTER, active=global_state)

        def on_global_switch_changed(switch, *args):
            """Handles toggling all extensions on/off"""
            try:
                enable = switch.get_active()
                success = False

                if is_flatpak():
                    success = self._toggle_global_extensions_flatpak(enable)
                else:
                    settings = Gio.Settings.new("org.gnome.shell")
                    settings.set_boolean("disable-user-extensions", not enable)
                    success = True

                if success:
                    # Update all individual extension switches to match global state
                    for row in extensions_group:
                        if isinstance(row, Adw.ExpanderRow):
                            for child in row:
                                if isinstance(child, Gtk.Switch):
                                    child.set_active(enable)
                else:
                    # Revert switch state if operation failed
                    switch.set_active(not enable)

            except Exception as e:
                print(f"Error toggling global extensions state: {e}")
                switch.set_active(not switch.get_active())

        global_switch.connect("notify::active", on_global_switch_changed)
        global_switch_row.add_suffix(global_switch)
        global_group.add(global_switch_row)

        self.append(global_group)

        # Add visual separator between global switch and extensions list
        separator = Gtk.Separator(
            orientation=Gtk.Orientation.HORIZONTAL, margin_top=12, margin_bottom=12
        )
        self.append(separator)

        # Create main extensions list section
        extensions_group = self.create_section("Installed Extensions")

        if not self.extensions:
            # Show empty state message
            status_row = Adw.ActionRow(
                title="No extensions found",
                subtitle="Install GNOME Shell extensions to see them here",
            )
            extensions_group.add(status_row)
        else:
            # Sort extensions alphabetically by name
            sorted_extensions = sorted(
                self.extensions.items(), key=lambda x: x[1]["name"].lower()
            )

            # Add each extension to the list
            for uuid, extension in sorted_extensions:
                # Create expandable row for extension details
                row = Adw.ExpanderRow(
                    title=extension["name"],
                    subtitle=extension.get("description", ""),
                    css_classes=["extension-row"],
                )

                # Add version and UUID info if version is available
                if extension.get("version"):
                    version = Adw.ActionRow(
                        title="Version", subtitle=extension["version"]
                    )
                    row.add_row(version)

                    uuid_row = Adw.ActionRow(title="UUID", subtitle=uuid)
                    row.add_row(uuid_row)

                # Add enable/disable switch for this extension
                switch = Gtk.Switch(
                    active=extension["state"] == ExtensionState.ENABLED,
                    valign=Gtk.Align.CENTER,
                )

                def on_switch_changed(switch, *args, ext_uuid=uuid):
                    """Handles toggling individual extension state"""
                    try:
                        settings = Gio.Settings.new("org.gnome.shell")
                        enabled_extensions = settings.get_strv("enabled-extensions")

                        if switch.get_active():
                            # Enable the extension
                            if ext_uuid not in enabled_extensions:
                                enabled_extensions.append(ext_uuid)
                                if is_flatpak():
                                    self._toggle_extension_flatpak(ext_uuid, True)
                                else:
                                    self.proxy.call_sync(
                                        "EnableExtension",
                                        GLib.Variant("(s)", (ext_uuid,)),
                                        Gio.DBusCallFlags.NONE,
                                        -1,
                                        None,
                                    )
                        else:
                            # Disable the extension
                            if ext_uuid in enabled_extensions:
                                enabled_extensions.remove(ext_uuid)
                                if is_flatpak():
                                    self._toggle_extension_flatpak(ext_uuid, False)
                                else:
                                    self.proxy.call_sync(
                                        "DisableExtension",
                                        GLib.Variant("(s)", (ext_uuid,)),
                                        Gio.DBusCallFlags.NONE,
                                        -1,
                                        None,
                                    )

                        # Update enabled extensions list in dconf
                        settings.set_strv("enabled-extensions", enabled_extensions)

                    except Exception as e:
                        print(f"Error toggling extension {ext_uuid}: {e}")
                        switch.set_active(not switch.get_active())

                switch.connect("notify::active", on_switch_changed)
                row.add_suffix(switch)

                # Add preferences button if extension has preferences
                if extension.get("hasPrefs"):
                    prefs_button = Gtk.Button(
                        icon_name="preferences-system-symbolic",
                        valign=Gtk.Align.CENTER,
                        css_classes=["flat"],
                    )

                    def on_prefs_clicked(button, ext_uuid=uuid):
                        """Opens extension preferences dialog"""
                        if is_flatpak():
                            self._open_prefs_flatpak(ext_uuid)
                        else:
                            self.proxy.call_sync(
                                "OpenExtensionPrefs",
                                GLib.Variant("(ssa{sv})", (ext_uuid, "", {})),
                                Gio.DBusCallFlags.NONE,
                                -1,
                                None,
                            )

                    prefs_button.connect("clicked", on_prefs_clicked)
                    row.add_suffix(prefs_button)

                extensions_group.add(row)

        self.append(extensions_group)

    def reset_settings(self):
        """Resets all extension settings to their default values"""
        try:
            # Reset global user extensions state
            settings = Gio.Settings.new("org.gnome.shell")
            settings.reset("disable-user-extensions")

            # Reset enabled extensions list
            settings.reset("enabled-extensions")

            # Reload extensions and rebuild view
            self.extensions = {}
            self.load_extensions()
        except Exception as e:
            print(f"Error resetting extension settings: {e}")
