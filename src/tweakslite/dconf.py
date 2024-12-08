from gi.repository import Gio, GLib


class DConfSettings:
    """Handles DConf settings"""

    def __init__(self):
        """Initializes DConf settings"""
        self.settings_cache = {}

    def get_settings(self, schema):
        """Gets or creates a settings object for the schema"""
        if schema not in self.settings_cache:
            try:
                if schema.startswith("org.gnome.desktop."):
                    self.settings_cache[schema] = Gio.Settings.new(
                        f"org.gnome.desktop.{schema}"
                    )
                else:
                    self.settings_cache[schema] = Gio.Settings.new(schema)
            except Exception as e:
                print(f"Error creating settings for {schema}: {e}")
                return None
        return self.settings_cache[schema]

    def get_string(self, schema, key):
        """Gets a string value from DConf"""
        settings = self.get_settings(schema)
        if settings:
            return settings.get_string(key)
        return ""

    def set_string(self, schema, key, value):
        """Sets a string value in DConf"""
        settings = self.get_settings(schema)
        if settings:
            settings.set_string(key, value)

    def get_strv(self, schema, key):
        """Gets a string array value from DConf"""
        settings = self.get_settings(schema)
        if settings:
            return settings.get_strv(key)
        return []

    def set_strv(self, schema, key, value):
        """Sets a string array value in DConf"""
        settings = self.get_settings(schema)
        if settings:
            settings.set_strv(key, value)

    def get_boolean(self, schema, key):
        """Gets a boolean value from DConf"""
        settings = self.get_settings(schema)
        if settings:
            return settings.get_boolean(key)
        return False

    def set_boolean(self, schema, key, value):
        """Sets a boolean value in DConf"""
        settings = self.get_settings(schema)
        if settings:
            settings.set_boolean(key, value)

    def get_double(self, schema, key):
        """Gets a double value from DConf"""
        settings = self.get_settings(schema)
        if settings:
            return settings.get_double(key)
        return 0.0

    def set_double(self, schema, key, value):
        """Sets a double value in DConf"""
        settings = self.get_settings(schema)
        if settings:
            settings.set_double(key, value)

    def reset(self, schema, key):
        """Resets a key to its default value"""
        settings = self.get_settings(schema)
        if settings:
            settings.reset(key)
