#!/usr/bin/env python3
# Copyright (C) 2024 Jay W
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys
import gi
import logging
import signal

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from tweakslite.application import TweaksLiteApp
from tweakslite.utils import setup_logging

def signal_handler(signum, frame):
    """Handle interrupt signals gracefully"""
    logger = logging.getLogger('tweakslite.main')
    logger.info("Received interrupt signal, shutting down gracefully...")
    sys.exit(0)

def main():
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Check for debug flag before GTK processes arguments
    debug_enabled = "--debug" in sys.argv
    if debug_enabled:
        # Remove debug flag so GTK doesn't complain
        sys.argv.remove("--debug")
    
    # Setup logging
    setup_logging(debug_enabled)
    
    # Get the logger for the main module
    logger = logging.getLogger('tweakslite.main')
    logger.debug("Starting Tweaks Lite application")
    
    try:
        # Run application
        app = TweaksLiteApp()
        return app.run(sys.argv)
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt, shutting down...")
        return 0
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    sys.exit(main()) 