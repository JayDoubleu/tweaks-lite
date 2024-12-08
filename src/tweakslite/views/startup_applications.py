from gi.repository import Gtk, Adw, Gio, GLib
from .base import BaseView
import os
from ..utils import is_flatpak, run_command
from ..desktop_entry import DesktopEntry
import tempfile
import shutil
import logging

# Get logger for this module
logger = logging.getLogger(__name__)


class View(BaseView):
    """View for startup applications settings"""

    def __init__(self, dconf, autostart_manager=None):
        logger.debug("Initializing StartupApplications view")
        # Call parent init but with show_reset=False
        super().__init__(dconf, autostart_manager, show_reset=False)

    def build(self):
        """Builds the startup applications view"""
        # Create title box for desktop view
        title_box = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=12,
            margin_start=12,
            margin_end=12,
            margin_top=24,
            margin_bottom=12,
        )

        # Title and subtitle in vertical box
        text_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL, spacing=3, hexpand=True
        )

        title = Gtk.Label(label="Startup Applications", halign=Gtk.Align.START)
        title.add_css_class("title-1")

        subtitle = Gtk.Label(
            label="Applications that will start automatically when you log in",
            halign=Gtk.Align.START,
            wrap=True,
        )
        subtitle.add_css_class("subtitle-1")

        text_box.append(title)
        text_box.append(subtitle)

        # Add button
        add_button = Gtk.Button(
            icon_name="list-add-symbolic",
            valign=Gtk.Align.CENTER,
            css_classes=["circular"],
        )
        add_button.connect("clicked", self.on_add_clicked)

        title_box.append(text_box)
        title_box.append(add_button)

        self.append(title_box)

        # Create list group
        list_group = Adw.PreferencesGroup()
        list_group.add_css_class("card")

        # Create stack for empty state and list
        self.startup_stack = Gtk.Stack()

        # Empty state
        empty_state = Adw.StatusPage(
            icon_name="application-x-executable-symbolic",
            title="No Startup Applications",
            description="Add applications to start automatically when you log in",
            vexpand=True,
        )

        # Create list group for applications
        self.startup_list = Adw.PreferencesGroup()

        # Add both states to stack
        self.startup_stack.add_named(empty_state, "empty")
        self.startup_stack.add_named(self.startup_list, "list")

        list_group.add(self.startup_stack)
        self.append(list_group)

        # Now refresh the list
        self.refresh_list()

    def refresh_list(self):
        """Updates the list of startup applications"""
        logger.debug("Refreshing startup applications list")
        # Create new preferences group
        new_list = Adw.PreferencesGroup()

        apps = self.autostart_manager.get_autostart_files()
        logger.debug(f"Found {len(apps)} startup applications")

        for app in apps:
            # Create a new row for each app
            row = Adw.ActionRow(
                title=app.get_name(),
                subtitle=app.get_description() or "",
                activatable=False,
            )

            # Add app icon
            icon = Gtk.Image()
            if isinstance(app, DesktopEntry):
                # For our custom DesktopEntry class
                icon.set_from_icon_name(app.get_icon_name())
            else:
                # For GDesktopAppInfo
                if app.get_icon():
                    icon.set_from_gicon(app.get_icon())
                else:
                    icon.set_from_icon_name("application-x-executable")
            icon.set_pixel_size(32)
            row.add_prefix(icon)

            # Add remove button
            remove_button = Gtk.Button(
                icon_name="user-trash-symbolic",
                valign=Gtk.Align.CENTER,
                css_classes=["flat", "dim-label"],
            )
            remove_button.connect("clicked", self.on_remove_clicked, app)
            row.add_suffix(remove_button)

            new_list.add(row)

        # Remove old list from stack if it exists
        old_list = self.startup_stack.get_child_by_name("list")
        if old_list:
            self.startup_stack.remove(old_list)

        # Add new list to stack
        self.startup_list = new_list
        self.startup_stack.add_named(self.startup_list, "list")

        # Show empty state or list
        if len(apps) > 0:
            self.startup_stack.set_visible_child_name("list")
        else:
            self.startup_stack.set_visible_child_name("empty")

    def on_add_clicked(self, button):
        """Shows dialog to add startup application"""
        logger.debug("Opening add startup application dialog")
        # Creates a new modal dialog window
        dialog = Adw.Window(
            modal=True,
            transient_for=self.get_root(),
            title="Add Startup Application",
            default_width=400,
            default_height=500,
        )

        # Create navigation view for add dialog
        navigation_view = Adw.NavigationView()

        def create_app_row(app):
            # Create row
            row = Adw.ActionRow(
                title=app.get_name() or "",
                subtitle=app.get_description() or "",
                activatable=True,
            )

            # Add application icon
            icon = Gtk.Image(pixel_size=32)
            if isinstance(app, DesktopEntry):
                icon.set_from_icon_name(app.get_icon_name())
            else:
                if app.get_icon():
                    icon.set_from_gicon(app.get_icon())
                else:
                    icon.set_from_icon_name("application-x-executable")

            row.add_prefix(icon)
            row.app_info = app
            return row

        def create_app_page():
            toolbar_view = Adw.ToolbarView()

            # Add header bar
            header = Adw.HeaderBar(
                show_title=False, show_end_title_buttons=False, decoration_layout=""
            )

            # Add cancel button
            cancel_button = Gtk.Button(label="Cancel")
            cancel_button.add_css_class("flat")
            cancel_button.connect("clicked", lambda _: dialog.destroy())
            header.pack_start(cancel_button)

            # Add add button
            add_button = Gtk.Button(label="Add")
            add_button.add_css_class("suggested-action")
            add_button.set_sensitive(False)  # Initially disabled until selection
            add_button.connect(
                "clicked", lambda b: self.on_add_button_clicked(b, dialog)
            )
            header.pack_end(add_button)

            toolbar_view.add_top_bar(header)

            # Create stack for loading state and list
            stack = Gtk.Stack(
                transition_type=Gtk.StackTransitionType.CROSSFADE,
                transition_duration=200,
            )

            # Create loading page
            loading_box = Gtk.Box(
                orientation=Gtk.Orientation.VERTICAL,
                spacing=12,
                valign=Gtk.Align.CENTER,
                halign=Gtk.Align.CENTER,
            )

            spinner = Gtk.Spinner(spinning=True, width_request=32, height_request=32)
            loading_label = Gtk.Label(label="Loading applications...")

            loading_box.append(spinner)
            loading_box.append(loading_label)

            stack.add_named(loading_box, "loading")

            # Create list box for applications
            list_box = Gtk.ListBox(
                selection_mode=Gtk.SelectionMode.SINGLE,
                css_classes=["boxed-list"],
                margin_start=12,
                margin_end=12,
                margin_top=12,
                margin_bottom=12,
            )

            # Create scrolled window for list
            scroll = Gtk.ScrolledWindow(
                hscrollbar_policy=Gtk.PolicyType.NEVER,
                vscrollbar_policy=Gtk.PolicyType.AUTOMATIC,
                vexpand=True,
            )
            scroll.set_child(list_box)

            stack.add_named(scroll, "list")
            stack.set_visible_child_name("loading")

            toolbar_view.set_content(stack)

            # Load applications in an idle callback to allow the UI to show
            def load_applications():
                logger.debug("Loading applications list")
                if is_flatpak():
                    with tempfile.TemporaryDirectory() as temp_dir:
                        logger.debug(f"Created temp directory: {temp_dir}")

                        # First handle host applications
                        host_apps_cmd = (
                            "ls /usr/share/applications/*.desktop 2>/dev/null"
                        )
                        result = run_command(host_apps_cmd, shell=True)

                        if result:
                            desktop_files = result.strip().split("\n")
                            logger.debug(
                                f"Found {len(desktop_files)} host applications"
                            )
                            for desktop_file in desktop_files:
                                if not desktop_file.strip():
                                    continue

                                try:
                                    logger.debug(f"Processing host app: {desktop_file}")
                                    cat_cmd = f"cat '{desktop_file}'"
                                    content = run_command(cat_cmd, shell=True)

                                    if content and "[Desktop Entry]" in content:
                                        # Process the desktop file content
                                        processed_content = []
                                        has_name = False
                                        has_type = False
                                        has_exec = False
                                        icon_name = None

                                        for line in content.split("\n"):
                                            # Skip certain entries
                                            if (
                                                line.startswith("DBusActivatable=")
                                                or line.startswith("X-")
                                                or line.startswith("Actions=")
                                            ):
                                                continue

                                            # Process specific entries
                                            if line.startswith("Name="):
                                                has_name = True
                                            elif line.startswith("Type=Application"):
                                                has_type = True
                                            elif line.startswith("Exec="):
                                                has_exec = True
                                                # Replace actual command with placeholder
                                                line = "Exec=true"
                                            elif line.startswith("Icon="):
                                                # Extract just the icon name without path
                                                icon_name = line.split("=")[1].strip()
                                                if "/" in icon_name:
                                                    icon_name = os.path.basename(
                                                        icon_name
                                                    )
                                                    if (
                                                        "." in icon_name
                                                    ):  # Remove extension if present
                                                        icon_name = icon_name.rsplit(
                                                            ".", 1
                                                        )[0]
                                                line = f"Icon={icon_name}"

                                            processed_content.append(line)

                                        # Skip if missing essential fields
                                        if not (has_name and has_type):
                                            continue

                                        # Add Exec if missing
                                        if not has_exec:
                                            processed_content.append("Exec=true")

                                        # Create desktop entry directly with processed content
                                        final_content = "\n".join(processed_content)
                                        entry = DesktopEntry(
                                            desktop_file, final_content
                                        )

                                        if entry.should_show():
                                            print(
                                                f"Adding host app: {entry.get_name()}"
                                            )
                                            row = create_app_row(entry)
                                            list_box.append(row)

                                except Exception as e:
                                    logger.error(
                                        f"Error processing host app {desktop_file}: {e}",
                                        exc_info=True,
                                    )

                        # Then handle Flatpak applications
                        flatpak_locations = [
                            "/var/lib/flatpak/exports/share/applications/*.desktop",
                            f"{os.environ.get('HOME')}/.local/share/flatpak/exports/share/applications/*.desktop",
                        ]

                        for location in flatpak_locations:
                            logger.debug(f"Scanning Flatpak location: {location}")
                            cmd = f"ls {location} 2>/dev/null || true"
                            result = run_command(cmd, shell=True)

                            if result and result != "true":
                                desktop_files = result.strip().split("\n")
                                logger.debug(
                                    f"Found {len(desktop_files)} Flatpak applications in {location}"
                                )
                                for desktop_file in desktop_files:
                                    if not desktop_file.strip():
                                        continue

                                    try:
                                        logger.debug(
                                            f"\nProcessing Flatpak app: {desktop_file}"
                                        )
                                        cat_cmd = f"cat '{desktop_file}'"
                                        content = run_command(cat_cmd, shell=True)

                                        if content and "[Desktop Entry]" in content:
                                            # Process the desktop file content
                                            processed_content = []
                                            has_name = False
                                            has_type = False
                                            has_exec = False

                                            for line in content.split("\n"):
                                                if line.startswith("Name="):
                                                    has_name = True
                                                elif line.startswith(
                                                    "Type=Application"
                                                ):
                                                    has_type = True
                                                elif line.startswith("Exec="):
                                                    has_exec = True
                                                    if "flatpak run" in line:
                                                        # Replace Flatpak exec with a simple command
                                                        line = "Exec=true"
                                                elif line.startswith("X-Flatpak="):
                                                    # Skip Flatpak metadata
                                                    continue
                                                processed_content.append(line)

                                            # Add Exec if missing
                                            if not has_exec:
                                                processed_content.append("Exec=true")

                                            if has_name and has_type:
                                                # Write processed content to temp file
                                                temp_path = os.path.join(
                                                    temp_dir,
                                                    os.path.basename(desktop_file),
                                                )
                                                with open(temp_path, "w") as f:
                                                    f.write(
                                                        "\n".join(processed_content)
                                                    )

                                                # Try to create app info from the modified file
                                                app_info = Gio.DesktopAppInfo.new_from_filename(
                                                    temp_path
                                                )
                                                if app_info and app_info.should_show():
                                                    print(
                                                        f"Adding Flatpak app: {app_info.get_name()}"
                                                    )
                                                    row = create_app_row(app_info)
                                                    list_box.append(row)

                                    except Exception as e:
                                        logger.error(
                                            f"Error processing Flatpak app {desktop_file}: {e}",
                                            exc_info=True,
                                        )
                else:
                    logger.debug("Loading applications in non-Flatpak environment")
                    app_list = Gio.AppInfo.get_all()
                    logger.debug(f"Found {len(app_list)} applications")
                    for app in app_list:
                        if not app.should_show():
                            continue
                        row = create_app_row(app)
                        list_box.append(row)

                # Switch to the list view once loading is complete
                stack.set_visible_child_name("list")
                return GLib.SOURCE_REMOVE

            # Schedule the loading to happen in an idle callback
            GLib.idle_add(load_applications)

            # Handle selection
            def on_row_selected(box, row):
                if row:
                    self.selected_app = row.app_info
                    add_button.set_sensitive(True)
                else:
                    self.selected_app = None
                    add_button.set_sensitive(False)

            list_box.connect("row-selected", on_row_selected)

            return toolbar_view

        # Create the page and add it to navigation view
        page = Adw.NavigationPage(title="Select Application", child=create_app_page())
        navigation_view.push(page)

        # Set the navigation view as the dialog content
        dialog.set_content(navigation_view)

        # Present the dialog
        dialog.present()

    def on_add_button_clicked(self, button, dialog):
        """Handles clicking the Add button"""
        logger.debug("Add button clicked")
        if hasattr(self, "selected_app") and self.selected_app:
            logger.info(
                f"Adding application to startup: {self.selected_app.get_name()}"
            )
            if self.autostart_manager.add_app_to_autostart(self.selected_app):
                logger.debug("Successfully added application to startup")
                self.refresh_list()
            else:
                logger.error("Failed to add application to startup")
        dialog.destroy()

    def on_remove_clicked(self, button, app_info):
        """Removes an application from startup"""
        logger.info(f"Removing application from startup: {app_info.get_name()}")
        if self.autostart_manager.remove_app_from_autostart(app_info):
            logger.debug("Successfully removed application from startup")
            self.refresh_list()
        else:
            logger.error("Failed to remove application from startup")

    def reset_settings(self):
        """Resets startup settings to defaults"""
        # Currently no settings to reset as startup apps are managed through files
        pass

    def add_app_to_autostart(self, app_info):
        """Adds an application to autostart"""
        logger.info(f"Adding {app_info.get_name()} to autostart")
        try:
            if is_flatpak():
                logger.debug("Processing Flatpak application")
                desktop_file = app_info.get_filename()
                logger.debug(f"Reading desktop file: {desktop_file}")
                with open(desktop_file, "r") as f:
                    content = f.read()

                # Process the content for autostart
                processed_content = []
                for line in content.split("\n"):
                    if line.startswith("Exec="):
                        # Keep the original Exec line for Flatpak apps
                        if "flatpak run" in line:
                            processed_content.append(line)
                        else:
                            # For host apps, preserve the original command
                            processed_content.append(line)
                    elif not (
                        line.startswith("DBusActivatable=")
                        or line.startswith("X-")
                        or line.startswith("Actions=")
                    ):
                        processed_content.append(line)

                # Create the content to write
                final_content = "\n".join(processed_content)

                # Get the destination path
                basename = os.path.basename(desktop_file)
                autostart_dir = os.path.expanduser("~/.config/autostart")
                dest_path = os.path.join(autostart_dir, basename)

                # Ensure autostart directory exists
                os.makedirs(autostart_dir, exist_ok=True)

                logger.debug(f"Writing processed content to: {dest_path}")
                with open(dest_path, "w") as f:
                    f.write(final_content)

                logger.info("Successfully added Flatpak application to autostart")
                return True

            else:
                logger.debug("Processing non-Flatpak application")
                source_path = app_info.get_filename()
                if not source_path:
                    logger.error("No desktop file found for application")
                    return False

                # Get the destination path
                basename = os.path.basename(source_path)
                dest_path = os.path.expanduser(f"~/.config/autostart/{basename}")

                # Ensure autostart directory exists
                os.makedirs(os.path.dirname(dest_path), exist_ok=True)

                logger.debug(f"Copying {source_path} to {dest_path}")
                shutil.copy2(source_path, dest_path)
                logger.info("Successfully added application to autostart")
                return True

        except Exception as e:
            logger.error(f"Failed to add application to autostart: {e}", exc_info=True)
            return False
