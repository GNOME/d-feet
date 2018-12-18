subdir('icons')
subdir('ui')

desktop_conf = configuration_data()
desktop_conf.set('PACKAGE', df_name)

desktop = df_namespace + '.desktop'

desktop_in = configure_file(
  input: desktop + '.in.in',
  output: '@BASENAME@',
  configuration: desktop_conf,
)

custom_target(
  desktop,
  input: desktop_in,
  output: '@BASENAME@',
  command: intltool_desktop_cmd,
  install: true,
  install_dir: df_datadir / 'applications',
)

appdata = df_namespace + '.appdata.xml'

custom_target(
  appdata,
  input: appdata + '.in',
  output: '@BASENAME@',
  command: intltool_xml_cmd,
  install: true,
  install_dir: df_datadir / 'metainfo',
)

install_data(
  df_namespace + '.gschema.xml',
  install_dir: gio_schemasdir,
)
