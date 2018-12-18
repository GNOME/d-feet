test_conf = configuration_data()
test_conf.set('PYTHON', python_path)
test_conf.set('DATA_DIR', data_dir)
test_conf.set('top_srcdir', source_root)

test_name = 'tests.py'

test_py = configure_file(
  input: test_name + '.in',
  output: '@BASENAME@',
  configuration: test_conf,
)

test(
  test_name,
  test_py,
  workdir: meson.current_source_dir(),
)

run_command(
  find_program('pycodestyle-3', 'pycodestyle', 'pep8'),
  '--exclude=".svn,CVS,.bzr,.hg,.git,__pycache__,.\#*"',
  '--max-line-length=99',
  '--ignore=E123,E402,W504',
  src_dir,
)
