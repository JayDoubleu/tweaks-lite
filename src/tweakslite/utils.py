import html
import os
import subprocess
import logging

# Configure logger
logger = logging.getLogger("tweakslite")


def setup_logging(debug: bool = False):
    """Setup application logging"""
    # Create log directory if it doesn't exist
    log_dir = os.path.expanduser("~/.cache/tweakslite")
    os.makedirs(log_dir, exist_ok=True)

    # Set the logging level
    level = logging.DEBUG if debug else logging.INFO

    # Configure the logger
    logger.setLevel(level)

    # Clear existing handlers
    logger.handlers.clear()

    # Create console handler with formatting
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)

    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    console_handler.setFormatter(formatter)

    # Add console handler first
    logger.addHandler(console_handler)

    try:
        # Create file handler
        file_handler = logging.FileHandler(os.path.join(log_dir, "tweakslite.log"))
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except PermissionError:
        # Continue with just console logging if file handler fails
        pass

    # Prevent the logger from propagating to the root logger
    logger.propagate = False


def escape_markup(text: str) -> str:
    """
    Escapes text for GTK markup using XML/HTML entity escaping.
    """
    if not text:
        return ""

    # Use html.escape to properly handle XML entities
    escaped = html.escape(text, quote=False)
    return escaped


def format_keyboard_option(text: str) -> str:
    """
    Formats keyboard option text for display.
    Uses XML escaping to handle special characters in keyboard descriptions.
    """
    if not text:
        return ""

    # Escape the text and wrap in a span
    escaped = escape_markup(text)
    return f"<span>{escaped}</span>"


def format_key_description(text: str) -> str:
    """
    Legacy function kept for compatibility.
    """
    return format_keyboard_option(text)


def is_flatpak():
    """Check if the application is running inside Flatpak"""
    return os.path.exists("/.flatpak-info")


def run_command(command: list[str], timeout: int = 30) -> str | None:
    """
    Run a command and return its output.
    Returns None if the command fails.
    """
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            check=True,
            shell=False,
            timeout=timeout,
        )
        # Always decode bytes to str
        if result.stdout is None:
            return None
        return result.stdout.decode("utf-8").strip()
    except subprocess.CalledProcessError as e:
        logger.error(f"Error running command: {e}")
        if e.stderr:
            logger.error(f"Command stderr: {e.stderr}")
        return None
    except subprocess.TimeoutExpired as e:
        logger.error(f"Command timed out after {timeout} seconds: {e}")
        return None


def debug_print(*args, **kwargs):
    """
    Wrapper around logger.debug that maintains compatibility with existing code
    while providing proper logging functionality
    """
    message = " ".join(str(arg) for arg in args)
    logger.debug(message)
