import html
import os
import subprocess
import shlex
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

    # Create console handler with formatting
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)

    # Create file handler
    file_handler = logging.FileHandler(os.path.join(log_dir, "tweakslite.log"))
    file_handler.setLevel(level)

    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    # Add the handlers to the logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

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


def run_command(command, shell=False):
    """Run a command, using flatpak-spawn if in Flatpak environment"""
    if is_flatpak():
        if isinstance(command, str):
            if shell:
                # For dconf commands, handle them with flatpak-spawn
                if command.startswith("dconf write"):
                    # Split only the first three parts (dconf, write, and the key)
                    parts = command.split(None, 2)
                    if len(parts) == 3:
                        key, value = parts[2].split(" ", 1)
                        # Ensure the value is properly quoted for GVariant format
                        if value.startswith("'") and value.endswith("'"):
                            value = value[1:-1]  # Remove existing quotes
                        # Always wrap the value in single quotes for GVariant string format
                        value = f"'{value}'"
                        # Use flatpak-spawn to run dconf
                        full_command = [
                            "flatpak-spawn",
                            "--host",
                            "dconf",
                            "write",
                            key,
                            value,
                        ]
                    else:
                        full_command = [
                            "flatpak-spawn",
                            "--host",
                            "bash",
                            "-c",
                            command,
                        ]
                elif command.startswith("dconf reset"):
                    # Handle dconf reset with flatpak-spawn too
                    parts = command.split()
                    if len(parts) == 3:
                        full_command = [
                            "flatpak-spawn",
                            "--host",
                            "dconf",
                            "reset",
                            parts[2],
                        ]
                    else:
                        full_command = [
                            "flatpak-spawn",
                            "--host",
                            "bash",
                            "-c",
                            command,
                        ]
                else:
                    full_command = ["flatpak-spawn", "--host", "bash", "-c", command]
            else:
                full_command = ["flatpak-spawn", "--host"] + shlex.split(command)
        else:
            # For dbus-send commands, don't use flatpak-spawn
            if (
                isinstance(command, list)
                and len(command) > 0
                and command[0] == "dbus-send"
            ):
                full_command = command
            else:
                full_command = ["flatpak-spawn", "--host"] + command
    else:
        full_command = command

    try:
        logger.debug(
            f"Running command: {' '.join(full_command if isinstance(full_command, list) else [full_command])}"
        )
        result = subprocess.run(
            full_command,
            shell=shell if not is_flatpak() else False,
            check=True,
            capture_output=True,
            text=True,
        )
        if result.stdout:
            logger.debug(f"Command stdout: {result.stdout}")
        if result.stderr:
            logger.debug(f"Command stderr: {result.stderr}")
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        logger.error(f"Error running command: {e}")
        if e.stderr:
            logger.error(f"Command stderr: {e.stderr}")
        return None


def debug_print(*args, **kwargs):
    """
    Wrapper around logger.debug that maintains compatibility with existing code
    while providing proper logging functionality
    """
    message = " ".join(str(arg) for arg in args)
    logger.debug(message)
