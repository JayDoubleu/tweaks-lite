import pytest
from tweakslite.desktop_entry import DesktopEntry


@pytest.fixture
def sample_desktop_content():
    """Create sample desktop entry content for testing"""
    return """
[Desktop Entry]
Type=Application
Name=Test App
Exec=testapp
Icon=test-icon
Comment=Test Application
Categories=Settings;
"""


def test_desktop_entry_basic(sample_desktop_content):
    """Test basic desktop entry creation and attributes"""
    entry = DesktopEntry(path=None, content=sample_desktop_content)

    # Test basic attributes
    assert entry.name == "Test App"
    assert entry.exec == "testapp"
    assert entry.icon == "test-icon"
    assert entry.description == "Test Application"
    assert not entry.no_display
    assert not entry.terminal
    assert not entry.hidden


def test_desktop_entry_visibility():
    """Test desktop entry visibility flags"""
    content = """
[Desktop Entry]
Name=Test
NoDisplay=true
Terminal=true
Hidden=true
"""
    entry = DesktopEntry(path=None, content=content)
    assert entry.no_display
    assert entry.terminal
    assert entry.hidden
    assert not entry.should_show()


def test_desktop_entry_getters():
    """Test getter methods"""
    entry = DesktopEntry(
        path="/test/app.desktop",
        content="[Desktop Entry]\nName=Test\nIcon=/path/to/icon.png",
    )

    assert entry.get_name() == "Test"
    assert entry.get_description() == ""  # Empty by default
    assert entry.get_filename() == "/test/app.desktop"
    assert entry.get_content() == "[Desktop Entry]\nName=Test\nIcon=/path/to/icon.png"
    assert entry.get_icon() is None  # Always returns None as per implementation


def test_desktop_entry_icon_handling():
    """Test icon name processing"""
    test_cases = [
        ("/path/to/icon.png", "/path/to/icon.png"),  # Absolute path
        ("org.gnome.Example", "org.gnome.Example"),  # Flatpak style
        ("test.png", "test"),  # Extension stripping
        ("simple-icon", "simple-icon"),  # Standard name
        (None, "application-x-executable"),  # Default icon
    ]

    for input_icon, expected in test_cases:
        content = "[Desktop Entry]\nName=Test"
        if input_icon:
            content += f"\nIcon={input_icon}"
        entry = DesktopEntry(path=None, content=content)
        assert entry.get_icon_name() == expected
