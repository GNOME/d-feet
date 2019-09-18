# -*- coding: utf-8 -*-
from gi.repository import Gtk, Gio

@Gtk.Template(resource_path='/org/gnome/dfeet/addconnectiondialog.ui')
class AddConnectionDialog(Gtk.Dialog):
    __gtype_name__ = 'AddConnectionDialog'

    label_status = Gtk.Template.Child()
    address_combo_box = Gtk.Template.Child()
    def __init__(self, parent, address_bus_history=[]):
        super(AddConnectionDialog, self).__init__()
        self.init_template('AddConnectionDialog')

        self.set_transient_for(parent)
        address_combo_box_store = Gtk.ListStore(str)
        # add history to model
        for el in address_bus_history:
            address_combo_box_store.append([el])

        self.address_combo_box.set_model(address_combo_box_store)
        

    @property
    def address(self):
        tree_iter = self.address_combo_box.get_active_iter()
        if tree_iter is not None:
            model = self.address_combo_box.get_model()
            return model[tree_iter][0]
        else:
            entry = self.address_combo_box.get_child()
            return entry.get_text()

    def start(self):
        response = self.run()
        if response == Gtk.ResponseType.CANCEL:
            return response
        elif response == Gtk.ResponseType.OK:
            # check if given address is valid
            try:
                Gio.dbus_is_supported_address(self.address)
            except Exception as e:
                self.label_status.set_text(str(e))
                self.run()
            else:
                return Gtk.ResponseType.OK

    def quit(self):
        self.destroy()
