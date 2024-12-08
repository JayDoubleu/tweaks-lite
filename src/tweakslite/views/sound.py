from gi.repository import Gtk, Adw
from .base import BaseView


class View(BaseView):
    """View for sound settings"""

    def build(self):
        """Builds the sound settings view"""
        # System Sound Theme section
        theme_group = self.create_section("System Sound Theme")

        # Theme selector row
        theme_row = Adw.ActionRow(title="System Sound Theme", subtitle="Default")
        theme_button = Gtk.Button(label="Default")
        theme_button.add_css_class("flat")
        theme_button.set_valign(Gtk.Align.CENTER)
        theme_row.add_suffix(theme_button)
        theme_group.add(theme_row)

        self.append(theme_group)

    def reset_settings(self):
        """Resets sound settings to defaults"""
        self.dconf.reset("sound", "theme-name")
        self.dconf.reset("sound", "event-sounds")

        # Refresh the view
        self.build()
