# Contributing to Tweaks Lite

Thank you for your interest in contributing to Tweaks Lite! This document provides guidelines and information for contributors.

## Code of Conduct

This project follows the GNOME Code of Conduct. By participating, you are expected to uphold this code. Please report unacceptable behavior to git.jaydoubleu@gmail.com.

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/your-username/tweaks-lite.git
   cd tweaks-lite
   ```

3. Set up your development environment:
   ```bash
   # Install build dependencies on Fedora
   sudo dnf install meson ninja-build python3-devel gtk4-devel \
                    libadwaita-devel desktop-file-utils gettext

   # Build the project
   meson setup builddir
   cd builddir
   meson compile
   sudo meson install
   ```

## Development Workflow

1. Create a new branch for your feature or bugfix:
   ```bash
   git checkout -b feature-name
   ```

2. Make your changes, following our coding style
3. Write meaningful commit messages using conventional commits:
   ```
   feat: add new feature
   fix: resolve specific issue
   docs: update documentation
   style: formatting changes
   refactor: code restructuring
   test: add or modify tests
   chore: maintenance tasks
   ```

4. Push to your fork and submit a Pull Request

## Coding Style

- Follow PEP 8 for Python code
- Use 4 spaces for indentation (no tabs)
- Maximum line length of 80 characters
- Use meaningful variable and function names
- Add docstrings for classes and functions
- Include type hints where appropriate

## Testing

Before submitting a PR:
1. Ensure your code builds without warnings
2. Test your changes thoroughly
3. Update documentation if needed
4. Add tests for new functionality

## Building Packages

### Flatpak 