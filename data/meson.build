subdir('icons')
subdir('ui')

desktop = df_namespace + '.desktop'

desktop_in = configure_file(
  input: desktop + '.in.in',
  output: '@BASENAME@',
  configuration: df_conf,
)

i18n.merge_file(
  desktop,
  type: 'desktop',
  input: desktop_in,
  output: '@BASENAME@',
  po_dir: po_dir,
  install: true,
  install_dir: df_datadir / 'applications',
)

appdata = df_namespace + '.appdata.xml'

i18n.merge_file(
  appdata,
  input: appdata + '.in',
  output: '@BASENAME@',
  po_dir: po_dir,
  install: true,
  install_dir: df_datadir / 'metainfo',
)

install_data(
  df_namespace + '.gschema.xml',
  install_dir: gio_schemasdir,
)
