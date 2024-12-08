# Tweaks Lite

A lightweight alternative to GNOME Tweaks, built with GTK4 and libadwaita. This project aims to provide essential GNOME customization options while maintaining minimal dependencies and optimal Flatpak compatibility.

## Features

- 🎨 Appearance customization
- 🔤 Font settings
- 🔊 Sound tweaks
- 🖱️ Mouse and touchpad configuration
- ⌨️ Keyboard settings
- 🪟 Window management options
- 🚀 Startup applications management
- 🧩 GNOME Shell extensions management

## Why Tweaks Lite?

GNOME Tweaks is a powerful tool, but it comes with a large number of dependencies that can be challenging to manage, especially in containerized environments like Flatpak. Tweaks Lite addresses this by:

- Using modern GTK4 and libadwaita instead of GTK3
- Minimizing dependencies to essential components
- Optimizing for Flatpak deployment
- Providing a clean, modern interface
- Following GNOME Human Interface Guidelines (HIG)

## Dependencies

### Runtime Dependencies
- Python 3.x
- GTK 4.0 (gtk4)
- libadwaita 1.0
- GLib 2.0
- python3-gobject >= 3.42.0
- dbus-python

### Build Dependencies
- meson
- ninja
- python3-devel
- gtk4-devel
- libadwaita-devel
- desktop-file-utils
- gettext
- glib2-devel

## Installation

### Flatpak (Recommended)
```bash
flatpak install dev.jaydoubleu.tweaks.lite
```

### From Source
```bash
# Clone the repository
git clone https://github.com/JayDoubleu/tweaks-lite.git
cd tweaks-lite

# Build using Meson
meson setup builddir
cd builddir
meson compile
sudo meson install
```

## Building

### Build Requirements
+ Common requirements for all build methods:
- meson
- ninja
- python3-devel
- gtk4-devel
- libadwaita-devel
+ desktop-file-utils
+ gettext
+ glib2-devel

### Build Methods

#### 1. From Source (Development)
```bash
# Clone the repository
git clone https://github.com/JayDoubleu/tweaks-lite.git
cd tweaks-lite

# Build using Meson
meson setup builddir
cd builddir
meson compile
sudo meson install
```

#### 2. Flatpak Build
You can build and install the Flatpak using either:

```bash
# Simple build
flatpak-builder --user --install --force-clean build dev.jaydoubleu.tweaks.lite.json

# Or use the build script (recommended)
chmod +x scripts/build-flatpak.sh
./scripts/build-flatpak.sh
```

#### 3. RPM Build
To build an RPM package, you'll need the following additional requirements:
- rpm-build
- rpmdevtools

Then you can build the RPM using the provided script:
```bash
chmod +x scripts/build-rpm.sh
./scripts/build-rpm.sh
```

The built RPMs will be available in `~/rpmbuild/RPMS/` and the source RPM in `~/rpmbuild/SRPMS/`.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the GPL-3.0 License - see the [COPYING](COPYING) file for details.

## Acknowledgments

- Inspired by [GNOME Tweaks](https://gitlab.gnome.org/GNOME/gnome-tweaks)
- Built with [GTK4](https://gtk.org/) and [libadwaita](https://gnome.pages.gitlab.gnome.org/libadwaita/)
- Development assisted by Claude 3.5 Sonnet model by Anthropic
- Developed using [Cursor IDE](https://cursor.so/)

### Development Setup with UV

This project uses [UV](https://github.com/astral-sh/uv) for Python package management. UV is a fast, reliable Python package installer and resolver.

#### Setup Development Environment
```bash
# Install the package with development dependencies
uv pip install ".[dev]"

# Activate the virtual environment (if you prefer working in an activated environment)
source .venv/bin/activate
```

#### Development Commands

You can run commands in two ways:

1. With activated virtual environment (after running `source .venv/bin/activate`):
```bash
# Run tests
pytest

# Run linter
ruff check .

# Format code
ruff format .

# Type checking
mypy .
```

2. Without activating (recommended):
```bash
# Run tests
uv run pytest

# Run linter
uv run ruff check .

# Format code
uv run ruff format .

# Type checking
uv run mypy .
```
