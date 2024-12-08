import pytest
import logging
import sys
from pathlib import Path
import gi

# Initialize GTK before importing any GTK-dependent modules
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


@pytest.fixture(scope="session", autouse=True)
def setup_gtk():
    """Initialize GTK for the test session"""
    from gi.repository import Gtk

    if not Gtk.is_initialized():
        import os

        os.environ["GSETTINGS_BACKEND"] = "memory"
        Gtk.init()


@pytest.fixture
def setup_logging():
    """Fixture to configure logging for tests"""
    logger = logging.getLogger("tweakslite")
    logger.setLevel(logging.DEBUG)
    return logger


@pytest.fixture
def mock_dbus(mocker):
    """Mock dbus-related functionality"""
    mock_bus = mocker.MagicMock()
    mock_interface = mocker.MagicMock()
    mock_bus.get_object.return_value = mock_interface

    mocker.patch("dbus.SessionBus", return_value=mock_bus)
    mocker.patch("dbus.Interface", return_value=mock_interface)
    return mock_bus
