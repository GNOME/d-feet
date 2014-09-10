#!/usr/bin/env python
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(__file__, "../../")))

from gi.repository import Gtk
from gi.repository import Gio
from gi.repository import GLib
from dfeet.introspection import AddressInfo
from dfeet.introspection_helper import DBusNode
from dfeet.introspection_helper import DBusInterface
from dfeet.introspection_helper import DBusProperty
from dfeet.introspection_helper import DBusSignal
from dfeet.introspection_helper import DBusMethod
import unittest

XML = """
<node>
  <interface name='org.gnome.d-feet.TestInterface'>
    <method name='HelloWorld'>
      <arg type='s' name='greeting' direction='in'/>
      <arg type='s' name='response' direction='out'/>
    </method>
    <property name="TestString" type="s" access="readwrite"/>
    <property name="TestBool" type="b" access="read"/>
    <property name="TestStruct" type="(suu)" access="read"/>
    <signal name="TestSignal">
      <arg name="SigString" type="s"/>
      <arg name="SigBool" type="b"/>
    </signal>
  </interface>
</node>
"""

DATA_DIR = os.path.abspath("../../data/")


class IntrospectionHelperTest(unittest.TestCase):
    """tests for the introspection helper classes"""
    def setUp(self):
        self.name = "org.gnome.d-feet"
        self.object_path = "/org/gnome/d-feet"
        self.node_info = Gio.DBusNodeInfo.new_for_xml(XML)

    def test_dbus_node_info(self):
        """test DBusNode class"""
        obj_node = DBusNode(self.name, self.object_path, self.node_info)
        self.assertEqual(obj_node.name, self.name)
        self.assertEqual(obj_node.object_path, self.object_path)
        self.assertEqual(len(obj_node.node_info.interfaces), 1)

    def test_dbus_interface(self):
        """test DBusInterface class"""
        obj_node = DBusNode(self.name, self.object_path, self.node_info)
        obj_iface = DBusInterface(obj_node, obj_node.node_info.interfaces[0])
        self.assertEqual(obj_iface.name, self.name)
        self.assertEqual(obj_iface.object_path, self.object_path)
        self.assertEqual(len(obj_iface.iface_info.methods), 1)
        self.assertEqual(len(obj_iface.iface_info.properties), 3)
        self.assertEqual(len(obj_iface.iface_info.signals), 1)

    def test_dbus_property(self):
        """test DBusProperty class"""
        obj_node = DBusNode(self.name, self.object_path, self.node_info)
        obj_iface = DBusInterface(obj_node, obj_node.node_info.interfaces[0])
        obj_prop = DBusProperty(obj_iface, obj_iface.iface_info.properties[0])
        self.assertEqual(obj_prop.name, self.name)
        self.assertEqual(obj_prop.object_path, self.object_path)
        # get the markup string with value for struct prop (see bgo #702593)
        obj_prop = DBusProperty(obj_iface, obj_iface.iface_info.properties[2])
        obj_prop.value = ("string", 1, 2)
        self.assertIn("'string', 1, 2", obj_prop.markup_str)

    def test_dbus_signal(self):
        """test DBusSignal class"""
        obj_node = DBusNode(self.name, self.object_path, self.node_info)
        obj_iface = DBusInterface(obj_node, obj_node.node_info.interfaces[0])
        obj_sig = DBusSignal(obj_iface, obj_iface.iface_info.signals[0])
        self.assertEqual(obj_sig.name, self.name)
        self.assertEqual(obj_sig.object_path, self.object_path)


class AddressInfoTest(unittest.TestCase):
    """tests for the AddressInfo class and the introspection stuff"""

    def setUp(self):
        self.bus = Gio.TestDBus()
        self.bus.unset()
        self.bus.up()

    def tearDown(self):
        self.bus.stop()

    def test_bus(self):
        """introspect a name on the system bus"""
        ai = AddressInfo(DATA_DIR, self.bus.get_bus_address(), None, "org.freedesktop.DBus")

    @unittest.skip("TODO:peer to peer test not implemented")
    def test_peer_to_peer(self):
        """test a p2p connection"""
        # TODO: setup a gdbus server and test a peer to peer connection
        # (see http://developer.gnome.org/gio/unstable/GDBusServer.html#gdbus-peer-to-peer)
        pass

if __name__ == "__main__":
    # run tests
    unittest.main()
