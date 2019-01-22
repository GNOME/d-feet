TESTS = tests.py

check_SCRIPTS = tests.py

EXTRA_DIST = tests.py.in
CLEANFILES = $(check_SCRIPTS)

tests.py: tests.py.in
	$(AM_V_GEN) sed -e 's|@PYTHON[@]|$(PYTHON)|g' \
			-e 's|@DATA_DIR[@]|..\/..\/data|g' \
			-e 's|@top_srcdir[@]|$(top_srcdir)|g' $< > $@
	chmod +x $@

# Default pycodestyle --exclude + emacs backup files
PYCODESTYLE_EXCLUDES=--exclude='.svn,CVS,.bzr,.hg,.git,__pycache__,.\#*'

check-local:
	$(PYCODESTYLE) --max-line-length=99 --ignore=E123,E402,W504 \
		$(PYCODESTYLE_EXCLUDES) $(top_srcdir)/src/
