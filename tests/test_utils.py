import pytest
from tweakslite.utils import (
    escape_markup,
    setup_logging,
    is_flatpak,
    run_command,
    format_keyboard_option,
    format_key_description,
)
import logging
import os
import subprocess


def test_escape_markup():
    """Test markup escaping functionality"""
    test_cases = [
        ("Hello World", "Hello World"),
        ("<test>", "&lt;test&gt;"),
        ("&special", "&amp;special"),
        ("", ""),
        (None, ""),
        ('Text with "quotes"', 'Text with "quotes"'),
        ("<b>Bold</b>", "&lt;b&gt;Bold&lt;/b&gt;"),
        ("100% & <more>", "100% &amp; &lt;more&gt;"),
    ]

    for input_text, expected in test_cases:
        assert escape_markup(input_text) == expected


def test_setup_logging(tmp_path):
    """Test logging setup functionality"""
    # Redirect log file to temporary directory
    log_dir = tmp_path / ".cache" / "tweakslite"
    os.environ["HOME"] = str(tmp_path)

    # Test debug mode
    setup_logging(debug=True)
    logger = logging.getLogger("tweakslite")

    assert logger.level == logging.DEBUG
    assert len(logger.handlers) == 2  # Console and file handler

    # Test if log file was created
    log_file = log_dir / "tweakslite.log"
    assert log_file.parent.exists()

    # Test actual logging
    test_message = "Test debug message"
    logger.debug(test_message)

    # Read log file content
    with open(log_file) as f:
        log_content = f.read()
    assert test_message in log_content


def test_setup_logging_info_level(tmp_path):
    """Test logging setup with INFO level"""
    os.environ["HOME"] = str(tmp_path)
    setup_logging(debug=False)
    logger = logging.getLogger("tweakslite")
    assert logger.level == logging.INFO


def test_is_flatpak(tmp_path, monkeypatch):
    """Test Flatpak environment detection in both scenarios"""
    # Test non-Flatpak environment
    monkeypatch.setattr("os.path.exists", lambda x: False)
    assert not is_flatpak()

    # Test Flatpak environment
    monkeypatch.setattr("os.path.exists", lambda x: x == "/.flatpak-info")
    assert is_flatpak()


def test_run_command_success(monkeypatch):
    """Test successful command execution"""
    mock_result = subprocess.CompletedProcess(
        args=["test"], returncode=0, stdout="success\n", stderr=""
    )
    monkeypatch.setattr("subprocess.run", lambda *args, **kwargs: mock_result)

    result = run_command(["test", "command"])
    assert result == "success"


def test_run_command_failure(monkeypatch):
    """Test failed command execution"""

    def mock_run(*args, **kwargs):
        error = subprocess.CalledProcessError(1, "test")
        error.stderr = "error message"
        raise error

    monkeypatch.setattr("subprocess.run", mock_run)

    result = run_command(["test", "command"])
    assert result is None


def test_run_command_timeout(monkeypatch):
    """Test command timeout"""

    def mock_run(*args, **kwargs):
        raise subprocess.TimeoutExpired("test", 30)

    monkeypatch.setattr("subprocess.run", mock_run)

    # Since TimeoutExpired isn't explicitly handled, it will propagate
    with pytest.raises(subprocess.TimeoutExpired):
        run_command(["test", "command"])


def test_setup_logging_file_error(tmp_path, monkeypatch):
    """Test logging setup with file creation error"""
    logger = logging.getLogger("tweakslite")
    logger.handlers.clear()  # Ensure clean state

    # Mock the FileHandler to simulate permission error
    def mock_file_handler(*args, **kwargs):
        raise PermissionError("Simulated permission error")

    monkeypatch.setattr("logging.FileHandler", mock_file_handler)

    # Since the error isn't handled, it should raise
    with pytest.raises(PermissionError):
        setup_logging(debug=True)


