import os
import logging

# Get logger for this module
logger = logging.getLogger("tweakslite.desktop_entry")


class DesktopEntry:
    def __init__(self, path, content):
        logger.debug(f"Creating DesktopEntry for {path}")
        self.path = path
        self.content = content  # Store the original content
        self.name = None
        self.exec = None
        self.icon = None
        self.description = ""
        self.no_display = False
        self.terminal = False
        self.hidden = False

        # Parse desktop file content
        logger.debug("Parsing desktop file content")
        current_group = None
        for line in content.split("\n"):
            line = line.strip()
            if line.startswith("["):
                current_group = line
                continue
            if not line or line.startswith("#") or "=" not in line:
                continue
            if current_group == "[Desktop Entry]":
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip()
                if key == "Name":
                    self.name = value
                elif key == "Exec":
                    self.exec = value
                elif key == "Icon":
                    self.icon = value
                elif key == "Comment":
                    self.description = value
                elif key == "NoDisplay":
                    self.no_display = value.lower() == "true"
                elif key == "Terminal":
                    self.terminal = value.lower() == "true"
                elif key == "Hidden":
                    self.hidden = value.lower() == "true"

    def should_show(self):
        return not (self.no_display or self.terminal or self.hidden)

    def get_name(self):
        return self.name or os.path.basename(self.path)

    def get_icon_name(self):
        if self.icon:
            logger.debug(f"Processing icon: {self.icon}")

            # Handle absolute paths
            if self.icon.startswith("/"):
                return self.icon

            # Handle Flatpak app icons
            if self.icon.startswith("org.") or self.icon.startswith("com."):
                return self.icon

            # Handle standard icon names
            if "." in self.icon:
                return self.icon.split(".")[0]

            return self.icon
        return "application-x-executable"

    def get_filename(self):
        return self.path

    def get_description(self):
        return self.description

    def get_icon(self):
        return None  # Let GTK handle icon loading through get_icon_name

    def get_content(self):
        """Returns the desktop file content"""
        return self.content
