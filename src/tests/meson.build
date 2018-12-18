test_name = 'tests.py'

test_py = configure_file(
  input: test_name + '.in',
  output: '@BASENAME@',
  configuration: df_conf,
)

test(test_name, test_py)

run_command(
  find_program('pycodestyle-3', 'pycodestyle', 'pep8'),
  '--exclude=".svn,CVS,.bzr,.hg,.git,__pycache__,.\#*"',
  '--max-line-length=99',
  '--ignore=E123,E402,W504',
  src_dir,
)
