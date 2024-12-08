from gi.repository import Adw, Gio, Gtk
from .window import TweaksLiteWindow
import logging

# Get logger for this module
logger = logging.getLogger(__name__)

class TweaksLiteApp(Adw.Application):
    """Main application class for Tweaks Lite"""

    def __init__(self):
        logger.debug("Initializing TweaksLite application")
        super().__init__(
            application_id="dev.jaydoubleu.tweaks.lite",
            flags=Gio.ApplicationFlags.FLAGS_NONE,
        )

    def do_activate(self):
        """Handles application activation"""
        logger.debug("Activating application")
        win = self.props.active_window
        if not win:
            logger.debug("Creating new application window")
            win = TweaksLiteWindow(application=self)
        win.present()

    def do_startup(self):
        """Initializes the application on startup"""
        logger.debug("Starting up application")
        Adw.Application.do_startup(self)

        # Add actions
        logger.debug("Setting up application actions")
        about_action = Gio.SimpleAction.new("about", None)
        about_action.connect("activate", self.on_about)
        self.add_action(about_action)

        # Add reset all action
        reset_all_action = Gio.SimpleAction.new("reset-all", None)
        reset_all_action.connect("activate", self.on_reset)
        self.add_action(reset_all_action)

        # Create menu
        menu = Gio.Menu()
        menu.append("Reset All Settings", "app.reset-all")
        menu.append("About Tweaks Lite", "app.about")

    def on_about(self, action, param):
        """Shows the About dialog with application information"""
        logger.debug("Showing about dialog")
        about = Adw.AboutWindow(
            transient_for=self.get_active_window(),
            application_name="Tweaks Lite",
            application_icon="dev.jaydoubleu.tweaks.lite",
            developer_name="Jay W",
            version="1.0.0",
            website="https://github.com/JayDoubleu/tweaks-lite",
            issue_url="https://github.com/JayDoubleu/tweaks-lite/issues",
            copyright="© 2024 Jay W",
            license_type=Gtk.License.GPL_3_0,
            developers=[]
        )
        
        # Add Code by section first
        about.add_credit_section(
            "Code by",
            ["Jay W https://github.com/JayDoubleu"]
        )
        
        # Add other credit sections
        about.add_credit_section(
            "Based on", 
            ["GNOME Tweaks by GNOME Project team https://gitlab.gnome.org/GNOME/gnome-tweaks"]
        )
        
        about.add_credit_section(
            "Development Assistance", 
            ["Claude 3.5 Sonnet model by Anthropic https://www.anthropic.com"]
        )
        
        about.add_credit_section(
            "Development Tools", 
            ["Cursor IDE https://www.cursor.so"]
        )
        
        about.present()

    def on_reset(self, action, param):
        """Shows a confirmation dialog for resetting all settings to defaults"""
        dialog = Adw.AlertDialog(
            heading="Reset All Settings?",
            body="This will reset all tweaks to their default values. This cannot be undone.",
            default_response="cancel",
            close_response="cancel",
        )

        dialog.add_response("cancel", "_Cancel")
        dialog.add_response("reset", "_Reset")
        dialog.set_response_appearance("reset", Adw.ResponseAppearance.DESTRUCTIVE)

        def on_response(dialog, response):
            if response == "reset":
                window = self.props.active_window
                window.reset_all_settings()

        dialog.connect("response", on_response)
        dialog.present(self.props.active_window) 