from gi.repository import Gtk, Adw
import logging

# Get logger for this module
logger = logging.getLogger(__name__)


class BaseView(Gtk.Box):
    """Base class for all settings views"""

    def __init__(self, dconf, autostart_manager=None, show_reset=True):
        logger.debug("Initializing BaseView")
        super().__init__(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=0,
            hexpand=True,
            vexpand=True,
        )

        self.dconf = dconf
        self.autostart_manager = autostart_manager

        if show_reset:
            logger.debug("Adding reset button to view")
            # Create header with reset button
            header = Gtk.Box(
                orientation=Gtk.Orientation.HORIZONTAL,
                spacing=12,
                margin_start=12,
                margin_end=12,
                margin_top=12,
                margin_bottom=12,
            )

            # Add reset button
            reset_button = Gtk.Button(
                label="Reset Page Settings",
                css_classes=["flat"],
                halign=Gtk.Align.END,
                hexpand=True,
            )
            reset_button.connect("clicked", self.on_reset_clicked)
            header.append(reset_button)

            Gtk.Box.append(self, header)

        # Create scrolled window
        scroll = Gtk.ScrolledWindow(
            hscrollbar_policy=Gtk.PolicyType.NEVER,
            vscrollbar_policy=Gtk.PolicyType.AUTOMATIC,
            hexpand=True,
            vexpand=True,
        )

        # Create content box for actual content
        self.content_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=24,
            margin_start=12,
            margin_end=12,
            margin_top=12,
            margin_bottom=12,
            hexpand=True,
        )

        # Add content box to scroll window
        scroll.set_child(self.content_box)

        # Add scroll window to view
        Gtk.Box.append(self, scroll)

        # Build the view
        self.build()

    def build(self):
        """Builds the view content - to be implemented by subclasses"""
        raise NotImplementedError

    def reset_settings(self):
        """Resets settings to defaults - to be implemented by subclasses"""
        raise NotImplementedError

    def create_section(self, title=None):
        """Creates a new preferences group with card styling"""
        logger.debug(f"Creating section: {title}")
        group = Adw.PreferencesGroup(title=title)
        group.add_css_class("card")
        return group

    def append(self, widget):
        """Override append to add widgets to content box instead"""
        self.content_box.append(widget)

    def on_reset_clicked(self, button):
        """Handles clicking the reset button"""
        logger.debug("Reset button clicked")
        dialog = Adw.AlertDialog(
            heading="Reset Page Settings?",
            body="This will reset all settings on this page to their default values. This cannot be undone.",
            default_response="cancel",
            close_response="cancel",
        )

        dialog.add_response("cancel", "Cancel")
        dialog.add_response("reset", "Reset")
        dialog.set_response_appearance("reset", Adw.ResponseAppearance.DESTRUCTIVE)

        def on_response(dialog, response):
            if response == "reset":
                logger.info("Resetting page settings to defaults")
                self.reset_settings()
                # Clear existing content
                while True:
                    child = self.content_box.get_first_child()
                    if child is None:
                        break
                    self.content_box.remove(child)
                # Rebuild the view
                self.build()
                logger.debug("View rebuilt after reset")
                # Show confirmation toast
                window = self.get_root()
                if window:
                    window.show_toast("Page settings have been reset to defaults")

        dialog.connect("response", on_response)
        dialog.present(self.get_root())
