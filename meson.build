project('tweaks-lite',
  version: '1.0.0',
  meson_version: '>= 1.0.0',
  default_options: [ 'warning_level=2', 'werror=false', ],
)

i18n = import('i18n')
gnome = import('gnome')

# Python setup
python = import('python')
python_installation = python.find_installation('python3',
  required: true,
  modules: ['gi']
)

# Dependencies
dependency('gtk4')
dependency('libadwaita-1')

# Installation directories
prefix = get_option('prefix')
bindir = join_paths(prefix, get_option('bindir'))
python_dir = python_installation.get_install_dir()

# Install main executable
install_data(
  'src/main.py',
  install_dir: bindir,
  install_mode: 'rwxr-xr-x',
  rename: ['tweaks-lite']
)

# Install Python package
install_subdir(
  'src/tweakslite',
  install_dir: python_dir
)

# Process subdirectories
subdir('data')
subdir('po')

gnome.post_install(
  glib_compile_schemas: true,
  gtk_update_icon_cache: true,
  update_desktop_database: true,
) 