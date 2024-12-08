Name:           tweaks-lite
Version:        1.0.0
Release:        1%{?dist}
Summary:        A lightweight system configuration tool for GNOME

License:        GPL-3.0-or-later
URL:            https://github.com/JayDoubleu/tweaks-lite
Source0:        %{url}/archive/v%{version}/%{name}-%{version}.tar.gz

BuildArch:      noarch
# Essential build system requirements
BuildRequires:  meson >= 1.0.0
BuildRequires:  ninja-build
BuildRequires:  python3-devel

# Required for schema and desktop file validation
BuildRequires:  desktop-file-utils
BuildRequires:  glib2-devel

# Required for translations
BuildRequires:  gettext

# Runtime dependencies - absolute minimum
# For GTK/GLib bindings
Requires:       python3-gobject
# Core GUI toolkit
Requires:       gtk4
# For Adw widgets
Requires:       libadwaita
# For application icons
Requires:       hicolor-icon-theme

%description
Tweaks Lite is a lightweight system configuration tool for GNOME that allows users
to customize advanced GNOME settings. It provides a simple and intuitive interface
for adjusting fonts, appearance, sound, mouse & touchpad, keyboard, windows,
startup applications, and GNOME Shell extensions.

%prep
%autosetup

%build
%meson
%meson_build

%install
%meson_install

# Find translations if they exist
%find_lang %{name} || :

%check
desktop-file-validate %{buildroot}%{_datadir}/applications/dev.jaydoubleu.tweaks.lite.desktop
appstream-util validate-relax --nonet %{buildroot}%{_datadir}/metainfo/dev.jaydoubleu.tweaks.lite.metainfo.xml

%files
%license COPYING
%doc README.md
%{_bindir}/tweaks-lite
%{python3_sitelib}/tweakslite/
%{_datadir}/applications/dev.jaydoubleu.tweaks.lite.desktop
%{_datadir}/metainfo/dev.jaydoubleu.tweaks.lite.metainfo.xml
%{_datadir}/glib-2.0/schemas/dev.jaydoubleu.tweaks.lite.gschema.xml
%{_datadir}/icons/hicolor/*/apps/dev.jaydoubleu.tweaks.lite*.svg
%{_datadir}/dbus-1/services/dev.jaydoubleu.tweaks.lite.service

%changelog
* Wed Mar 13 2024 Jay W <git.jaydoubleu@gmail.com> - 1.0.0-1
- Initial package release 