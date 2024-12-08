import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
gi.require_version("GnomeDesktop", "4.0")

from gi.repository import Gtk, Adw, GnomeDesktop, GLib, Gio
from .base import BaseView
from ..utils import format_keyboard_option


class View(BaseView):
    """View for keyboard settings"""

    def build(self):
        """Builds the keyboard settings view"""
        # Input Sources section
        self.append(self.create_input_section())

        # Layout section
        self.append(self.create_layout_section())

    def create_input_section(self):
        """Creates the input sources section"""
        input_group = self.create_section()

        # Extended Input Sources toggle
        current_show_all = self.dconf.get_boolean("input-sources", "show-all-sources")
        sources_row = Adw.ActionRow(
            title="Show Extended Input Sources",
            subtitle="Increases the choice of input sources in the Settings application",
        )
        sources_switch = Gtk.Switch(active=current_show_all, valign=Gtk.Align.CENTER)
        sources_switch.connect("notify::active", self.on_show_all_sources_changed)
        sources_row.add_suffix(sources_switch)
        input_group.add(sources_row)

        return input_group

    def create_layout_section(self):
        """Creates the keyboard layout section"""
        layout_group = self.create_section("Layout")

        # Emacs Input
        current_theme = self.dconf.get_string("interface", "gtk-key-theme")
        emacs_row = Adw.ActionRow(
            title="Emacs Input",
            subtitle="Overrides shortcuts to use keybindings from the Emacs editor",
        )
        emacs_switch = Gtk.Switch(
            active=current_theme == "Emacs", valign=Gtk.Align.CENTER
        )
        emacs_switch.connect("notify::active", self.on_emacs_input_changed)
        emacs_row.add_suffix(emacs_switch)
        layout_group.add(emacs_row)

        # Overview Shortcut
        current_key = self.dconf.get_string("mutter", "overlay-key")
        options = ["Left Super", "Right Super"]

        shortcut_row = Adw.ComboRow(
            title="Overview Shortcut", model=Gtk.StringList.new(options)
        )

        # Set initial selection
        shortcut_row.set_selected(1 if current_key == "Right Super" else 0)

        # Connect to changes
        shortcut_row.connect("notify::selected", self.on_overlay_key_changed)

        layout_group.add(shortcut_row)

        # Additional Layout Options button
        options_row = Adw.ActionRow(title="Additional Layout Options", activatable=True)
        options_row.connect("activated", self.on_additional_options_clicked)
        layout_group.add(options_row)

        return layout_group

    def on_show_all_sources_changed(self, switch, pspec):
        """Handles changes to show all input sources setting"""
        self.dconf.set_boolean("input-sources", "show-all-sources", switch.get_active())

    def on_emacs_input_changed(self, switch, pspec):
        """Handles changes to Emacs input setting"""
        self.dconf.set_string(
            "interface", "gtk-key-theme", "Emacs" if switch.get_active() else "Default"
        )

    def on_overlay_key_changed(self, row, pspec):
        """Handles changes to overview shortcut key"""
        selected = row.get_selected()
        key = "Right Super" if selected == 1 else "Left Super"
        self.dconf.set_string("mutter", "overlay-key", key)

    def on_additional_options_clicked(self, button):
        """Opens the additional layout options page"""
        window = self.get_root()
        if isinstance(window, Adw.ApplicationWindow):
            navigation_view = window.get_content().get_child().get_content().get_child()

            if isinstance(navigation_view, Adw.NavigationView):
                # Create toolbar view for the content
                toolbar_view = Adw.ToolbarView()

                # Add header bar with only back button
                header = Adw.HeaderBar(
                    show_title=False, show_end_title_buttons=False, decoration_layout=""
                )
                toolbar_view.add_top_bar(header)

                # Create content
                list_box = Gtk.ListBox(
                    selection_mode=Gtk.SelectionMode.NONE,
                    css_classes=["boxed-list"],
                    margin_start=12,
                    margin_end=12,
                    margin_top=12,
                    margin_bottom=12,
                )

                try:
                    xkb_info = GnomeDesktop.XkbInfo()
                    blacklist = {"grp_led", "Compose key"}

                    # Get all option groups except blacklisted ones
                    for group_id in set(xkb_info.get_all_option_groups()) - blacklist:
                        try:
                            group_desc = xkb_info.description_for_group(group_id)
                        except AttributeError:
                            group_desc = group_id

                        # Create row for each option group
                        row = Adw.ActionRow(
                            title=group_desc,
                            activatable=True,
                            css_classes=["option-row"],  # Add custom class for styling
                        )

                        # Add arrow indicator
                        arrow = Gtk.Image.new_from_icon_name("go-next-symbolic")
                        arrow.add_css_class("dim-label")
                        row.add_suffix(arrow)

                        # Store the group ID for later use
                        row.group_id = group_id

                        list_box.append(row)

                    # Connect to row activation
                    list_box.connect("row-activated", self.on_option_group_activated)

                except (AttributeError, GLib.Error) as e:
                    print(f"Error loading XKB options: {e}")
                    row = Adw.ActionRow(
                        title="Could not load keyboard layout options",
                        subtitle="GnomeDesktop library may be missing",
                    )
                    list_box.append(row)

                # Create scrolled window
                scroll = Gtk.ScrolledWindow(
                    hscrollbar_policy=Gtk.PolicyType.NEVER,
                    vscrollbar_policy=Gtk.PolicyType.AUTOMATIC,
                    vexpand=True,
                    hexpand=True,
                )
                scroll.set_child(list_box)

                # Add scroll to toolbar view
                toolbar_view.set_content(scroll)

                # Create navigation page
                page = Adw.NavigationPage(
                    title="Additional Layout Options", child=toolbar_view
                )

                # Push the new page to the navigation stack
                navigation_view.push(page)

    def on_option_group_activated(self, list_box, row):
        """Handles activation of an option group"""
        if hasattr(row, "group_id"):
            window = self.get_root()
            if isinstance(window, Adw.ApplicationWindow):
                navigation_view = (
                    window.get_content().get_child().get_content().get_child()
                )

                if isinstance(navigation_view, Adw.NavigationView):
                    # Create the options page for this group
                    options_page = self.create_options_page(row.group_id)
                    navigation_view.push(options_page)

    def create_options_page(self, group_id):
        """Creates a page for the options in a group"""
        # Create toolbar view
        toolbar_view = Adw.ToolbarView()

        # Add header bar
        header = Adw.HeaderBar(
            show_title=False, show_end_title_buttons=False, decoration_layout=""
        )
        toolbar_view.add_top_bar(header)

        # Create content
        xkb_info = GnomeDesktop.XkbInfo()
        group_desc = xkb_info.description_for_group(group_id)

        # Create preferences group
        group = Adw.PreferencesGroup()
        group.add_css_class("card")

        # Get current options
        current_options = self.dconf.settings["input-sources"].get_strv("xkb-options")

        # Add options
        first_radio = None
        for option_id in xkb_info.get_options_for_group(group_id):
            option_desc = xkb_info.description_for_option(group_id, option_id)
            # Escape the description before setting it as the title
            safe_desc = format_keyboard_option(option_desc)
            row = Adw.ActionRow()
            row.set_title(safe_desc)  # Set the title first
            row.set_use_markup(True)  # Then enable markup interpretation

            # Create check/radio button
            if group_id in {"keypad", "kpdl", "caps", "altwin", "nbsp", "esperanto"}:
                button = Gtk.CheckButton(active=option_id in current_options)
                if first_radio:
                    button.set_group(first_radio)
                else:
                    first_radio = button
            else:
                button = Gtk.CheckButton(active=option_id in current_options)

            button.connect("toggled", self.on_xkb_option_toggled, option_id)
            row.add_prefix(button)
            group.add(row)

        # Create scroll window
        scroll = Gtk.ScrolledWindow(
            hscrollbar_policy=Gtk.PolicyType.NEVER,
            vscrollbar_policy=Gtk.PolicyType.AUTOMATIC,
        )

        # Add group to a box with margins
        box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            margin_start=12,
            margin_end=12,
            margin_top=12,
            margin_bottom=12,
        )
        box.append(group)
        scroll.set_child(box)

        toolbar_view.set_content(scroll)

        # Create navigation page
        return Adw.NavigationPage(title=group_desc, child=toolbar_view)

    def on_xkb_option_toggled(self, button, option_id):
        """Handles toggling of XKB options"""
        if button.get_active():
            self.dconf.setting_add_to_list("input-sources", "xkb-options", option_id)
        else:
            self.dconf.setting_remove_from_list(
                "input-sources", "xkb-options", option_id
            )

    def reset_settings(self):
        """Resets keyboard settings to defaults"""
        self.dconf.reset("input-sources", "show-all-sources")
        self.dconf.reset("interface", "gtk-key-theme")
        self.dconf.reset("mutter", "overlay-key")
        self.dconf.reset("input-sources", "xkb-options")

        # Refresh the view
        self.build()
