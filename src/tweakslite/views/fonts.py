from gi.repository import Gtk, Adw, GLib, Pango
from .base import BaseView

class View(BaseView):
    """View for font settings"""
    
    def build(self):
        """Builds the fonts settings view"""
        # Preferred Fonts section
        preferred_group = self.create_section("Preferred Fonts")
        
        # Get available fonts
        fonts = self.get_system_fonts()
        font_model = Gtk.StringList.new(fonts)
        
        # Create font rows with size selectors
        font_configs = [
            ("Interface Text", "font-name", "Used for application interface elements"),
            ("Document Text", "document-font-name", "Used for reading documents and web pages"),
            ("Monospace Text", "monospace-font-name", "Used for code and terminal text")
        ]
        
        def create_font_section(title, schema_key, subtitle):
            """Creates a font section with its own state"""
            # Create main row
            row = Adw.ActionRow(
                title=title,
                subtitle=subtitle,
                activatable=True,
                can_focus=False
            )
            
            # Add arrow indicator
            arrow = Gtk.Image.new_from_icon_name("go-next-symbolic")
            arrow.add_css_class("dim-label")
            row.add_suffix(arrow)
            
            def on_row_activated(row):
                window = self.get_root()
                if isinstance(window, Adw.ApplicationWindow):
                    navigation_view = window.get_content().get_child().get_content().get_child()
                    
                    if isinstance(navigation_view, Adw.NavigationView):
                        # Create a new page
                        page = Adw.NavigationPage(
                            title=f"Select {title} Font",
                            can_focus=False
                        )
                        
                        # Create the content after the page is shown
                        def on_page_shown(page):
                            if not page.get_child():
                                # Create the content
                                content = create_font_content(window, navigation_view, schema_key, row)
                                page.set_child(content)
                                # Ensure no focus
                                window.set_focus(None)
                        
                        def on_page_hidden(page):
                            # Clear focus when page is hidden
                            window.set_focus(None)
                            # Remove the content to prevent focus issues
                            page.set_child(None)
                        
                        # Connect to signals
                        page.connect("map", on_page_shown)
                        page.connect("unmap", on_page_hidden)
                        
                        # Push the page
                        navigation_view.push(page)
            
            click = Gtk.GestureClick()
            click.connect("released", lambda g, n, x, y: on_row_activated(row))
            row.add_controller(click)
            return row
        
        def create_font_content(window, navigation_view, schema_key, original_row):
            """Creates the font selection content"""
            toolbar_view = Adw.ToolbarView()
            
            # Add header bar
            header = Adw.HeaderBar(
                show_title=False,
                show_end_title_buttons=False,
                decoration_layout=""
            )
            
            # Add back button
            back_button = Gtk.Button(label="Cancel")
            back_button.add_css_class("flat")
            back_button.connect("clicked", lambda b: navigation_view.pop())
            header.pack_start(back_button)
            
            # Add apply button
            apply_button = Gtk.Button(label="Select")
            apply_button.add_css_class("suggested-action")
            header.pack_end(apply_button)
            
            toolbar_view.add_top_bar(header)
            
            # Create content box
            content_box = Gtk.Box(
                orientation=Gtk.Orientation.VERTICAL,
                spacing=18,
                margin_start=18,
                margin_end=18,
                margin_top=12,
                margin_bottom=12
            )
            
            # Create size selector group
            size_group = Adw.PreferencesGroup(
                margin_bottom=12
            )
            
            # Add size controls
            size_row = Adw.ActionRow(
                title="Font Size",
                subtitle="Adjust the size of the font"
            )
            
            size_box = Gtk.Box(
                orientation=Gtk.Orientation.HORIZONTAL,
                spacing=12,
                valign=Gtk.Align.CENTER,
                margin_start=6,
                margin_end=6
            )
            
            # Get current font and size
            current_font = self.dconf.get_string("interface", schema_key)
            current_size = 11
            font_name = current_font
            if " " in current_font:
                font_name, size_str = current_font.rsplit(" ", 1)
                if size_str.isdigit():
                    current_size = int(size_str)
            
            minus_button = Gtk.Button(
                icon_name="list-remove-symbolic",
                css_classes=["flat", "circular"]
            )
            
            size_label = Gtk.Label(
                label=str(current_size),
                css_classes=["numeric", "heading", "monospace"],
                margin_start=12,
                margin_end=12,
                width_chars=2
            )
            
            plus_button = Gtk.Button(
                icon_name="list-add-symbolic",
                css_classes=["flat", "circular"]
            )
            
            size_box.append(minus_button)
            size_box.append(size_label)
            size_box.append(plus_button)
            size_row.add_suffix(size_box)
            size_group.add(size_row)
            content_box.append(size_group)
            
            # Create font list group
            font_group = Adw.PreferencesGroup(
                margin_bottom=12,
                css_classes=["boxed-list"]
            )
            
            # Create radio button group
            first_radio = None
            
            # Create a variable to track the currently selected font
            selected_font_row = None
            
            for font in fonts:
                # Create row with font preview
                row = Adw.ActionRow(
                    activatable=True,
                    css_classes=["font-row"],
                    margin_top=2,
                    margin_bottom=2
                )
                
                # Create a vertical box for labels
                label_box = Gtk.Box(
                    orientation=Gtk.Orientation.VERTICAL,
                    spacing=3,
                    hexpand=True,
                    margin_start=12,
                    margin_end=12
                )
                
                # Create title label with system font
                title_label = Gtk.Label(
                    label=font,
                    halign=Gtk.Align.START,
                    hexpand=True,
                    xalign=0
                )
                title_label.add_css_class("title")
                
                # Create subtitle label with the specific font
                subtitle_label = Gtk.Label(
                    label="The quick brown fox jumps over the lazy dog",
                    halign=Gtk.Align.START,
                    hexpand=True,
                    wrap=True,
                    xalign=0,
                    max_width_chars=40
                )
                subtitle_label.add_css_class("subtitle")
                
                # Style the labels
                css_provider = Gtk.CssProvider()
                css_provider.load_from_data(f"""
                    label.title {{
                        font-size: 14px;
                        font-weight: 500;
                        margin-bottom: 2px;
                    }}
                    label.subtitle {{
                        font-family: "{font}";
                        font-size: 13px;
                        opacity: 0.7;
                        padding: 2px 0;
                    }}
                    row.font-row.selected {{
                        background-color: alpha(@accent_bg_color, 0.15);
                        border-left: 3px solid @accent_bg_color;
                    }}
                """.encode())
                
                title_label.get_style_context().add_provider(css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
                subtitle_label.get_style_context().add_provider(css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
                row.get_style_context().add_provider(css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
                
                label_box.append(title_label)
                label_box.append(subtitle_label)
                
                # Add radio button
                radio = Gtk.CheckButton(
                    valign=Gtk.Align.CENTER,
                    can_focus=False
                )
                if first_radio:
                    radio.set_group(first_radio)
                else:
                    first_radio = radio
                
                if font == font_name:
                    radio.set_active(True)
                    selected_font_row = row
                    row.add_css_class("selected")
                
                row.set_child(label_box)
                row.add_suffix(radio)
                row.radio = radio
                row.font_name = font
                
                # Handle row activation
                def on_row_activated(activated_row, *args):
                    nonlocal selected_font_row
                    if hasattr(activated_row, 'radio'):
                        # Deactivate previous selection
                        if selected_font_row:
                            selected_font_row.remove_css_class("selected")
                            if selected_font_row != activated_row:
                                selected_font_row.radio.set_active(False)
                        # Activate new selection
                        activated_row.radio.set_active(True)
                        activated_row.add_css_class("selected")
                        selected_font_row = activated_row
                
                row.connect("activated", on_row_activated)
                
                # Handle radio button toggled
                def on_radio_toggled(button, toggled_row):
                    nonlocal selected_font_row
                    if button.get_active():
                        if selected_font_row:
                            selected_font_row.remove_css_class("selected")
                        selected_font_row = toggled_row
                        toggled_row.add_css_class("selected")
                    elif toggled_row == selected_font_row:
                        toggled_row.remove_css_class("selected")
                
                radio.connect("toggled", on_radio_toggled, row)
                
                font_group.add(row)
            
            # Add to scroll window
            scroll = Gtk.ScrolledWindow(
                vexpand=True,
                hscrollbar_policy=Gtk.PolicyType.NEVER
            )
            scroll.set_child(font_group)
            content_box.append(scroll)
            
            def on_size_changed(button, change):
                current = int(size_label.get_text())
                new_size = max(6, min(72, current + change))
                size_label.set_text(str(new_size))
            
            def on_apply_clicked(button):
                if selected_font_row:
                    new_font = f"{selected_font_row.font_name} {size_label.get_text()}"
                    self.dconf.set_string("interface", schema_key, new_font)
                    original_row.set_subtitle(new_font)
                    navigation_view.pop()
                else:
                    print("No font selected")
            
            minus_button.connect("clicked", lambda b: on_size_changed(b, -1))
            plus_button.connect("clicked", lambda b: on_size_changed(b, 1))
            apply_button.connect("clicked", on_apply_clicked)
            
            toolbar_view.set_content(content_box)
            return toolbar_view
        
        # Create each font section
        for title, schema_key, subtitle in font_configs:
            section = create_font_section(title, schema_key, subtitle)
            preferred_group.add(section)
        
        self.append(preferred_group)
        self.append(self.create_rendering_section())
    
    def create_rendering_section(self):
        """Creates the font rendering section"""
        rendering_group = self.create_section("Rendering")
        
        # Hinting
        hinting_row = Adw.ExpanderRow(title="Hinting")
        current_hinting = self.dconf.get_string("interface", "font-hinting")
        
        # Create box for hinting options
        hinting_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=8,
            margin_top=8,
            margin_bottom=8,
            margin_start=8,
            margin_end=8,
        )
        
        first_radio = None
        for option in ["Full", "Medium", "Slight", "None"]:
            radio = Gtk.CheckButton(label=option)
            if first_radio:
                radio.set_group(first_radio)
            else:
                first_radio = radio
            if option.lower() == current_hinting:
                radio.set_active(True)
            radio.connect("toggled", self.on_hinting_changed, option.lower())
            hinting_box.append(radio)
        
        hinting_row.add_row(hinting_box)
        rendering_group.add(hinting_row)
        
        # Antialiasing
        antialiasing_row = Adw.ExpanderRow(title="Antialiasing")
        current_aa = self.dconf.get_string("interface", "font-antialiasing")
        
        # Create box for antialiasing options
        antialiasing_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=8,
            margin_top=8,
            margin_bottom=8,
            margin_start=8,
            margin_end=8,
        )
        
        aa_map = {
            "rgba": "Subpixel (for LCD screens)",
            "grayscale": "Standard (greyscale)",
            "none": "None",
        }
        
        first_aa_radio = None
        for value, label in aa_map.items():
            radio = Gtk.CheckButton(label=label)
            if first_aa_radio:
                radio.set_group(first_aa_radio)
            else:
                first_aa_radio = radio
            if value == current_aa:
                radio.set_active(True)
            radio.connect("toggled", self.on_antialiasing_changed, value)
            antialiasing_box.append(radio)
        
        antialiasing_row.add_row(antialiasing_box)
        rendering_group.add(antialiasing_row)
        
        return rendering_group
    
    def on_hinting_changed(self, button, value):
        """Updates font hinting when radio button selection changes"""
        if button.get_active():
            self.dconf.set_string("interface", "font-hinting", value)
    
    def on_antialiasing_changed(self, button, value):
        """Updates font antialiasing when radio button selection changes"""
        if button.get_active():
            self.dconf.set_string("interface", "font-antialiasing", value)
    
    def reset_settings(self):
        """Resets font settings to defaults"""
        self.dconf.reset("interface", "font-name")
        self.dconf.reset("interface", "document-font-name")
        self.dconf.reset("interface", "monospace-font-name")
        self.dconf.reset("interface", "text-scaling-factor")
        self.dconf.reset("interface", "font-antialiasing")
        self.dconf.reset("interface", "font-hinting")
        
        # Refresh the view
        self.build()
    
    def get_system_fonts(self):
        """Gets list of available system fonts"""
        try:
            # Create a temporary widget to get Pango context
            label = Gtk.Label()
            context = label.get_pango_context()
            
            # Get all font families
            families = context.list_families()
            
            # Filter and sort fonts
            fonts = []
            for family in families:
                # Get font name
                name = family.get_name()
                
                # Skip some system/special fonts
                if any(x in name.lower() for x in [
                    'emoji', 'awesome', 'icon', 'symbol', 'webdings', 'wingdings'
                ]):
                    continue
                
                fonts.append(name)
            
            # Sort alphabetically
            fonts.sort()
            
            # If no fonts found, fall back to defaults
            if not fonts:
                return [
                    "Cantarell",
                    "Ubuntu",
                    "DejaVu Sans",
                    "Liberation Sans",
                    "Noto Sans",
                    "Source Code Pro",
                    "Fira Code",
                    "JetBrains Mono"
                ]
            
            return fonts
            
        except Exception as e:
            print(f"Error getting system fonts: {e}")
            return [
                "Cantarell",
                "Ubuntu",
                "DejaVu Sans",
                "Liberation Sans",
                "Noto Sans",
                "Source Code Pro",
                "Fira Code",
                "JetBrains Mono"
            ] 