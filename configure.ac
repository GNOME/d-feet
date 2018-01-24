AC_PREREQ([2.64])
AC_INIT([d-feet],
	[0.3.14],
	[http://bugzilla.gnome.org/enter_bug.cgi?product=d-feet],
        [d-feet],
        [https://wiki.gnome.org/Apps/DFeet])
AC_CONFIG_AUX_DIR([build-aux])
AC_CONFIG_MACRO_DIR([m4])

AM_INIT_AUTOMAKE([1.11 -Wall foreign no-define tar-ustar no-dist-gzip dist-xz])

GLIB_GSETTINGS

PKG_PROG_PKG_CONFIG

YELP_HELP_INIT

AM_PATH_PYTHON([2.7])

PKG_CHECK_MODULES(DFEET, [
  gtk+-3.0 >= 3.9.4
])

AC_ARG_ENABLE(tests,
  AS_HELP_STRING([--disable-tests],
                 [do not run tests]),
    enable_tests=$enableval, enable_tests=yes)

if test x$enable_tests = xyes; then
  AC_CHECK_PROG([PEP8], [pep8], [yes])
  test -z "$PEP8" && AC_MSG_ERROR([pep8 binary not found but needed for testsuite. either install it or run with the argument --disable-tests to not run the testsuite.])
fi
AM_CONDITIONAL(ENABLE_TESTS, test "x$enable_tests" = "xyes")

# i18n stuff
IT_PROG_INTLTOOL([0.40.0])

GETTEXT_PACKAGE=AC_PACKAGE_NAME
AC_SUBST(GETTEXT_PACKAGE)
AC_DEFINE_UNQUOTED(GETTEXT_PACKAGE,"$GETTEXT_PACKAGE", [Package name for gettext])

GOBJECT_INTROSPECTION_REQUIRE([0.9.6])

AC_CONFIG_FILES([
	Makefile
	po/Makefile.in
	src/Makefile
	src/dfeet/Makefile
	src/tests/Makefile
	data/Makefile
	data/org.gnome.d_feet.desktop.in
	data/icons/Makefile
	data/ui/Makefile
	help/Makefile
])

AC_OUTPUT
