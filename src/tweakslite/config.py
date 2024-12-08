from gi.repository import Gtk, Gdk
import logging

# Get logger for this module
logger = logging.getLogger(__name__)


class Config:
    """Configuration and shared resources for Tweaks Lite"""

    # Application CSS
    CSS = """
        .navigation-sidebar row.compact {
            min-height: 0;
            padding: 0;
            margin: 4px 0;
        }

        .navigation-sidebar row.compact box {
            padding: 0;
            margin: 0;
        }

        .navigation-sidebar row.compact separator {
            margin: 0 12px;
            opacity: 0.5;
        }

        /* Search bar styling */
        .search-box {
            background: none;
            padding: 0;
            margin: 0;
        }

        searchbar {
            background: none;
            padding: 0;
            margin: 0;
        }

        searchbar > box {
            background: none;
            padding: 0;
            margin: 0;
        }

        searchentry {
            margin: 4px 6px;
            min-height: 34px;
            background: alpha(@window_fg_color, 0.05);
            border: none;
            border-radius: 8px;
        }

        searchentry:focus {
            background: alpha(@window_fg_color, 0.08);
            border: 1px solid @accent_color;
        }

        /* Make group titles dimmed */
        .preferences-group > label {
            color: alpha(@window_fg_color, 0.55);
            font-weight: bold;
            font-size: 0.9em;
        }

        /* Make cards more subtle */
        .card {
            background: alpha(@window_fg_color, 0.03);
            border-radius: 12px;
            padding: 12px;
            margin: 0;
        }

        /* Scaling section styling */
        .title-4 {
            font-weight: bold;
            font-size: 1em;
        }

        .numeric {
            font-feature-settings: "tnum";
            font-family: monospace;
        }

        .button-group button {
            min-width: 60px;
            padding: 4px 12px;
        }

        .button-group-first {
            border-top-right-radius: 0;
            border-bottom-right-radius: 0;
        }

        .button-group-last {
            border-top-left-radius: 0;
            border-bottom-left-radius: 0;
        }
    """

    # Navigation items with their icons
    NAV_ITEMS = [
        ("Fonts", "font-x-generic-symbolic"),
        ("Appearance", "org.gnome.Settings-appearance-symbolic"),
        ("Sound", "org.gnome.Settings-sound-symbolic"),
        ("Mouse & Touchpad", "org.gnome.Settings-mouse-symbolic"),
        ("Keyboard", "org.gnome.Settings-keyboard-symbolic"),
        ("Windows", "org.gnome.Settings-multitasking-symbolic"),
        ("Startup Applications", "org.gnome.Settings-applications-symbolic"),
        ("Extensions", "application-x-addon-symbolic"),
    ]

    @classmethod
    def load_css(cls):
        """Loads the application CSS"""
        logger.debug("Loading application CSS")
        css_provider = Gtk.CssProvider()
        try:
            css_provider.load_from_data(cls.CSS.encode())
            Gtk.StyleContext.add_provider_for_display(
                Gdk.Display.get_default(),
                css_provider,
                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
            )
            logger.debug("CSS loaded successfully")
        except Exception as e:
            logger.error(f"Error loading CSS: {e}", exc_info=True)
