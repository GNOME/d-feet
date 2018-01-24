SUBDIRS = icons ui

gsettings_SCHEMAS = org.gnome.d_feet.gschema.xml
@GSETTINGS_RULES@

@INTLTOOL_DESKTOP_RULE@

desktopdir = $(datadir)/applications
desktop_in_files = org.gnome.d_feet.desktop.in
desktop_DATA = $(desktop_in_files:.desktop.in=.desktop)

UPDATE_DESKTOP = if test -z "$(DESTDIR)"; then update-desktop-database $(datadir)/applications || :; fi

@INTLTOOL_XML_RULE@
appdatadir = $(datadir)/metainfo
appdata_DATA = $(appdata_in_files:.xml.in=.xml)
appdata_in_files = org.gnome.d_feet.appdata.xml.in


install-data-hook:
	$(UPDATE_DESKTOP)
uninstall-hook:
	$(UPDATE_DESKTOP)

EXTRA_DIST =			\
	$(desktop_in_files)	\
	$(gsettings_SCHEMAS)	\
	$(appdata_in_files)

CLEANFILES =			\
	$(DESKTOP_FILES)	\
	$(appdata_DATA)

DISTCLEANFILES =		\
	$(desktop_DATA)
