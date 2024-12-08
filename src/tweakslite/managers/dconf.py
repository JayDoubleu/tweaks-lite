import gi
import logging

# Get logger for this module
logger = logging.getLogger(__name__)

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gio, GLib
import dbus
from dbus.mainloop.glib import DBusGMainLoop
import json
from ..utils import is_flatpak, run_command

class DConfSettings:
    """Helper class to manage dconf settings"""

    def __init__(self):
        logger.debug("Initializing DConfSettings")
        DBusGMainLoop(set_as_default=True)
        self.settings = {
            "interface": Gio.Settings.new("org.gnome.desktop.interface"),
            "background": Gio.Settings.new("org.gnome.desktop.background"),
            "input-sources": Gio.Settings.new("org.gnome.desktop.input-sources"),
            "wm": Gio.Settings.new("org.gnome.desktop.wm.preferences"),
            "sound": Gio.Settings.new("org.gnome.desktop.sound"),
            "mutter": Gio.Settings.new("org.gnome.mutter"),
        }
        self.dconf = Gio.Settings.new("org.gnome.desktop.interface")
        
        # Setup dbus connection to dconf if not in Flatpak
        if not is_flatpak():
            bus = dbus.SessionBus()
            self.dconf_service = bus.get_object(
                'ca.desrt.dconf', 
                '/ca/desrt/dconf/Writer/user'
            )
            self.dconf_interface = dbus.Interface(
                self.dconf_service,
                dbus_interface='ca.desrt.dconf.Writer'
            )

    def _get_full_key(self, schema, key):
        """Get the full dconf key path"""
        schema_map = {
            "interface": "/org/gnome/desktop/interface/",
            "background": "/org/gnome/desktop/background/",
            "input-sources": "/org/gnome/desktop/input-sources/",
            "wm": "/org/gnome/desktop/wm/preferences/",
            "sound": "/org/gnome/desktop/sound/",
            "mutter": "/org/gnome/mutter/"
        }
        full_key = f"{schema_map[schema]}{key}"
        logger.debug(f"Getting full key path: {full_key}")
        return full_key

    def _set_value_flatpak(self, schema, key, value, value_type):
        """Set a value using dconf command in Flatpak environment"""
        full_key = self._get_full_key(schema, key)
        
        if value_type == "string":
            value = f"'{value}'"  # Wrap strings in quotes
        elif value_type == "boolean":
            value = str(value).lower()
        elif value_type == "double":
            value = str(value)
        elif value_type == "strv":
            value = json.dumps(value)  # Convert list to JSON string
            
        cmd = f"dconf write {full_key} {value}"
        return run_command(cmd, shell=True)

    def get_string(self, schema, key):
        """Get a string value from dconf"""
        return self.settings[schema].get_string(key)

    def set_string(self, schema, key, value):
        """Set a string value in dconf"""
        logger.debug(f"Setting string value - schema: {schema}, key: {key}, value: {value}")
        if is_flatpak():
            self._set_value_flatpak(schema, key, value, "string")
        self.settings[schema].set_string(key, value)

    def get_boolean(self, schema, key):
        """Get a boolean value from dconf"""
        return self.settings[schema].get_boolean(key)

    def set_boolean(self, schema, key, value):
        """Set a boolean value in dconf"""
        if is_flatpak():
            self._set_value_flatpak(schema, key, value, "boolean")
        self.settings[schema].set_boolean(key, value)

    def reset(self, schema, key):
        """Resets a dconf key to its default value"""
        logger.info(f"Resetting dconf key - schema: {schema}, key: {key}")
        try:
            if is_flatpak():
                full_key = self._get_full_key(schema, key)
                run_command(f"dconf reset {full_key}", shell=True)
            self.settings[schema].reset(key)
        except Exception as e:
            logger.error(f"Error resetting {schema} {key}: {e}", exc_info=True)

    def get_default_string(self, schema, key):
        """Get the default string value for a key"""
        value = self.settings[schema].get_default_value(key)
        if value:
            return value.get_string()
        return None

    def get_double(self, schema, key):
        """Get a double value from dconf"""
        return self.settings[schema].get_double(key)

    def get_default_double(self, schema, key):
        """Get the default double value for a key"""
        value = self.settings[schema].get_default_value(key)
        if value:
            return value.get_double()
        return None

    def set_double(self, schema, key, value):
        """Set a double value in dconf"""
        if is_flatpak():
            self._set_value_flatpak(schema, key, value, "double")
        self.settings[schema].set_double(key, value)

    def get_default_boolean(self, schema, key):
        """Get the default boolean value for a key"""
        value = self.settings[schema].get_default_value(key)
        if value:
            return value.get_boolean()
        return None

    def is_value_default(self, schema, key):
        """Check if the current value is the default value"""
        current = self.settings[schema].get_value(key)
        default = self.settings[schema].get_default_value(key)
        if current and default:
            return current.equal(default)
        return False

    def get_available_values(self, schema, key):
        """Get list of available values for an enum key"""
        range_type = self.settings[schema].get_range(key)[0]
        if range_type == "enum":
            return self.settings[schema].get_range(key)[1]
        return None

    def mark_default_in_list(self, values, default_value):
        """Adds '(default)' suffix to the default value in a list"""
        return [f"{v} (default)" if v == default_value else v for v in values]

    def setting_add_to_list(self, schema, key, value):
        """Add a value to a list setting"""
        values = self.settings[schema].get_strv(key)
        if value not in values:
            values.append(value)
            if is_flatpak():
                self._set_value_flatpak(schema, key, values, "strv")
            self.settings[schema].set_strv(key, values)

    def setting_remove_from_list(self, schema, key, value):
        """Remove a value from a list setting"""
        values = self.settings[schema].get_strv(key)
        if value in values:
            values.remove(value)
            if is_flatpak():
                self._set_value_flatpak(schema, key, values, "strv")
            self.settings[schema].set_strv(key, values)

    def get_default_value(self, schema, key):
        """Get the default value for a key"""
        return self.settings[schema].get_default_value(key)
  