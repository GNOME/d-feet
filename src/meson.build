configure_file(
  input: df_name + '.in',
  output: '@BASENAME@',
  configuration: df_conf,
  install: true,
  install_dir: df_bindir,
)

subdir('dfeet')

if get_option('tests')
  subdir('tests')
endif
