from gi.repository import Adw, Gtk, GLib, Gio
from .managers import DConfSettings, AutostartManager
from .config import Config
import logging

# Get logger for this module
logger = logging.getLogger(__name__)

class TweaksLiteWindow(Adw.ApplicationWindow):
    """Main window for the Tweaks Lite application"""

    def __init__(self, **kwargs):
        logger.debug("Initializing TweaksLite window")
        super().__init__(**kwargs)
        
        # Initialize managers
        logger.debug("Initializing settings managers")
        self.dconf = DConfSettings()
        self.autostart_manager = AutostartManager()
        
        # Load configuration
        logger.debug("Loading configuration")
        self.config = Config()
        
        # Build UI
        logger.debug("Building window UI")
        self.build()

    def build(self):
        """Builds the main user interface"""
        # Set up window properties
        self.set_title("Tweaks Lite")
        self.set_default_size(980, 640)
        
        # Load CSS
        Config.load_css()
        
        # Initialize UI
        self.setup_ui()
        
    def setup_ui(self):
        """Sets up the main user interface"""
        # Create split view
        self.split_view = Adw.NavigationSplitView()
        
        # Set up sidebar
        self.setup_sidebar()
        
        # Set up content area
        self.setup_content()
        
        # Create toast overlay and wrap the split view
        self.toast_overlay = Adw.ToastOverlay()
        self.toast_overlay.set_child(self.split_view)
        
        # Set the window content
        self.set_content(self.toast_overlay)
        
        # Add responsive breakpoint
        self.setup_breakpoint()

    def setup_sidebar(self):
        """Sets up the sidebar navigation"""
        # Create toolbar view for sidebar
        self.sidebar_toolbar_view = Adw.ToolbarView()
        
        # Setup header
        header = Adw.HeaderBar(css_classes=["flat"])
        title = Gtk.Label(label="Tweaks Lite")
        title.add_css_class("title")
        header.set_title_widget(title)
        
        search_button = Gtk.ToggleButton(icon_name="edit-find-symbolic")
        search_button.add_css_class("flat")
        search_button.connect("toggled", self.on_search_toggled)
        header.pack_start(search_button)
        
        menu_button = Gtk.MenuButton(icon_name="open-menu-symbolic")
        menu_button.add_css_class("flat")
        menu = Gio.Menu()
        menu.append("Reset All Settings", "app.reset-all")
        menu.append("About Tweaks Lite", "app.about")
        menu_button.set_menu_model(menu)
        header.pack_end(menu_button)
        
        self.sidebar_toolbar_view.add_top_bar(header)
        
        # Setup search
        search_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        search_box.add_css_class("search-box")
        
        self.search_bar = Gtk.SearchBar(hexpand=True)
        self.search_entry = Gtk.SearchEntry(
            placeholder_text="Search Settings",
            hexpand=True,
            margin_start=6,
            margin_end=6,
            margin_top=4,
            margin_bottom=4,
        )
        self.search_bar.set_child(self.search_entry)
        self.search_bar.connect_entry(self.search_entry)
        search_box.append(self.search_bar)
        
        self.sidebar_toolbar_view.add_top_bar(search_box)
        
        # Create sidebar content
        scroll = Gtk.ScrolledWindow(hscrollbar_policy=Gtk.PolicyType.NEVER)
        self.sidebar_list = Gtk.ListBox(
            css_classes=["navigation-sidebar"],
            selection_mode=Gtk.SelectionMode.SINGLE
        )
        self.sidebar_list.connect("row-activated", self.on_sidebar_item_activated)
        
        # Set filter function for search
        self.sidebar_list.set_filter_func(self.filter_sidebar_items)
        
        # Add navigation items
        for item in Config.NAV_ITEMS:
            if item is None:
                self.add_sidebar_separator(self.sidebar_list)
            else:
                self.add_sidebar_item(self.sidebar_list, item[0], item[1])
        
        scroll.set_child(self.sidebar_list)
        self.sidebar_toolbar_view.set_content(scroll)
        
        # Create navigation page
        sidebar_page = Adw.NavigationPage(
            title="Tweaks Lite",
            child=self.sidebar_toolbar_view
        )
        
        self.split_view.set_sidebar(sidebar_page)

    def setup_content(self):
        """Sets up the content area"""
        # Create content stack
        self.content_stack = Gtk.Stack()
        self.content_stack.add_css_class("background")
        
        # Create toolbar view for content
        self.content_toolbar_view = Adw.ToolbarView()
        
        # Content header bar
        content_header = Adw.HeaderBar(
            show_start_title_buttons=False,
            show_end_title_buttons=True,
            show_title=False,
        )
        self.content_toolbar_view.add_top_bar(content_header)
        self.content_toolbar_view.set_content(self.content_stack)
        
        # Create navigation view for content
        self.content_navigation = Adw.NavigationView()
        
        # Create main content page
        content_page = Adw.NavigationPage(
            title="Content",
            child=self.content_toolbar_view
        )
        self.content_navigation.push(content_page)
        
        # Wrap navigation view in a page
        navigation_page = Adw.NavigationPage(
            title="Content",
            child=self.content_navigation
        )
        
        self.split_view.set_content(navigation_page)
        
        # Load first category by default
        first_category = Config.NAV_ITEMS[0][0]  # Get first non-separator category
        self.load_category(first_category)
        self.set_title(first_category)

    def setup_breakpoint(self):
        """Sets up responsive breakpoint"""
        breakpoint = Adw.Breakpoint.new(
            Adw.BreakpointCondition.new_length(
                Adw.BreakpointConditionLengthType.MAX_WIDTH,
                600,
                Adw.LengthUnit.SP,
            )
        )
        breakpoint.add_setter(self.split_view, "collapsed", True)
        self.add_breakpoint(breakpoint)

    def create_welcome_page(self):
        """Creates the welcome page"""
        welcome = Adw.StatusPage(
            icon_name="preferences-system-symbolic",
            title="Tweaks Lite",
            description="Select a category to begin customizing your desktop",
            vexpand=True,
            hexpand=True,
            valign=Gtk.Align.CENTER
        )
        return welcome

    def add_sidebar_item(self, list_box, title, icon_name):
        """Adds an item to the sidebar"""
        row = Gtk.ListBoxRow()
        box = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=10,
            margin_start=14,
            margin_end=14,
            margin_top=2,
            margin_bottom=2,
        )
        
        icon = Gtk.Image(icon_name=icon_name)
        label = Gtk.Label(label=title, xalign=0, hexpand=True)
        
        box.append(icon)
        box.append(label)
        row.set_child(box)
        list_box.append(row)

    def add_sidebar_separator(self, list_box):
        """Adds a separator to the sidebar"""
        row = Gtk.ListBoxRow(selectable=False, activatable=False, css_classes=["compact"])
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        separator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        box.append(separator)
        row.set_child(box)
        list_box.append(row)

    def on_search_toggled(self, button):
        """Handles search button toggle"""
        self.search_bar.set_search_mode(button.get_active())
        if button.get_active():
            self.search_entry.grab_focus()
        else:
            self.search_entry.set_text("")  # Clear search when closing
        
        # Connect search entry changes to filter
        if not hasattr(self, '_search_handler_id'):
            self._search_handler_id = self.search_entry.connect(
                "search-changed", self.on_search_changed
            )

    def on_search_changed(self, entry):
        """Handles changes to search text"""
        # Refilter the sidebar list
        self.sidebar_list.invalidate_filter()

    def filter_sidebar_items(self, row):
        """Filters sidebar items based on search text"""
        # Don't filter if search is not active
        if not self.search_bar.get_search_mode():
            return True
        
        # Always hide separators during search
        if row.get_css_classes() and "compact" in row.get_css_classes():
            return False
        
        search_text = self.search_entry.get_text().lower()
        if not search_text:
            return True
        
        # Get the row's label
        box = row.get_child()
        label = [w for w in box if isinstance(w, Gtk.Label)][0]
        category = label.get_label()
        
        # First check category name and basic terms
        terms = self.get_search_terms_for_category(category)
        if any(search_text in term.lower() for term in terms):
            return True
        
        # Then search through the actual content
        return self.search_in_view_content(category, search_text)

    def search_in_view_content(self, category, search_text):
        """Searches through the actual content of a view"""
        # Convert category name to view name
        view_name = category.lower()
        view_name = view_name.replace(" & ", "_and_")
        view_name = view_name.replace(" ", "_")
        
        try:
            # Get or create the view
            view = self.content_stack.get_child_by_name(category)
            if not view:
                view_module = __import__(f"tweakslite.views.{view_name}", fromlist=["View"])
                view_class = getattr(view_module, "View")
                view = view_class(self.dconf, self.autostart_manager)
            
            # Search through the view's content
            searchable_content = self.get_view_searchable_content(view)
            return any(search_text in content.lower() for content in searchable_content)
            
        except (ImportError, AttributeError) as e:
            print(f"Error searching in {category}: {e}")
            return False

    def get_view_searchable_content(self, view):
        """Gets all searchable content from a view"""
        searchable_content = set()
        
        def process_widget(widget):
            if isinstance(widget, Adw.ActionRow):
                # Add row title and subtitle
                if widget.get_title():
                    searchable_content.add(widget.get_title().lower())
                if widget.get_subtitle():
                    searchable_content.add(widget.get_subtitle().lower())
            
            elif isinstance(widget, Adw.ComboRow):
                # Add combo row options
                model = widget.get_model()
                if model:
                    for i in range(model.get_n_items()):
                        searchable_content.add(model.get_string(i).lower())
            
            elif isinstance(widget, Gtk.Label):
                if widget.get_text():
                    searchable_content.add(widget.get_text().lower())
            
            # Recursively process children
            if isinstance(widget, Gtk.Widget):
                child = widget.get_first_child()
                while child:
                    process_widget(child)
                    child = child.get_next_sibling()
        
        # Start processing from the view's content box
        if hasattr(view, 'content_box'):
            process_widget(view.content_box)
        
        return searchable_content

    def on_sidebar_item_activated(self, list_box, row):
        """Handles sidebar item selection"""
        # Skip separators
        if not row or row.get_css_classes() and "compact" in row.get_css_classes():
            return

        # Get selected category
        box = row.get_child()
        label = [w for w in box if isinstance(w, Gtk.Label)][0]
        category = label.get_label()

        # Load or show category content
        self.load_category(category)

        # Update window title
        self.set_title(category)

        # In mobile mode, hide sidebar
        if self.split_view.get_collapsed():
            self.split_view.set_show_content(True)

    def load_category(self, category):
        """Loads the content for a category"""
        try:
            # Convert category name to module name
            view_name = category.lower()
            view_name = view_name.replace(" & ", "_and_")
            view_name = view_name.replace(" ", "_")
            
            view_module = __import__(f"tweakslite.views.{view_name}", fromlist=["View"])
            view_class = getattr(view_module, "View")
            
            # Create view if it doesn't exist
            if not self.content_stack.get_child_by_name(category):
                view = view_class(self.dconf, self.autostart_manager)
                self.content_stack.add_named(view, category)
            
            # Show the view
            self.content_stack.set_visible_child_name(category)
            
        except Exception as e:
            print(f"Error loading view for {category}: {e}")
            if hasattr(self, 'toast_overlay'):
                self.show_toast(f"Error loading {category} settings")

    def show_toast(self, text):
        """Shows a toast notification"""
        toast = Adw.Toast(title=text, timeout=2)
        self.toast_overlay.add_toast(toast)

    def reset_all_settings(self):
        """Resets all settings to their defaults"""
        # Get all view names from Config.NAV_ITEMS
        view_names = []
        for item in Config.NAV_ITEMS:
            if item is not None:  # Skip separators
                category = item[0]
                view_name = category.lower()
                view_name = view_name.replace(" & ", "_and_")
                view_name = view_name.replace(" ", "_")
                view_names.append((category, view_name))
        
        # Reset each view's settings
        for category, view_name in view_names:
            try:
                # Get existing view if it's loaded
                existing_view = self.content_stack.get_child_by_name(category)
                
                # Import and instantiate the view if needed
                if not existing_view:
                    view_module = __import__(f"tweakslite.views.{view_name}", fromlist=["View"])
                    view_class = getattr(view_module, "View")
                    view = view_class(self.dconf, self.autostart_manager)
                else:
                    view = existing_view
                
                # Reset its settings if it has a reset method
                if hasattr(view, 'reset_settings'):
                    view.reset_settings()
                
                # If it's startup applications, refresh the list
                if view_name == "startup_applications":
                    view.refresh_list()
                # For other views that are loaded, rebuild them
                elif existing_view:
                    # Clear existing content
                    while True:
                        child = existing_view.content_box.get_first_child()
                        if child is None:
                            break
                        existing_view.content_box.remove(child)
                    # Rebuild the view
                    existing_view.build()
                
            except (ImportError, AttributeError) as e:
                print(f"Error resetting {category}: {e}")
        
        # Show confirmation toast
        self.show_toast("All settings have been reset to defaults")

    def get_search_terms_for_category(self, category):
        """Gets searchable terms for a category"""
        terms = [category]  # Start with category name
        
        # Add category-specific search terms
        search_terms = {
            "Fonts": [
                "font", "text", "interface", "document", "monospace", "hinting", 
                "antialiasing", "scaling", "size", "rendering", "cantarell", 
                "source code pro"
            ],
            "Appearance": [
                "theme", "style", "dark mode", "light mode", "icons", "cursor",
                "adwaita", "yaru", "legacy", "high contrast"
            ],
            "Sound": [
                "audio", "sound effects", "alert", "feedback", "event sounds",
                "input feedback", "system sounds"
            ],
            "Mouse & Touchpad": [
                "mouse", "touchpad", "clicking", "scrolling", "pointer", "cursor",
                "paste", "middle click", "primary selection"
            ],
            "Keyboard": [
                "keyboard", "typing", "shortcuts", "layout", "input", "emacs",
                "compose key", "caps lock", "numlock", "super key"
            ],
            "Windows": [
                "window", "titlebar", "buttons", "maximize", "minimize", "focus",
                "raise", "click action", "double click", "middle click"
            ],
            "Extensions": [
                "extensions", "gnome shell", "shell extensions", "gnome-shell-extension",
                "gnome-shell-extensions", "gnome-shell-extension-manager", "gnome-shell-extension-installer"
            ],
            "Startup Applications": [
                "autostart", "startup", "boot", "login", "automatic", "launch",
                "startup programs", "session", "autorun"
            ]
        }
        
        if category in search_terms:
            terms.extend(search_terms[category])
        
        return terms