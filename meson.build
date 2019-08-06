project(
  'd-feet',
  version: '0.3.15',
  license: 'GPL2',
  meson_version: '>= 0.50.0',
)

df_name = meson.project_name()

df_prefix = get_option('prefix')
df_bindir = get_option('bindir')
df_datadir = get_option('datadir')
df_libdir = get_option('libdir')

df_pkgdatadir = df_datadir / df_name
df_pkglibdir = df_libdir / df_name

df_namespace = 'org.gnome.dfeet'

gnome = import('gnome')
i18n = import('i18n')
python = import('python').find_installation('python3')

# FIXME: workaround for missing path method
#        https://github.com/mesonbuild/meson/pull/4616
python_path = find_program('python3').path()

source_root = meson.current_source_dir()

data_dir = source_root / 'data'
po_dir = source_root / 'po'
src_dir = source_root / 'src'

top_inc = include_directories('.')

df_conf = configuration_data()

values = [
  # python
  ['PYTHON', python_path],
  ['pythondir', python.get_install_dir()],
  # directories
  ['pkglibdir', df_prefix / df_pkglibdir],
  ['pkgdatadir', df_prefix / df_pkgdatadir],
  # package
  ['PACKAGE_NAME', df_name],
  ['PACKAGE_VERSION', meson.project_version()],
  # i18n
  ['GETTEXT_PACKAGE', df_name],
]

foreach value: values
  df_conf.set(value[0], value[1])
endforeach

# just check that they exist
dependency('gtk+-3.0', version: '>= 3.9.4')
dependency('gobject-introspection-1.0', version: '>= 0.9.6')

gio_schemasdir = dependency('gio-2.0').get_pkgconfig_variable(
  'schemasdir',
  define_variable: ['datadir', df_prefix / df_datadir],
  default: df_prefix / df_datadir / 'glib-2.0/schemas',
)

subdir('po')
subdir('src')
subdir('data')
subdir('help')

meson.add_install_script(
  'meson_post_install.py',
  df_datadir,
  gio_schemasdir,
  python_path,
  python.get_install_dir(),
)
