from gi.repository import Gtk, Adw, GLib, Gio
from .base import BaseView

class View(BaseView):
    """View for appearance settings"""
    
    def build(self):
        """Builds the appearance settings view"""
        # Styles section
        self.append(self.create_styles_section())
        
        # Background section
        self.append(self.create_background_section())
    
    def create_styles_section(self):
        """Creates the styles section"""
        styles_group = self.create_section("Styles")
        
        # Icons theme selection
        current_icons = self.dconf.get_string("interface", "icon-theme")
        default_icons = self.dconf.get_default_string("interface", "icon-theme")
        
        # Get available icon themes
        icon_themes = ["Adwaita", "HighContrast", "AdwaitaLegacy", "Hicolor"]
        icon_themes = self.dconf.mark_default_in_list(icon_themes, default_icons)
        
        icons_row = Adw.ComboRow(
            title="Icons",
            model=Gtk.StringList.new(icon_themes)
        )
        
        # Set active option
        for i, theme in enumerate(icon_themes):
            theme_value = theme.replace(" (default)", "")
            if theme_value == current_icons:
                icons_row.set_selected(i)
                break
        
        icons_row.connect(
            "notify::selected",
            self.on_theme_changed,
            "interface",
            "icon-theme"
        )
        styles_group.add(icons_row)
        
        # Legacy Applications (GTK Theme)
        current_theme = self.dconf.get_string("interface", "gtk-theme")
        default_theme = self.dconf.get_default_string("interface", "gtk-theme")
        
        gtk_themes = ["Adwaita", "HighContrastInverse", "Adwaita-dark", "HighContrast"]
        gtk_themes = self.dconf.mark_default_in_list(gtk_themes, default_theme)
        
        legacy_row = Adw.ComboRow(
            title="Legacy Applications",
            model=Gtk.StringList.new(gtk_themes)
        )
        
        for i, theme in enumerate(gtk_themes):
            theme_value = theme.replace(" (default)", "")
            if theme_value == current_theme:
                legacy_row.set_selected(i)
                break
        
        legacy_row.connect(
            "notify::selected",
            self.on_theme_changed,
            "interface",
            "gtk-theme"
        )
        styles_group.add(legacy_row)
        
        return styles_group
    
    def create_background_section(self):
        """Creates the background section"""
        background_group = self.create_section("Background")
        
        # Default Image
        default_uri = self.dconf.get_string("background", "picture-uri") or ""
        default_filename = default_uri.split("/")[-1] if default_uri else "None"
        default_row = Adw.ActionRow(title="Default Image", subtitle=default_filename)
        default_button = Gtk.Button(label=default_filename)
        default_button.add_css_class("flat")
        default_button.set_valign(Gtk.Align.CENTER)
        default_button.connect(
            "clicked",
            self.on_background_clicked,
            "background",
            "picture-uri",
            default_row,
        )
        default_row.add_suffix(default_button)
        background_group.add(default_row)
        
        # Dark Style Image
        dark_uri = self.dconf.get_string("background", "picture-uri-dark") or ""
        dark_filename = dark_uri.split("/")[-1] if dark_uri else "None"
        dark_row = Adw.ActionRow(title="Dark Style Image", subtitle=dark_filename)
        dark_button = Gtk.Button(label=dark_filename)
        dark_button.add_css_class("flat")
        dark_button.set_valign(Gtk.Align.CENTER)
        dark_button.connect(
            "clicked",
            self.on_background_clicked,
            "background",
            "picture-uri-dark",
            dark_row,
        )
        dark_row.add_suffix(dark_button)
        background_group.add(dark_row)
        
        # Adjustment
        current_option = self.dconf.get_string("background", "picture-options")
        default_option = self.dconf.get_default_string("background", "picture-options")
        
        options_map = {
            "none": "None",
            "wallpaper": "Wallpaper",
            "centered": "Centered",
            "scaled": "Scaled",
            "stretched": "Stretched",
            "zoom": "Zoom",
            "spanned": "Spanned",
        }
        
        options = self.dconf.mark_default_in_list(
            list(options_map.values()),
            options_map[default_option]
        )
        
        adjustment_row = Adw.ComboRow(
            title="Adjustment",
            model=Gtk.StringList.new(options)
        )
        
        if current_option in options_map:
            current_label = options_map[current_option]
            for i, option in enumerate(options):
                if option.startswith(current_label):
                    adjustment_row.set_selected(i)
                    break
        
        adjustment_row.connect(
            "notify::selected",
            self.on_background_adjustment_changed,
            options_map
        )
        background_group.add(adjustment_row)
        
        return background_group
    
    def on_theme_changed(self, row, pspec, schema, key):
        """Handles changes to theme selections"""
        selected = row.get_selected()
        selected_text = row.get_model().get_string(selected)
        theme_value = selected_text.replace(" (default)", "")
        self.dconf.set_string(schema, key, theme_value)
    
    def on_background_clicked(self, button, schema, key, row):
        """Opens file chooser for background image selection"""
        dialog = Gtk.FileDialog()
        dialog.set_title("Select Background Image")
        
        filter_images = Gtk.FileFilter()
        filter_images.set_name("Image files")
        filter_images.add_mime_type("image/*")
        filters = Gio.ListStore.new(Gtk.FileFilter)
        filters.append(filter_images)
        dialog.set_filters(filters)
        
        def on_response(dialog, result):
            try:
                file = dialog.open_finish(result)
                if file:
                    uri = file.get_uri()
                    filename = uri.split("/")[-1]
                    self.dconf.set_string(schema, key, uri)
                    button.set_label(filename)
                    row.set_subtitle(filename)
            except GLib.Error as error:
                print(f"Error selecting file: {error.message}")
        
        dialog.open(self.get_root(), None, on_response)
    
    def on_background_adjustment_changed(self, row, pspec, options_map):
        """Handles changes to background adjustment option"""
        selected = row.get_selected()
        selected_text = row.get_model().get_string(selected)
        clean_text = selected_text.replace(" (default)", "")
        for key, value in options_map.items():
            if value == clean_text:
                self.dconf.set_string("background", "picture-options", key)
                break
    
    def reset_settings(self):
        """Resets appearance settings to defaults"""
        self.dconf.reset("interface", "gtk-theme")
        self.dconf.reset("interface", "icon-theme")
        self.dconf.reset("interface", "cursor-theme")
        self.dconf.reset("interface", "color-scheme")
        
        # Refresh the view
        self.build() 