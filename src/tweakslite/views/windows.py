from gi.repository import Gtk, Adw
from .base import BaseView

class View(BaseView):
    """View for window management settings"""
    
    def build(self):
        """Builds the windows settings view"""
        # Titlebar Actions section
        self.append(self.create_titlebar_actions_section())
        
        # Titlebar Buttons section
        self.append(self.create_titlebar_buttons_section())
        
        # Click Actions section
        self.append(self.create_click_actions_section())
        
        # Window Focus section
        self.append(self.create_focus_section())
    
    def create_titlebar_actions_section(self):
        """Creates the titlebar actions section"""
        actions_group = self.create_section("Titlebar Actions")
        
        # Action options
        action_options = [
            "Toggle Maximize",
            "Toggle Shade",
            "Toggle Maximize Horizontally",
            "Toggle Maximize Vertically",
            "Minimize",
            "None",
            "Lower",
            "Menu",
        ]
        
        # Map display names to dconf values
        action_map = {
            "Toggle Maximize": "toggle-maximize",
            "Toggle Shade": "toggle-shade",
            "Toggle Maximize Horizontally": "toggle-maximize-horizontally",
            "Toggle Maximize Vertically": "toggle-maximize-vertically",
            "Minimize": "minimize",
            "None": "none",
            "Lower": "lower",
            "Menu": "menu",
        }
        
        # Double-Click action selector
        current_double = self.dconf.get_string("wm", "action-double-click-titlebar")
        double_click_row = Adw.ComboRow(
            title="Double-Click",
            model=Gtk.StringList.new(action_options)
        )
        for i, option in enumerate(action_options):
            if action_map[option] == current_double:
                double_click_row.set_selected(i)
                break
        double_click_row.connect(
            "notify::selected",
            self.on_titlebar_action_changed,
            "wm",
            "action-double-click-titlebar",
            action_map,
        )
        actions_group.add(double_click_row)
        
        # Middle-Click action selector
        current_middle = self.dconf.get_string("wm", "action-middle-click-titlebar")
        middle_click_row = Adw.ComboRow(
            title="Middle-Click",
            model=Gtk.StringList.new(action_options)
        )
        for i, option in enumerate(action_options):
            if action_map[option] == current_middle:
                middle_click_row.set_selected(i)
                break
        middle_click_row.connect(
            "notify::selected",
            self.on_titlebar_action_changed,
            "wm",
            "action-middle-click-titlebar",
            action_map,
        )
        actions_group.add(middle_click_row)
        
        # Secondary-Click action selector
        current_right = self.dconf.get_string("wm", "action-right-click-titlebar")
        secondary_click_row = Adw.ComboRow(
            title="Secondary-Click",
            model=Gtk.StringList.new(action_options)
        )
        for i, option in enumerate(action_options):
            if action_map[option] == current_right:
                secondary_click_row.set_selected(i)
                break
        secondary_click_row.connect(
            "notify::selected",
            self.on_titlebar_action_changed,
            "wm",
            "action-right-click-titlebar",
            action_map,
        )
        actions_group.add(secondary_click_row)
        
        return actions_group
    
    def create_titlebar_buttons_section(self):
        """Creates the titlebar buttons section"""
        buttons_group = self.create_section("Titlebar Buttons")
        
        # Get current button layout
        current_layout = self.dconf.get_string("wm", "button-layout")
        layout_parts = current_layout.split(":")
        
        # Determine current button states and position
        buttons_on_right = len(layout_parts) > 1 and layout_parts[0] == "appmenu"
        current_buttons = layout_parts[1].split(",") if buttons_on_right else layout_parts[0].split(",")
        current_buttons = [b for b in current_buttons if b]  # Remove empty strings
        
        # Maximize button
        maximize_row = Adw.ActionRow(title="Maximize")
        maximize_switch = Gtk.Switch(
            active="maximize" in current_buttons,
            valign=Gtk.Align.CENTER
        )
        maximize_switch.connect("notify::active", self.on_button_toggled, "maximize")
        maximize_row.add_suffix(maximize_switch)
        buttons_group.add(maximize_row)
        
        # Minimize button
        minimize_row = Adw.ActionRow(title="Minimize")
        minimize_switch = Gtk.Switch(
            active="minimize" in current_buttons,
            valign=Gtk.Align.CENTER
        )
        minimize_switch.connect("notify::active", self.on_button_toggled, "minimize")
        minimize_row.add_suffix(minimize_switch)
        buttons_group.add(minimize_row)
        
        # Button placement
        placement_row = Adw.ActionRow(title="Placement")
        placement_box = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=6,
            valign=Gtk.Align.CENTER
        )
        placement_box.add_css_class("linked")
        
        # Create toggle buttons
        self.left_button = Gtk.ToggleButton(label="Left")
        self.left_button.set_active(not buttons_on_right)
        
        self.right_button = Gtk.ToggleButton(label="Right")
        self.right_button.set_active(buttons_on_right)
        
        # Set up the button group
        self.left_button.set_group(None)  # Remove any existing group
        self.right_button.set_group(self.left_button)
        
        # Connect signals to both buttons
        self.left_button.connect("toggled", self.on_button_placement_changed, "Left")
        self.right_button.connect("toggled", self.on_button_placement_changed, "Right")
        
        placement_box.append(self.left_button)
        placement_box.append(self.right_button)
        placement_row.add_suffix(placement_box)
        buttons_group.add(placement_row)
        
        return buttons_group
    
    def create_click_actions_section(self):
        """Creates the click actions section"""
        click_group = self.create_section("Click Actions")
        
        # Attach Modal Dialogues
        current_attach = self.dconf.get_boolean("mutter", "attach-modal-dialogs")
        attach_row = Adw.ActionRow(
            title="Attach Modal Dialogues",
            subtitle="When on, modal dialogue windows are attached to their parent windows, and cannot be moved",
        )
        attach_switch = Gtk.Switch(active=current_attach, valign=Gtk.Align.CENTER)
        attach_switch.connect("notify::active", self.on_modal_attach_changed)
        attach_row.add_suffix(attach_switch)
        click_group.add(attach_row)
        
        # Centre New Windows
        current_center = self.dconf.get_boolean("mutter", "center-new-windows")
        center_row = Adw.ActionRow(title="Centre New Windows")
        center_switch = Gtk.Switch(active=current_center, valign=Gtk.Align.CENTER)
        center_switch.connect("notify::active", self.on_center_windows_changed)
        center_row.add_suffix(center_switch)
        click_group.add(center_row)
        
        # Window Action Key
        current_modifier = self.dconf.get_string("wm", "mouse-button-modifier")
        modifier_options = ["Super", "Alt", "Disabled"]
        modifier_map = {"Super": "<Super>", "Alt": "<Alt>", "Disabled": "disabled"}
        
        action_key_row = Adw.ComboRow(
            title="Window Action Key",
            model=Gtk.StringList.new(modifier_options)
        )
        
        for i, option in enumerate(modifier_options):
            if modifier_map[option] == current_modifier:
                action_key_row.set_selected(i)
                break
        
        action_key_row.connect(
            "notify::selected",
            self.on_action_key_changed,
            modifier_map
        )
        click_group.add(action_key_row)
        
        # Resize with Secondary-Click
        current_resize = self.dconf.get_boolean("wm", "resize-with-right-button")
        resize_row = Adw.ActionRow(title="Resize with Secondary-Click")
        resize_switch = Gtk.Switch(active=current_resize, valign=Gtk.Align.CENTER)
        resize_switch.connect("notify::active", self.on_resize_right_changed)
        resize_row.add_suffix(resize_switch)
        click_group.add(resize_row)
        
        return click_group
    
    def create_focus_section(self):
        """Creates the window focus section"""
        focus_group = self.create_section("Window Focus")
        
        # Focus Mode radio buttons
        current_focus = self.dconf.get_string("wm", "focus-mode")
        
        # Create focus mode rows
        focus_modes = [
            ("Click to Focus", "click", "Windows are focused when they are clicked"),
            (
                "Focus on Hover",
                "sloppy",
                "Window is focused when hovered with the pointer. Windows remain focused when the desktop is hovered",
            ),
            (
                "Focus Follows Mouse",
                "mouse",
                "Window is focused when hovered with the pointer. Hovering the desktop removes focus from the previous window",
            ),
        ]
        
        # Store radio buttons to access them in the handler
        self.focus_radios = {}
        first_radio = None
        for label, mode, subtitle in focus_modes:
            row = Adw.ActionRow(title=label, subtitle=subtitle)
            radio = Gtk.CheckButton()
            if first_radio:
                radio.set_group(first_radio)
            else:
                first_radio = radio
            if mode == current_focus:
                radio.set_active(True)
            radio.connect("toggled", self.on_focus_mode_changed, mode)
            row.add_prefix(radio)
            focus_group.add(row)
            self.focus_radios[mode] = radio
        
        # Add separator before auto-raise option
        separator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        separator.add_css_class("spacer")
        focus_group.add(separator)
        
        # Raise Windows When Focused
        current_raise = self.dconf.get_boolean("wm", "auto-raise")
        self.raise_row = Adw.ActionRow(
            title="Raise Windows When Focused",
            subtitle="Windows are raised to the top when they receive focus",
        )
        self.raise_switch = Gtk.Switch(active=current_raise, valign=Gtk.Align.CENTER)
        self.raise_switch.connect("notify::active", self.on_auto_raise_changed)
        self.raise_row.add_suffix(self.raise_switch)
        focus_group.add(self.raise_row)
        
        # Set initial sensitivity based on current focus mode
        self.update_raise_sensitivity(current_focus)
        
        return focus_group
    
    def on_titlebar_action_changed(self, row, pspec, schema, key, action_map):
        """Handles changes to titlebar action settings"""
        selected = row.get_selected()
        selected_text = row.get_model().get_string(selected)
        self.dconf.set_string(schema, key, action_map[selected_text])
    
    def on_button_toggled(self, switch, pspec, button_type):
        """Handles changes to titlebar button visibility"""
        current_layout = self.dconf.get_string("wm", "button-layout")
        layout_parts = current_layout.split(":")
        
        # Determine current position and buttons
        buttons_on_right = len(layout_parts) > 1 and layout_parts[0] == "appmenu"
        current_buttons = layout_parts[1].split(",") if buttons_on_right else layout_parts[0].split(",")
        current_buttons = [b for b in current_buttons if b]  # Remove empty strings
        
        # Create new button list
        buttons = []
        
        # Add minimize button
        if button_type == "minimize":
            if switch.get_active() and "minimize" not in current_buttons:
                buttons.append("minimize")
        elif "minimize" in current_buttons:
            buttons.append("minimize")
        
        # Add maximize button
        if button_type == "maximize":
            if switch.get_active() and "maximize" not in current_buttons:
                buttons.append("maximize")
        elif "maximize" in current_buttons:
            buttons.append("maximize")
        
        # Always add close button if it exists
        if "close" in current_buttons or not buttons:  # Ensure at least close button remains
            buttons.append("close")
        
        # Create new layout preserving the current side
        if buttons_on_right:
            new_layout = "appmenu:" + ",".join(buttons)
        else:
            new_layout = ",".join(buttons) + ":appmenu"
        
        self.dconf.set_string("wm", "button-layout", new_layout)
    
    def on_button_placement_changed(self, button, position):
        """Handles changes to titlebar button placement"""
        if not button.get_active():
            return  # Only handle activation, not deactivation
            
        # Get the current button layout
        current_layout = self.dconf.get_string("wm", "button-layout")
        buttons = []
        for part in current_layout.split(":"):
            buttons.extend(part.split(","))
        buttons = [b for b in buttons if b and b != "appmenu"]
        
        # Create new layout based on position
        if position == "Right":
            new_layout = "appmenu:" + ",".join(buttons)
        else:
            new_layout = ",".join(buttons) + ":appmenu"
        
        self.dconf.set_string("wm", "button-layout", new_layout)
    
    def on_modal_attach_changed(self, switch, pspec):
        """Handles changes to modal dialog attachment setting"""
        self.dconf.set_boolean("mutter", "attach-modal-dialogs", switch.get_active())
    
    def on_center_windows_changed(self, switch, pspec):
        """Handles changes to window centering setting"""
        self.dconf.set_boolean("mutter", "center-new-windows", switch.get_active())
    
    def on_action_key_changed(self, row, pspec, modifier_map):
        """Handles changes to window action key setting"""
        selected = row.get_selected()
        selected_text = row.get_model().get_string(selected)
        self.dconf.set_string(
            "wm",
            "mouse-button-modifier",
            modifier_map[selected_text]
        )
    
    def on_resize_right_changed(self, switch, pspec):
        """Handles changes to secondary-click resize setting"""
        self.dconf.set_boolean("wm", "resize-with-right-button", switch.get_active())
    
    def on_focus_mode_changed(self, button, mode):
        """Handles changes to window focus mode"""
        if button.get_active():
            self.dconf.set_string("wm", "focus-mode", mode)
            self.update_raise_sensitivity(mode)
    
    def update_raise_sensitivity(self, mode):
        """Updates the sensitivity of the raise option based on focus mode"""
        is_sensitive = mode in ["sloppy", "mouse"]
        self.raise_row.set_sensitive(is_sensitive)
        self.raise_switch.set_sensitive(is_sensitive)
    
    def on_auto_raise_changed(self, switch, pspec):
        """Handles changes to window auto-raise setting"""
        self.dconf.set_boolean("wm", "auto-raise", switch.get_active())
    
    def reset_settings(self):
        """Resets window settings to defaults"""
        # Get the default button layout first
        default_layout = self.dconf.get_default_value("wm", "button-layout").get_string()
        print(f"Default button layout: {default_layout}")
        
        # Reset all settings
        self.dconf.reset("wm", "button-layout")
        
        # Verify the reset
        current_layout = self.dconf.get_string("wm", "button-layout")
        print(f"Current button layout after reset: {current_layout}")
        
        # Reset other settings
        self.dconf.reset("wm", "action-double-click-titlebar")
        self.dconf.reset("wm", "action-middle-click-titlebar")
        self.dconf.reset("wm", "action-right-click-titlebar")
        self.dconf.reset("mutter", "attach-modal-dialogs")
        self.dconf.reset("mutter", "center-new-windows")
        self.dconf.reset("wm", "mouse-button-modifier")
        self.dconf.reset("wm", "resize-with-right-button")
        self.dconf.reset("wm", "focus-mode")
        self.dconf.reset("wm", "auto-raise")
        
        # Force a rebuild to update the UI
        self.build() 