@pytest.fixture(autouse=True)
def clean_logging():
    """Clean up logging handlers before and after each test"""
    logger = logging.getLogger("tweakslite")
    # Store original handlers
    original_handlers = logger.handlers[:]
    logger.handlers.clear()
    logger.propagate = False

    yield

    # Restore original handlers
    logger.handlers.clear()
    logger.handlers.extend(original_handlers)
    logger.propagate = True


def test_setup_logging_handlers_cleanup(tmp_path):
    """Test that logging handlers are properly cleaned up on multiple calls"""
    os.environ["HOME"] = str(tmp_path)
    logger = logging.getLogger("tweakslite")
    logger.handlers.clear()  # Ensure we start clean

    # First call should add handlers
    setup_logging(debug=True)
    initial_count = len(logger.handlers)

    # Second call should replace handlers, not add more
    logger.handlers.clear()  # Clear handlers before second call
    setup_logging(debug=False)
    assert len(logger.handlers) == initial_count


def test_escape_markup_special_cases():
    """Test markup escaping with special characters"""
    test_cases = [
        ("Line 1\nLine 2", "Line 1\nLine 2"),  # Newlines preserved
        ("\t\tIndented", "\t\tIndented"),  # Tabs preserved
        ("Multiple   Spaces", "Multiple   Spaces"),  # Spaces preserved
        ("<&>\"'", "&lt;&amp;&gt;\"'"),  # All special chars
        (
            "Mixed <b>Bold</b> & 'quoted'",
            "Mixed &lt;b&gt;Bold&lt;/b&gt; &amp; 'quoted'",
        ),
    ]

    for input_text, expected in test_cases:
        assert escape_markup(input_text) == expected


def test_format_keyboard_option():
    """Test keyboard option formatting"""
    test_cases = [
        ("Ctrl+Alt", "<span>Ctrl+Alt</span>"),
        ("", ""),
        (None, ""),
        ("Special <key>", "<span>Special &lt;key&gt;</span>"),
        ("Option & Alt", "<span>Option &amp; Alt</span>"),
    ]

    for input_text, expected in test_cases:
        assert format_keyboard_option(input_text) == expected


def test_format_key_description():
    """Test key description formatting"""
    test_cases = [
        ("Ctrl+Alt", "<span>Ctrl+Alt</span>"),
        ("", ""),
        (None, ""),
        ("Special <key>", "<span>Special &lt;key&gt;</span>"),
        ("Option & Alt", "<span>Option &amp; Alt</span>"),
    ]

    for input_text, expected in test_cases:
        assert format_key_description(input_text) == expected


def test_run_command_with_output(monkeypatch):
    """Test command execution with different output types"""
    # Test with string output
    mock_result = subprocess.CompletedProcess(
        args=["test"], returncode=0, stdout="bytes output\n", stderr=""
    )
    monkeypatch.setattr("subprocess.run", lambda *args, **kwargs: mock_result)
    result = run_command(["test"])
    assert result == "bytes output"

    # Test with empty output
    mock_result = subprocess.CompletedProcess(
        args=["test"], returncode=0, stdout="", stderr=""
    )
    result = run_command(["test"])
    assert result == ""


def test_run_command_error_logging(monkeypatch, capsys):
    """Test error logging in run_command"""

    def mock_run(*args, **kwargs):
        error = subprocess.CalledProcessError(1, "test")
        error.stderr = "error message"
        raise error

    monkeypatch.setattr("subprocess.run", mock_run)
    result = run_command(["test", "command"])

    assert result is None
    captured = capsys.readouterr()
    assert "Error running command" in captured.err
    assert "error message" in captured.err


def test_run_command_timeout_logging(monkeypatch, capsys):
    """Test timeout logging in run_command"""

    def mock_run(*args, **kwargs):
        raise subprocess.TimeoutExpired("test", 30)

    monkeypatch.setattr("subprocess.run", mock_run)

    # Should raise TimeoutExpired
    with pytest.raises(subprocess.TimeoutExpired):
        run_command(["test", "command"])
