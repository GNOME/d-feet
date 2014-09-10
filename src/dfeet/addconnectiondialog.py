# -*- coding: utf-8 -*-
from gi.repository import Gtk, Gio
from dfeet.uiloader import UILoader


class AddConnectionDialog:

    def __init__(self, data_dir, parent, address_bus_history=[]):
        ui = UILoader(data_dir, UILoader.UI_ADDCONNECTIONDIALOG)

        self.dialog = ui.get_root_widget()

        # get the hbox and add address combo box with model
        hbox1 = ui.get_widget('hbox1')
        self.address_combo_box_store = Gtk.ListStore(str)
        self.address_combo_box = Gtk.ComboBox.new_with_model_and_entry(
            self.address_combo_box_store)
        self.address_combo_box.set_entry_text_column(0)
        self.label_status = ui.get_widget('label_status')

        hbox1.pack_start(self.address_combo_box, True, True, 0)
        hbox1.show_all()

        # add history to model
        for el in address_bus_history:
            self.address_combo_box_store.append([el])

        self.dialog.add_button('gtk-cancel', Gtk.ResponseType.CANCEL)
        self.dialog.add_button('gtk-connect', Gtk.ResponseType.OK)

    @property
    def address(self):
        tree_iter = self.address_combo_box.get_active_iter()
        if tree_iter is not None:
            model = self.address_combo_box.get_model()
            return model[tree_iter][0]
        else:
            entry = self.address_combo_box.get_child()
            return entry.get_text()

    def run(self):
        response = self.dialog.run()
        if response == Gtk.ResponseType.CANCEL:
            return response
        elif response == Gtk.ResponseType.OK:
            # check if given address is valid
            try:
                is_supported = Gio.dbus_is_supported_address(self.address)
            except Exception as e:
                self.label_status.set_text(str(e))
                self.run()
            else:
                return Gtk.ResponseType.OK

    def destroy(self):
        self.dialog.destroy()
