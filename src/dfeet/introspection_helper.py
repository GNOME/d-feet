# -*- coding: utf-8 -*-

from gi.repository import GObject, Gio, Gtk
from dfeet import dbus_utils


def fg_color(widget):
    if widget is None:
        style_context = Gtk.StyleContext()
    else:
        style_context = widget.get_style_context()
    color = style_context.get_color(Gtk.StateFlags.NORMAL)
    return "#%02x%02x%02x" % (
        int(color.red) * 255,
        int(color.green) * 255,
        int(color.blue) * 255,
    )


def args_signature_markup(arg_signature, widget):
    return '<small><span foreground="#2E8B57">%s</span></small>' % (arg_signature)


def args_name_markup(arg_name, widget):
    return '<small><span foreground="%s">%s</span></small>' % (
        fg_color(widget),
        arg_name)


class DBusNode(GObject.GObject):
    """object to represent a DBus Node (object path)"""
    def __init__(self, name, object_path, node_info):
        GObject.GObject.__init__(self)
        self.__name = name
        self.__object_path = object_path
        self.__node_info = node_info  # Gio.GDBusNodeInfo object

    def __repr__(self):
        return "Name: %s ; ObjPath: %s ; NodeInfo: %s" % (
            self.name, self.object_path, self.node_info)

    @property
    def name(self):
        return self.__name

    @property
    def object_path(self):
        return self.__object_path

    @property
    def node_info(self):
        return self.__node_info


class DBusInterface(DBusNode):
    """object to represent a DBus Interface"""
    def __init__(self, dbus_node_obj, iface_info):
        DBusNode.__init__(self, dbus_node_obj.name,
                          dbus_node_obj.object_path, dbus_node_obj.node_info)
        self.__iface_info = iface_info  # Gio.GDBusInterfaceInfo object

    def __repr__(self):
        return "iface '%s' on node '%s'" % (self.iface_info.name, self.node_info.path)

    @property
    def iface_info(self):
        return self.__iface_info


class DBusProperty(DBusInterface):
    """object to represent a DBus Property"""
    def __init__(self, dbus_iface_obj, property_info):
        DBusInterface.__init__(self, dbus_iface_obj, dbus_iface_obj.iface_info)
        self.__property_info = property_info  # Gio.GDBusPropertyInfo object
        self.__value = None  # the value

    def __repr__(self):
        sig = dbus_utils.sig_to_string(self.property_info.signature)
        return "%s %s (%s)" % (sig, self.property_info.name, self.property_info.flags)

    @property
    def property_info(self):
        return self.__property_info

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, new_val):
        self.__value = new_val

    def markup_str(self, widget):
        sig = dbus_utils.sig_to_string(self.property_info.signature)
        readwrite = list()
        if self.readable:
            readwrite.append("read")
        if self.writable:
            readwrite.append("write")
        s = "%s %s <small>(%s)</small>" % (
            args_signature_markup(sig, widget),
            args_name_markup(self.property_info.name, widget),
            " / ".join(readwrite))
        if self.value is not None:
            s += " = %s" % (self.value,)
        return s

    @property
    def readable(self):
        if int(self.property_info.flags) == int(Gio.DBusPropertyInfoFlags.READABLE) or \
                int(self.property_info.flags) == \
                (int(Gio.DBusPropertyInfoFlags.WRITABLE | Gio.DBusPropertyInfoFlags.READABLE)):
            return True
        else:
            return False

    @property
    def writable(self):
        if int(self.property_info.flags) == int(Gio.DBusPropertyInfoFlags.WRITABLE) or \
                int(self.property_info.flags) == \
                (int(Gio.DBusPropertyInfoFlags.WRITABLE | Gio.DBusPropertyInfoFlags.READABLE)):
            return True
        else:
            return False


