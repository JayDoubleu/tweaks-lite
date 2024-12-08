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

- Python 3.x
- GTK 4.0
- libadwaita 1.0
- GLib 2.0
- dbus-python

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
- meson
- ninja
- python3-devel
- gtk4-devel
- libadwaita-devel

### Flatpak Build
```bash
flatpak-builder --user --install --force-clean build dev.jaydoubleu.tweaks.lite.json
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the GPL-3.0 License - see the [COPYING](COPYING) file for details.

## Acknowledgments

- Inspired by [GNOME Tweaks](https://gitlab.gnome.org/GNOME/gnome-tweaks)
- Built with [GTK4](https://gtk.org/) and [libadwaita](https://gnome.pages.gitlab.gnome.org/libadwaita/)
- Development assisted by Claude 3.5 Sonnet model by Anthropic
- Developed using [Cursor IDE](https://cursor.so/) 