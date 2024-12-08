from gi.repository import Gtk, Adw
from .base import BaseView

class View(BaseView):
    """View for mouse and touchpad settings"""
    
    def build(self):
        """Builds the mouse settings view"""
        # Mouse settings section
        mouse_group = self.create_section("Mouse")
        
        # Middle Click Paste toggle
        current_paste = self.dconf.get_boolean("interface", "gtk-enable-primary-paste")
        paste_row = Adw.ActionRow(
            title="Middle Click Paste",
            subtitle="Paste text by clicking the middle mouse button",
        )
        paste_switch = Gtk.Switch(active=current_paste, valign=Gtk.Align.CENTER)
        paste_switch.connect("notify::active", self.on_middle_click_paste_changed)
        paste_row.add_suffix(paste_switch)
        mouse_group.add(paste_row)
        
        self.append(mouse_group)
    
    def on_middle_click_paste_changed(self, switch, pspec):
        """Handles changes to middle click paste setting"""
        self.dconf.set_boolean(
            "interface",
            "gtk-enable-primary-paste",
            switch.get_active()
        )
    
    def reset_settings(self):
        """Resets mouse settings to defaults"""
        self.dconf.reset("interface", "gtk-enable-primary-paste")
        
        # Refresh the view
        self.build()