class DBusSignal(DBusInterface):
    """object to represent a DBus Signal"""
    def __init__(self, dbus_iface_obj, signal_info):
        DBusInterface.__init__(self, dbus_iface_obj,
                               dbus_iface_obj.iface_info)
        self.__signal_info = signal_info  # Gio.GDBusSignalInfo object

    def __repr__(self):
        return "%s" % (self.signal_info.name)

    @property
    def signal_info(self):
        return self.__signal_info

    @property
    def args(self):
        args = list()
        for arg in self.signal_info.args:
            sig = dbus_utils.sig_to_string(arg.signature)
            args.append({'signature': sig, 'name': arg.name})
        return args

    def args_markup_str(self, widget):
        result = ''
        result += '<span foreground="#FF00FF">(</span>'
        result += ', '.join(
            '%s' % (args_signature_markup(arg['signature'], widget))
            for arg in self.args
        )
        result += '<span foreground="#FF00FF">)</span>'
        return result

    def markup_str(self, widget):
        return "%s %s" % (self.signal_info.name, self.args_markup_str(widget))


class DBusMethod(DBusInterface):
    """object to represent a DBus Method"""
    def __init__(self, dbus_iface_obj, method_info):
        DBusInterface.__init__(self, dbus_iface_obj, dbus_iface_obj.iface_info)
        self.__method_info = method_info  # Gio.GDBusMethodInfo object

    def __repr__(self):
        return "%s(%s) ↦ %s (%s)" % (
            self.method_info.name, self.in_args_str,
            self.out_args_str, DBusInterface.__repr__(self))

    @property
    def in_args_code(self):
        in_args = ""
        for a in self.__method_info.in_args:
            in_args += a.signature
        return in_args

    @property
    def method_info(self):
        return self.__method_info

    def markup_str(self, widget):
        return "%s %s <b>↦</b> %s" % (
            self.method_info.name,
            self.in_args_markup_str(widget),
            self.out_args_markup_str(widget),
        )

    @property
    def in_args(self):
        in_args = list()
        for in_arg in self.method_info.in_args:
            sig = dbus_utils.sig_to_string(in_arg.signature)
            in_args.append({'signature': sig, 'name': in_arg.name})
        return in_args

    @property
    def out_args(self):
        out_args = list()
        for out_arg in self.method_info.out_args:
            sig = dbus_utils.sig_to_string(out_arg.signature)
            out_args.append({'signature': sig, 'name': out_arg.name})
        return out_args

    @property
    def in_args_str(self):
        result = ""
        for arg in self.in_args:
            result += "%s %s, " % (arg['signature'], arg['name'])

        return result[0:-2]

    @property
    def out_args_str(self):
        result = ""
        for arg in self.out_args:
            result += "%s %s, " % (arg['signature'], arg['name'])

        return result[0:-2]

    def __args_markup_str(self, args, widget):
        """markup a given list of args"""
        result = ''
        result += '<span foreground="#FF00FF">(</span>'
        result += ', '.join(
            '%s %s' % (
                args_signature_markup(arg['signature'], widget),
                args_name_markup(arg['name'], widget)
            ) for arg in args)
        result += '<span foreground="#FF00FF">)</span>'
        return result

    def in_args_markup_str(self, widget):
        return self.__args_markup_str(self.in_args, widget)

    def out_args_markup_str(self, widget):
        return self.__args_markup_str(self.out_args, widget)


class DBusAnnotation(DBusInterface):
    """object to represent a DBus Annotation"""
    def __init__(self, dbus_iface_obj, annotation_info):
        DBusInterface.__init__(self, dbus_iface_obj,
                               dbus_iface_obj.iface_info)
        self.__annotation_info = annotation_info  # Gio.GDBusAnnotationInfo object

    def __repr__(self):
        return "%s: %s" % (self.annotation_info.key, self.annotation_info.value)

    @property
    def annotation_info(self):
        return self.__annotation_info

    def markup_str(self, widget):
        return "%s: %s" % (self.annotation_info.key, self.annotation_info.value)
