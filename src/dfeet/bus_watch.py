# -*- coding: utf-8 -*-
from __future__ import print_function

from gi.repository import GObject, Gtk, Gio

from dfeet.uiloader import UILoader
from dfeet.introspection import AddressInfo
from dfeet.wnck_utils import IconTable


class BusNameBox(Gtk.VBox):
    """class to represent a BusName (eg 'org.freedesktop.NetworkManager')"""
    def __init__(self, bus_name, unique_name):
        super(BusNameBox, self).__init__(spacing=5, expand=True)
        self.__bus_name = bus_name
        self.__unique_name = unique_name
        self.__process_id = 0
        self.__command_line = ''
        self.__activatable = False
        self.__icon_table = IconTable.get_instance()
        self.__icon_image = Gtk.Image.new_from_pixbuf(self.__icon_table.default_icon)

        self.__hbox = Gtk.HBox(spacing=5, halign=Gtk.Align.START)
        self.pack_start(self.__hbox, True, True, 0)
        # icon
        self.__hbox.pack_start(self.__icon_image, True, True, 0)
        # other information
        self.__vbox_right = Gtk.VBox(spacing=5, expand=True)
        self.__hbox.pack_start(self.__vbox_right, True, True, 0)

        # first element
        self.__label_bus_name = Gtk.Label()
        self.__label_bus_name.set_halign(Gtk.Align.START)
        self.__vbox_right.pack_start(self.__label_bus_name, True, True, 0)
        # second element
        self.__label_info = Gtk.Label()
        self.__label_info.set_halign(Gtk.Align.START)
        self.__vbox_right.pack_start(self.__label_info, True, True, 0)
        # separator for the boxes
        self.pack_end(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL), True, True, 0)
        # update widget information
        self.__update_widget()
        self.show_all()

    def __update_widget(self):
        """update the widget with the available information"""
        if self.__process_id > 0:
            self.__label_bus_name.set_markup("<b>{0}</b>".format(self.__bus_name))
        else:
            self.__label_bus_name.set_markup("<b><i>{0}</i></b>".format(self.__bus_name))
        # update the label info
        label_info_str = "<small>"
        if self.__activatable:
            label_info_str += "activatable: yes"
        else:
            label_info_str += "activatable: no"
        if self.__process_id:
            label_info_str += ", pid: {0}".format(self.__process_id)
            # get the icon (if available)
            if self.__process_id in self.__icon_table.app_map.keys():
                self.__icon_image.set_from_pixbuf(self.__icon_table.app_map[self.__process_id])
            else:
                self.__icon_image.set_from_pixbuf(self.__icon_table.default_icon)
        if self.__command_line:
            label_info_str += ", cmd: {0}".format(self.__command_line)
        label_info_str += "</small>"
        self.__label_info.set_markup(label_info_str)

    def __repr__(self):
        return "%s (pid: %s)" % (self.__bus_name, self.__process_id)

    def __update_command_line(self):
        """get the command line of process-id is available"""
        if self.__process_id > 0:
            procpath = '/proc/' + str(self.__process_id) + '/cmdline'
            with open(procpath, 'r') as f:
                self.__command_line = " ".join(f.readline().split('\0'))
        else:
            self.__command_line = ''

    @property
    def bus_name(self):
        return self.__bus_name

    @property
    def unique_name(self):
        return self.__unique_name

    @property
    def activatable(self):
        return self.__activatable

    @activatable.setter
    def activatable(self, act_new):
        self.__activatable = act_new

        # update the shown widget
        self.__update_widget()

    @property
    def process_id(self):
        return self.__process_id

    @process_id.setter
    def process_id(self, process_id_new):
        self.__process_id = process_id_new
        try:
            self.__update_command_line()
        except:
            self.__command_line = ''
        # update the shown widget
        self.__update_widget()


