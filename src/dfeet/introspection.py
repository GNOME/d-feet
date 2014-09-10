# -*- coding: utf-8 -*-
from __future__ import print_function

from gi.repository import Gtk, Gio, GLib
from dfeet.executemethoddialog import ExecuteMethodDialog

from dfeet.uiloader import UILoader

from dfeet.introspection_helper import DBusNode
from dfeet.introspection_helper import DBusInterface
from dfeet.introspection_helper import DBusProperty
from dfeet.introspection_helper import DBusSignal
from dfeet.introspection_helper import DBusMethod
from dfeet.introspection_helper import DBusAnnotation


class AddressInfo():
    """
    class to handle information about a name (eg "org.freedesktop.NetworkManager")
    on a given address (eg Gio.BusType.SYSTEM or unix:path=/var/run/dbus/system_bus_socket)
    """
    def __del__(self):
        try:
            self.connection.close()
        except:
            pass

    def __init__(self, data_dir, address, name, unique_name, connection_is_bus=True):
        self.data_dir = data_dir
        signal_dict = {
            'treeview_row_activated_cb': self.__treeview_row_activated_cb,
            'treeview_row_expanded_cb': self.__treeview_row_expanded_cb,
            'button_reload_clicked_cb': self.__button_reload_clicked_cb,
            }

        self.address = address  # can be Gio.BusType.SYSTEM or Gio.BusType.SYSTEM or other address
        self.name = name  # the well-known name or None
        self.unique_name = unique_name  # the unique name or None
        self.connection_is_bus = connection_is_bus  # is it a bus or a p2p connection?

        # setup UI
        ui = UILoader(self.data_dir, UILoader.UI_INTROSPECTION)
        self.introspect_box = ui.get_root_widget()  # this is the main box with the treeview
        self.__spinner = ui.get_widget('spinner')  # progress during the introspection
        self.__scrolledwindow = \
            ui.get_widget('scrolledwindow')  # the scrolledwindow contains the treeview
        self.__treemodel = ui.get_widget('treestore')
        self.__treemodel.set_sort_func(0, self.__sort_model)
        self.__treemodel.set_sort_column_id(0, Gtk.SortType.ASCENDING)
        self.__treeview = ui.get_widget('treeview')
        self.__label_name = ui.get_widget('label_name')
        self.__label_unique_name = ui.get_widget('label_unique_name')
        self.__label_address = ui.get_widget('label_address')
        self.__messagedialog = ui.get_widget('messagedialog')
        self.__messagedialog.connect("close", self.__messagedialog_close_cb)
        # connect signals
        ui.connect_signals(signal_dict)
        if self.connection_is_bus:
            # we expect a bus connection
            if self.address == Gio.BusType.SYSTEM or self.address == Gio.BusType.SESSION:
                self.connection = Gio.bus_get_sync(self.address, None)
                self.__label_address.set_text(
                    Gio.dbus_address_get_for_bus_sync(self.address, None))
            elif Gio.dbus_is_address(self.address):
                self.connection = Gio.DBusConnection.new_for_address_sync(
                    self.address,
                    Gio.DBusConnectionFlags.AUTHENTICATION_CLIENT |
                    Gio.DBusConnectionFlags.MESSAGE_BUS_CONNECTION,
                    None, None)
                self.__label_address.set_text(self.address)
            else:
                self.connection = None
                raise Exception("Invalid bus address '%s'" % (self.address))
        else:
            # we have a peer-to-peer connection
            if Gio.dbus_is_supported_address(self.address):
                self.connection = Gio.DBusConnection.new_for_address_sync(
                    self.address,
                    Gio.DBusConnectionFlags.AUTHENTICATION_CLIENT,
                    None, None)
                self.__label_address.set_text(self.address)
            else:
                self.connection = None
                raise Exception("Invalid p2p address '%s'" % (self.address))

        # start processing data
        self.introspect_start()

    def __messagedialog_close_cb(self, dialog):
        self.__messagedialog.destroy()

    def __treeview_row_activated_cb(self, treeview, path, view_column):
        model = treeview.get_model()
        iter_ = model.get_iter(path)

        obj = model.get_value(iter_, 1)

        if isinstance(obj, DBusMethod):
            # execute the selected method
            dialog = ExecuteMethodDialog(
                self.data_dir, self.connection, self.connection_is_bus, self.name, obj)
            dialog.run()
        elif isinstance(obj, DBusProperty):
            # update the selected property (TODO: do this async)
            proxy = Gio.DBusProxy.new_sync(self.connection,
                                           Gio.DBusProxyFlags.NONE,
                                           None,
                                           self.name,
                                           obj.object_path,
                                           "org.freedesktop.DBus.Properties", None)
            args = GLib.Variant('(ss)', (obj.iface_info.name, obj.property_info.name))
            result = proxy.call_sync("Get", args, 0, -1, None)
            # update the object value so markup string is calculated correct
            obj.value = result[0]
            # set new markup string
            model[iter_][0] = obj.markup_str
        else:
            if treeview.row_expanded(path):
                treeview.collapse_row(path)
            else:
                treeview.expand_row(path, False)

    def __treeview_row_expanded_cb(self, treeview, iter_, path):
        model = treeview.get_model()
        node = model.get(iter_, 1)[0]
        if isinstance(node, DBusNode):
            if model.iter_has_child(iter_):
                childiter = model.iter_children(iter_)
                while childiter is not None:
                    childpath = model.get_path(childiter)
                    treeview.expand_to_path(childpath)
                    childiter = model.iter_next(childiter)

    def __sort_model(self, model, iter1, iter2, user_data):
        """objects with small path depth first"""
        un1 = model.get_value(iter1, 0)
        un2 = model.get_value(iter2, 0)

        if un1.startswith("/"):
            un1_depth = len(un1.split("/"))
        else:
            un1_depth = 1
        if un2.startswith("/"):
            un2_depth = len(un2.split("/"))
        else:
            un2_depth = 1

        if un1_depth > un2_depth:
            return 1
        elif un1_depth < un2_depth:
            return -1
        else:
            return un1 > un2

    def introspect_start(self):
        """introspect the given bus name and update the tree model"""
        # cleanup current tree model
        self.__treemodel.clear()
        # start introspection
        self.__dbus_node_introspect("/")

    def __button_reload_clicked_cb(self, widget):
        """reload the introspection data"""
        self.introspect_start()

    def __dbus_node_introspect_cb(self, connection, result_async, object_path):
        """callback when Introspect dbus function call finished"""
        try:
            res = connection.call_finish(result_async)
        except Exception as e:
            # got an exception (eg dbus timeout). show the exception
            self.__messagedialog.set_title("DBus Exception")
            self.__messagedialog.set_property("text", "%s : %s" % (self.name, str(e)))
            self.__messagedialog.run()
            self.__messagedialog.destroy()
        else:
            # we got a valid result from dbus call! Create nodes and add to treemodel
            node_info = Gio.DBusNodeInfo.new_for_xml(res[0])
            # create a GObject node and add to tree-model
            tree_iter = None
            if len(node_info.interfaces) > 0:
                node_obj = DBusNode(self.name, object_path, node_info)
                tree_iter = self.__treemodel.append(tree_iter, ["%s" % object_path, node_obj])
                # tree_iter = self.__treemodel.append(tree_iter, ["Hallo", None])

                # append interfaces to tree model
                name_iter = self.__treemodel.append(tree_iter,
                                                    ["<b>Interfaces</b>", None])
                for iface in node_info.interfaces:
                    iface_obj = DBusInterface(node_obj, iface)
                    iface_iter = self.__treemodel.append(
                        name_iter,
                        ["%s" % iface.name, iface_obj])
                    # interface methods
                    if len(iface.methods) > 0:
                        iface_methods_iter = self.__treemodel.append(
                            iface_iter, ["<b>Methods</b>", None])
                        for iface_method in iface.methods:
                            method_obj = DBusMethod(iface_obj, iface_method)
                            self.__treemodel.append(
                                iface_methods_iter,
                                ["%s" % method_obj.markup_str, method_obj])
                    # interface signals
                    if len(iface.signals) > 0:
                        iface_signals_iter = self.__treemodel.append(
                            iface_iter, ["<b>Signals</b>", None])
                        for iface_signal in iface.signals:
                            signal_obj = DBusSignal(iface_obj, iface_signal)
                            self.__treemodel.append(
                                iface_signals_iter,
                                ["%s" % signal_obj.markup_str, signal_obj])
                    # interface properties
                    if len(iface.properties) > 0:
                        iface_properties_iter = self.__treemodel.append(
                            iface_iter, ["<b>Properties</b>", None])
                        for iface_property in iface.properties:
                            property_obj = DBusProperty(iface_obj, iface_property)
                            self.__treemodel.append(
                                iface_properties_iter,
                                ["%s" % property_obj.markup_str, property_obj])
                    # interface annotations
                    if len(iface.annotations) > 0:
                        iface_annotations_iter = self.__treemodel.append(
                            iface_iter, ["<b>Annotations</b>", None])
                        for iface_annotation in iface.annotations:
                            annotation_obj = DBusAnnotation(iface_obj, iface_annotation)
                            self.__treemodel.append(
                                iface_annotations_iter,
                                ["%s" % (annotation_obj.markup_str), annotation_obj])

            # are more nodes left?
            if len(node_info.nodes) > 0:
                for node in node_info.nodes:
                    # node_iter = self.__treemodel.append(tree_iter, [node.path, node])
                    if object_path == "/":
                        object_path = ""
                    object_path_new = object_path + "/" + node.path
                    self.__dbus_node_introspect(object_path_new)
            else:
                # no nodes left. we finished the introspection
                self.__spinner.stop()
                self.__spinner.set_visible(False)
                # update name, unique name, ...
                self.__label_name.set_text(self.name)
                self.__label_unique_name.set_text(self.unique_name)

                self.introspect_box.show_all()

    def __dbus_node_introspect(self, object_path):
        """Introspect the given object path. This function will be called recursive"""
        # start spinner
        self.__spinner.start()
        self.__spinner.set_visible(True)
        # start async dbus call
        self.connection.call(
            self.name, object_path, 'org.freedesktop.DBus.Introspectable', 'Introspect',
            None, GLib.VariantType.new("(s)"), Gio.DBusCallFlags.NONE, -1,
            None, self.__dbus_node_introspect_cb, object_path)


if __name__ == "__main__":
    """for debugging"""
    import argparse

    parser = argparse.ArgumentParser(description='introspect a given dbus address and name')
    parser.add_argument('-p', '--p2p', action='store_true', default=False)
    parser.add_argument('addr')
    parser.add_argument('name')
    p = parser.parse_args()

    if p.addr.lower() == 'system':
        addr = Gio.BusType.SYSTEM
    elif p.addr.lower() == 'session':
        addr = Gio.BusType.SESSION
    else:
        addr = p.addr

    name = p.name
    ai = AddressInfo(addr, name, None, not p.p2p)
    win = Gtk.Window()
    win.connect("delete-event", Gtk.main_quit)
    win.set_default_size(1024, 768)
    win.add(ai.introspect_box)
    win.show_all()
    try:
        Gtk.main()
    except (KeyboardInterrupt, SystemExit):
        Gtk.main_quit()
