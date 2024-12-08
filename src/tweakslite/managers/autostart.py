import os
import shutil
import logging
from gi.repository import Gio
from ..utils import is_flatpak, run_command
from ..desktop_entry import DesktopEntry

# Get logger for this module
logger = logging.getLogger('tweakslite.managers.autostart')

class AutostartManager:
    """Manages startup applications through .desktop files"""

    def __init__(self):
        """Initialize the autostart manager"""
        logger.debug("Initializing AutostartManager")
        if is_flatpak():
            # In Flatpak, we need to use the host's autostart directory
            # Use $HOME instead of ~ for proper expansion in Flatpak
            self.autostart_dir = os.path.join(os.environ.get('HOME', ''), '.config/autostart')
        else:
            self.autostart_dir = os.path.expanduser("~/.config/autostart")
        
        # Create directory if it doesn't exist
        if not is_flatpak():
            os.makedirs(self.autostart_dir, exist_ok=True)

    def get_autostart_files(self):
        """Returns list of current autostart applications"""
        logger.debug("Getting list of autostart applications")
        autostart_apps = []

        if is_flatpak():
            # First, ensure the directory exists on the host
            logger.debug("Running in Flatpak environment")
            mkdir_cmd = f"mkdir -p '{self.autostart_dir}'"
            run_command(mkdir_cmd, shell=True)
            
            # Use find command to list files
            cmd = f"find '{self.autostart_dir}' -type f -name '*.desktop'"
            logger.debug(f"Executing find command: {cmd}")
            result = run_command(cmd, shell=True)
            
            if result:
                desktop_files = result.strip().split('\n')
                logger.debug(f"Found {len(desktop_files)} desktop files")
                for desktop_file in desktop_files:
                    if not desktop_file.strip():
                        continue
                        
                    try:
                        # Get contents of the desktop file
                        logger.debug(f"Reading desktop file: {desktop_file}")
                        cat_cmd = f"cat '{desktop_file}'"
                        content = run_command(cat_cmd, shell=True)
                        
                        if content:
                            entry = DesktopEntry(desktop_file, content)
                            autostart_apps.append(entry)
                    except Exception as e:
                        logger.error(f"Error loading desktop file: {e}", exc_info=True)
        else:
            # Original functionality for non-Flatpak
            logger.debug("Running in non-Flatpak environment")
            if os.path.exists(self.autostart_dir):
                for filename in os.listdir(self.autostart_dir):
                    if filename.endswith(".desktop"):
                        path = os.path.join(self.autostart_dir, filename)
                        try:
                            logger.debug(f"Loading desktop file: {path}")
                            app_info = Gio.DesktopAppInfo.new_from_filename(path)
                            if app_info:
                                autostart_apps.append(app_info)
                        except Exception as e:
                            logger.error(f"Error loading {filename}: {e}", exc_info=True)
        
        logger.debug(f"Found {len(autostart_apps)} autostart applications")
        return autostart_apps

    def add_app_to_autostart(self, app_info):
        """Adds an application to autostart"""
        try:
            if hasattr(app_info, 'get_content'):  # Our custom DesktopEntry
                content = app_info.get_content()
                basename = os.path.basename(app_info.get_filename())
            else:  # Regular GDesktopAppInfo
                source_path = app_info.get_filename()
                if not source_path:
                    logger.error("No source path found")
                    return False
                    
                # Read content from the original file
                with open(source_path, 'r') as f:
                    content = f.read()
                basename = os.path.basename(source_path)
            
            logger.info(f"Adding app: {app_info.get_name()}")
            dest_path = os.path.join(self.autostart_dir, basename)
            logger.debug(f"Destination path: {dest_path}")
            
            # Ensure autostart directory exists
            os.makedirs(self.autostart_dir, exist_ok=True)
            
            # Write content directly to destination
            with open(dest_path, 'w') as f:
                f.write(content)
            
            logger.debug("Successfully copied file")
            return True
            
        except Exception as e:
            logger.error(f"Error adding app to autostart: {e}")
            return False

    def remove_app_from_autostart(self, app_info):
        """Removes an application from autostart"""
        filename = os.path.basename(app_info.get_filename())
        path = os.path.join(self.autostart_dir, filename)

        try:
            if os.path.exists(path):
                os.remove(path)
                logger.info(f"Removed {filename} from autostart")
                return True
            logger.warning(f"File {filename} not found in autostart directory")
            return False
        except Exception as e:
            logger.error(f"Error removing app from autostart: {e}")
            return False 