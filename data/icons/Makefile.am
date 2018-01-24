icon16dir = $(datadir)/icons/hicolor/16x16/apps
icon16_DATA = \
	hicolor/16x16/apps/org.gnome.d_feet.png \
	hicolor/16x16/apps/dfeet-method-category.png \
	hicolor/16x16/apps/dfeet-method.png \
	hicolor/16x16/apps/dfeet-object.png \
	hicolor/16x16/apps/dfeet-property-category.png \
	hicolor/16x16/apps/dfeet-property.png \
	hicolor/16x16/apps/dfeet-signal-category.png \
	hicolor/16x16/apps/dfeet-signal.png \
	hicolor/16x16/apps/dfeet-icon-default-service.png

icon24dir = $(datadir)/icons/hicolor/24x24/apps
icon24_DATA = hicolor/24x24/apps/org.gnome.d_feet.png

icon32dir = $(datadir)/icons/hicolor/32x32/apps
icon32_DATA = hicolor/32x32/apps/org.gnome.d_feet.png

icon48dir = $(datadir)/icons/hicolor/48x48/apps
icon48_DATA = hicolor/48x48/apps/org.gnome.d_feet.png

#icon64dir = $(datadir)/icons/hicolor/64x64/apps
#icon64_DATA = hicolor/64x64/apps/org.gnome.d_feet.png

#icon128dir = $(datadir)/icons/hicolor/128x128/apps
#icon128_DATA = hicolor/128x128/apps/org.gnome.d_feet.png

icon256dir = $(datadir)/icons/hicolor/256x256/apps
icon256_DATA = hicolor/256x256/apps/org.gnome.d_feet.png

scalabledir = $(datadir)/icons/hicolor/scalable/apps
scalable_DATA = hicolor/scalable/apps/org.gnome.d_feet.svg

scalablehcdir = $(datadir)/icons/HighContrast/scalable/apps
scalablehc_DATA = HighContrast/scalable/apps/org.gnome.d_feet.svg


gtk_update_icon_cache = gtk-update-icon-cache -f -t $(datadir)/icons/hicolor

install-data-hook: update-icon-cache
uninstall-hook: update-icon-cache
update-icon-cache:
	@-if test -z "$(DESTDIR)"; then \
		echo "Updating Gtk icon cache."; \
		$(gtk_update_icon_cache); \
	else \
		echo "*** Icon cache not updated.  After (un)install, run this:"; \
		echo "***   $(gtk_update_icon_cache)"; \
	fi

EXTRA_DIST = \
	$(icon16_DATA)  	\
	$(icon24_DATA)  	\
	$(icon32_DATA)  	\
	$(icon48_DATA)  	\
	$(icon256_DATA)  	\
	$(scalable_DATA)	\
	$(scalablehc_DATA)