class BusWatch(object):
    """watch for a given bus"""
    def __init__(self, data_dir, bus_address):
        self.__data_dir = data_dir
        self.__bus_address = bus_address
        # setup UI
        ui = UILoader(self.__data_dir, UILoader.UI_BUS)
        self.__box_bus = ui.get_root_widget()
        self.__scrolledwindow_listbox = ui.get_widget("scrolledwindow_listbox")
        self.__bus_name_filter = ui.get_widget('entry_filter')
        # create a listbox for all the busnames
        self.__listbox = Gtk.ListBox(hexpand=True, vexpand=True, expand=True)
        self.__listbox.set_sort_func(self.__listbox_sort_by_name, None)
        self.__listbox.set_filter_func(self.__listbox_filter_by_name, None)
        self.__scrolledwindow_listbox.add(self.__listbox)
        self.__scrolledwindow_listbox.show_all()
        # setup the bus connection
        if self.__bus_address == Gio.BusType.SYSTEM or self.__bus_address == Gio.BusType.SESSION:
            # TODO: do this async
            self.connection = Gio.bus_get_sync(self.__bus_address, None)
        elif Gio.dbus_is_supported_address(self.__bus_address):
            # TODO: do this async
            self.connection = Gio.DBusConnection.new_for_address_sync(
                self.__bus_address,
                Gio.DBusConnectionFlags.AUTHENTICATION_CLIENT |
                Gio.DBusConnectionFlags.MESSAGE_BUS_CONNECTION,
                None, None)
        else:
            raise ValueError("Invalid bus address '{0}'".format(self.__bus_address))

        # setup signals
        self.connection.signal_subscribe(None, "org.freedesktop.DBus", "NameOwnerChanged",
                                         None, None, 0, self.__name_owner_changed_cb, None)

        # refilter if someone wants to filter the busbox list
        self.__bus_name_filter.connect("changed",
                                       self.__bus_name_filter_changed_cb)

        # change bus detail tree if a different bus is selected
        self.__listbox.connect("row-selected",
                               self.__listbox_row_selected_cb)

        # TODO: do this async
        self.bus_proxy = Gio.DBusProxy.new_sync(self.connection,
                                                Gio.DBusProxyFlags.NONE,
                                                None,
                                                'org.freedesktop.DBus',
                                                '/org/freedesktop/DBus',
                                                'org.freedesktop.DBus', None)

        # get a list with activatable names
        self.bus_proxy.ListActivatableNames('()',
                                            result_handler=self.__list_act_names_handler,
                                            error_handler=self.__list_act_names_error_handler)

        # list all names
        self.bus_proxy.ListNames('()',
                                 result_handler=self.__list_names_handler,
                                 error_handler=self.__list_names_error_handler)

    @property
    def box_bus(self):
        """the main widget for the bus"""
        return self.__box_bus

    def __bus_name_filter_changed_cb(self, bus_name_filter):
        """someone typed something in the searchbox - refilter"""
        self.__listbox.invalidate_filter()

    def __listbox_row_selected_cb(self, listbox, listbox_row):
        """someone selected a different row of the listbox"""
        childs = self.box_bus.get_children()
        # never remove first element - that's the listbox with the busnames
        if len(childs) > 1:
            self.box_bus.remove(childs[-1])

        try:
            del(self.__addr_info)
        except:
            pass

        # get the selected busname
        if listbox_row:
            row_childs = listbox_row.get_children()
            bus_name_box = row_childs[0]
            # add the introspection info to the left side
            self.__addr_info = AddressInfo(self.__data_dir,
                                           self.__bus_address,
                                           bus_name_box.bus_name,
                                           bus_name_box.unique_name,
                                           connection_is_bus=True)
            self.box_bus.pack_end(self.__addr_info.introspect_box, True, True, 0)
        self.box_bus.show_all()

    def __name_owner_changed_cb(self, connection, sender_name,
                                object_path, interface_name, signal_name,
                                parameters, user_data):
        """bus name added or removed"""
        bus_name = parameters[0]
        old_owner = parameters[1]
        new_owner = parameters[2]

        if bus_name[0] == ':':
            if not old_owner:
                bus_name_box = BusNameBox(bus_name, new_owner)
                self.__listbox_add_bus_name(bus_name_box)
            else:
                self.__listbox_remove_bus_name(bus_name)
        else:
            if new_owner:
                bus_name_box = BusNameBox(bus_name, new_owner)
                self.__listbox_add_bus_name(bus_name_box)
            if old_owner:
                self.__listbox_remove_bus_name(bus_name)

    def __listbox_find_bus_name(self, bus_name):
        """find the given busname in the listbox or return None if not found"""
        for listbox_child in self.__listbox.get_children():
            if listbox_child.get_children()[0].bus_name == bus_name:
                return listbox_child
        # busname not found
        return None

    def __listbox_remove_bus_name(self, bus_name):
        """remove the given busname from the listbox"""
        obj = self.__listbox_find_bus_name(bus_name)
        if obj:
            self.__listbox.remove(obj)
            # if bus is activatable, add the bus name again
            if bus_name in self.__activatable_names:
                bnb = BusNameBox(bus_name, '')
                self.__listbox_add_bus_name(bnb)
        else:
            print("can not remove busname '{0}'. busname not found".format(bus_name))

    def __listbox_add_bus_name(self, bus_name_box):
        """add the given busnamebox to the listbox and update the info"""
        # first check if busname is already listed
        # ie an activatable (but inactive) busname
        bn = self.__listbox_find_bus_name(bus_name_box.bus_name)
        if bn:
            # bus name is already in the list - use this
            bus_name_box = bn.get_children()[0]
        else:
            # add busnamebox to the list
            self.__listbox.add(bus_name_box)

        # update bus info stuff
        self.bus_proxy.GetConnectionUnixProcessID(
            '(s)', bus_name_box.bus_name,
            result_handler=self.__get_unix_process_id_cb,
            error_handler=self.__get_unix_process_id_error_cb,
            user_data=bus_name_box)
        # check if bus name is dbus activatable
        if bus_name_box.bus_name in self.__activatable_names:
            bus_name_box.activatable = True
        else:
            bus_name_box.activatable = False

    def __add_name(self, name, unique_name):
        bus_name_box = BusNameBox(name, unique_name)
        self.__listbox_add_bus_name(bus_name_box)

    def __get_name_owner_cb(self, obj, unique_name, name):
        self.__add_name(name, unique_name)

    def __get_name_owner_error_cb(self, obj, error, name):
        # no name owner, empty unique name
        self.__add_name(name, '')

    def __add_names(self, names):
        for n in names:
            # unique names are added right away
            if n[0] == ':':
                self.__add_name(n, n)
            else:
                self.bus_proxy.GetNameOwner('(s)', n,
                                            result_handler=self.__get_name_owner_cb,
                                            error_handler=self.__get_name_owner_error_cb,
                                            user_data=n)

    def __list_names_handler(self, obj, names, userdata):
        self.__add_names(names)

    def __list_names_error_handler(self, obj, error, userdata):
        print("error getting bus names: %s" % str(error))

    def __list_act_names_handler(self, obj, act_names, userdata):
        # remember the activatable bus names
        self.__activatable_names = act_names
        # add all activatable bus names to the list
        self.__add_names(act_names)

    def __list_act_names_error_handler(self, obj, error, userdata):
        self.__activatable_names = []
        print("error getting activatable names: %s" % str(error))

    def __get_unix_process_id_cb(self, obj, pid, bus_name_box):
        bus_name_box.process_id = pid

    def __get_unix_process_id_error_cb(self, obj, error, bus_name_box):
        # print("error getting unix process id for %s: %s" % (
        #     bus_name_box.bus_name, str(error)))
        bus_name_box.process_id = 0

    def __listbox_filter_by_name(self, row, user_data):
        bus_name_box_list = row.get_children()
        return self.__bus_name_filter.get_text().lower() in bus_name_box_list[0].bus_name.lower()

    def __listbox_sort_by_name(self, row1, row2, user_data):
        """sort function for listbox"""
        child1 = row1.get_children()
        child2 = row2.get_children()
        un1 = child1[0].bus_name
        un2 = child2[0].bus_name

        # covert to integers if comparing two unique names
        if un1[0] == ':' and un2[0] == ':':
            un1 = un1[1:].split('.')
            un1 = tuple(map(int, un1))

            un2 = un2[1:].split('.')
            un2 = tuple(map(int, un2))

        elif un1[0] == ':' and un2[0] != ':':
            return 1
        elif un1[0] != ':' and un2[0] == ':':
            return -1
        else:
            un1 = un1.split('.')
            un2 = un2.split('.')

        if un1 == un2:
            return 0
        elif un1 > un2:
            return 1
        else:
            return -1


if __name__ == "__main__":
    """for debugging"""
    import sys
    import argparse

    parser = argparse.ArgumentParser(description='show a given bus address')
    parser.add_argument('addr')
    p = parser.parse_args()

    if p.addr.lower() == 'system':
        addr = Gio.BusType.SYSTEM
    elif p.addr.lower() == 'session':
        addr = Gio.BusType.SESSION
    else:
        addr = p.addr

    bw = BusWatch(addr)

    win = Gtk.Window()
    win.connect("delete-event", Gtk.main_quit)
    win.set_default_size(1024, 768)
    win.add(bw.box_bus)
    win.show_all()
    try:
        Gtk.main()
    except (KeyboardInterrupt, SystemExit):
        Gtk.main_quit()
