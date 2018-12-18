project(
  'd-feet',
  version: '0.3.15',
  license: 'GPL2',
  meson_version: '>= 0.49.0',
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
pymod = import('python')

python_name = 'python'
python = pymod.find_installation(python_name)
# FIXME: workaround for missing path method
#        https://github.com/mesonbuild/meson/pull/4616
python_path = find_program(python_name).path()

source_root = meson.current_source_dir()

po_dir = source_root / 'po'
src_dir = source_root / 'src'

intltool_merge = find_program('intltool-merge')
intltool_cache = join_paths(po_dir, '.intltool-merge-cache')
intltool_desktop_cmd = [intltool_merge, '-d', '-u', '-c', intltool_cache, po_dir, '@INPUT@', '@OUTPUT@']
intltool_xml_cmd = [intltool_merge, '-x', '-u', '-c', intltool_cache, po_dir, '@INPUT@', '@OUTPUT@']

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
  ['PACKAGE', df_name],
  ['PACKAGE_NAME', df_name],
  ['PACKAGE_VERSION', meson.project_version()],
  # i18n
  ['GETTEXT_PACKAGE', df_name],
]

foreach value: values
  df_conf.set(value[0], value[1])
endforeach

# we only check if these are covered
dependency('gtk+-3.0', version: '>= 3.9.4')
dependency('gobject-introspection-1.0', version: '>= 0.9.6')

gio_schemasdir = dependency('gio-2.0').get_pkgconfig_variable('schemasdir', define_variable: ['datadir', df_prefix / df_datadir])
if gio_schemasdir == ''
  gio_schemasdir = df_prefix / df_datadir / 'glib-2.0/schemas'
endif

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
