icon16_data = files(
  'hicolor/16x16/apps/org.gnome.dfeet.png',
  'hicolor/16x16/apps/dfeet-method-category.png',
  'hicolor/16x16/apps/dfeet-method.png',
  'hicolor/16x16/apps/dfeet-object.png',
  'hicolor/16x16/apps/dfeet-property-category.png',
  'hicolor/16x16/apps/dfeet-property.png',
  'hicolor/16x16/apps/dfeet-signal-category.png',
  'hicolor/16x16/apps/dfeet-signal.png',
  'hicolor/16x16/apps/dfeet-icon-default-service.png',
)

icons = {
  '16x16': icon16_data,
  '24x24': 'hicolor/24x24/apps/org.gnome.dfeet.png',
  '32x32': 'hicolor/32x32/apps/org.gnome.dfeet.png',
  '48x48': 'hicolor/48x48/apps/org.gnome.dfeet.png',
  '256x256': 'hicolor/256x256/apps/org.gnome.dfeet.png',
  'scalable': 'hicolor/scalable/apps/org.gnome.dfeet.svg',
}

foreach size, data: icons
  install_data(
    data,
    install_dir: df_datadir / 'icons/hicolor' / size / 'apps',
  )
endforeach

install_data(
  'HighContrast/scalable/apps/org.gnome.dfeet.svg',
  install_dir: df_datadir / 'icons/HighContrast/scalable/apps',
)
