# -*- coding: utf-8 -*-
# Copyright (C) 2013 Thomas Bechtold <thomasbechtold@jpberlin.de>

# This file is part of D-Feet.

# D-Feet is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# D-Feet is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with D-Feet.  If not, see <http://www.gnu.org/licenses/>.

from gi.repository import GObject, Gtk, Gio

import gettext
from gettext import gettext as _
gettext.textdomain('d-feet')

from dfeet.bus_watch import BusWatch
from dfeet.settings import Settings
from dfeet.uiloader import UILoader
from dfeet.addconnectiondialog import AddConnectionDialog
from dfeet.executemethoddialog import ExecuteMethodDialog


class DFeetWindow(Gtk.ApplicationWindow):
    """the main window"""

    HISTORY_MAX_SIZE = 10

    def __init__(self, app, package, version, data_dir):
        Gtk.Window.__init__(self, application=app)
        self.package = package
        self.version = version
        self.data_dir = data_dir
        self.session_bus = None
        self.system_bus = None

        # setup the window
        self.set_default_size(600, 480)
        self.set_icon_name(package)

        # create actions
        action = Gio.SimpleAction.new('connect-system-bus', None)
        action.connect('activate', self.__action_connect_system_bus_cb)
        self.add_action(action)

        action = Gio.SimpleAction.new('connect-session-bus', None)
        action.connect('activate', self.__action_connect_session_bus_cb)
        self.add_action(action)

        action = Gio.SimpleAction.new('connect-other-bus', None)
        action.connect('activate', self.__action_connect_other_bus_cb)
        self.add_action(action)

        # get settings
        settings = Settings.get_instance()
        self.connect('delete-event', self.__delete_cb)
        self.set_default_size(int(settings.general['windowwidth']),
                              int(settings.general['windowheight']))

        # setup ui
        ui = UILoader(self.data_dir, UILoader.UI_MAINWINDOW)
        header = ui.get_widget('headerbar')
        self.set_titlebar(header)
        self.stack = ui.get_widget('buses_stack')
        self.add(self.stack)
        self.__stack_child_added_id = self.stack.connect('add', self.__stack_child_added_cb)
        self.__stack_child_removed_id = self.stack.connect('remove', self.__stack_child_removed_cb)
        self.connect('destroy', self.__on_destroy)

        # create bus history list and load entries from settings
        self.__bus_history = []
        for bus in settings.general['addbus_list']:
            if bus != '':
                self.__bus_history.append(bus)

        # add a System and Session Bus tab
        self.activate_action('connect-system-bus', None)
        self.activate_action('connect-session-bus', None)

        self.show_all()

    @property
    def bus_history(self):
        return self.__bus_history

    @bus_history.setter
    def bus_history(self, history_new):
        self.__bus_history = history_new

    def __stack_child_added_cb(self, stack, child):
        existing = self.lookup_action('close-bus')
        if existing is None:
            action = Gio.SimpleAction.new('close-bus', None)
            action.connect('activate', self.__action_close_bus_cb)
            self.add_action(action)

    def __stack_child_removed_cb(self, stack, child):
        current = self.stack.get_visible_child()
        if current is None:
            self.remove_action('close-bus')

        if child == self.system_bus:
            self.system_bus = None
            # Re-enable the action
            action = Gio.SimpleAction.new('connect-system-bus', None)
            action.connect('activate', self.__action_connect_system_bus_cb)
            self.add_action(action)
        elif child == self.session_bus:
            self.session_bus = None
            # Re-enable the action
            action = Gio.SimpleAction.new('connect-session-bus', None)
            action.connect('activate', self.__action_connect_session_bus_cb)
            self.add_action(action)

    def __on_destroy(self, data=None):
        self.stack.disconnect(self.__stack_child_added_id)
        self.stack.disconnect(self.__stack_child_removed_id)

    def __action_connect_system_bus_cb(self, action, parameter):
        """connect to system bus"""
        try:
            if self.system_bus is not None:
                return
            bw = BusWatch(self.data_dir, Gio.BusType.SYSTEM)
            self.system_bus = bw.box_bus
            self.stack.add_titled(self.system_bus, 'System Bus', 'System Bus')
            self.remove_action('connect-system-bus')
        except Exception as e:
            print(e)

    def __action_connect_session_bus_cb(self, action, parameter):
        """connect to session bus"""
        try:
            if self.session_bus is not None:
                return
            bw = BusWatch(self.data_dir, Gio.BusType.SESSION)
            self.session_bus = bw.box_bus
            self.stack.add_titled(self.session_bus, 'Session Bus', 'Session Bus')
            self.remove_action('connect-session-bus')
        except Exception as e:
            print(e)

    def __action_connect_other_bus_cb(self, action, parameter):
        """connect to other bus"""
        dialog = AddConnectionDialog(self.data_dir, self, self.bus_history)
        result = dialog.run()
        if result == Gtk.ResponseType.OK:
            address = dialog.address
            if address == 'Session Bus':
                self.activate_action('connect-session-bus', None)
                return
            elif address == 'System Bus':
                self.activate_action('connect-system-bus', None)
                return
            else:
                try:
                    bw = BusWatch(self.data_dir, address)
                    self.stack.add_titled(bw.box_bus, address, address)
                    # Fill history
                    if address in self.bus_history:
                        self.bus_history.remove(address)
                    self.bus_history.insert(0, address)
                    # Truncating history
                    if (len(self.bus_history) > self.HISTORY_MAX_SIZE):
                        self.bus_history = self.bus_history[0:self.HISTORY_MAX_SIZE]
                except Exception as e:
                    print("can not connect to '%s': %s" % (address, str(e)))
        dialog.destroy()

    def __action_close_bus_cb(self, action, parameter):
        """close current bus"""
        try:
            current = self.stack.get_visible_child()
            self.stack.remove(current)
        except Exception as e:
            print(e)

    def __delete_cb(self, main_window, event):
        """store some settings"""
        settings = Settings.get_instance()
        size = main_window.get_size()
        pos = main_window.get_position()

        settings.general['windowwidth'] = size[0]
        settings.general['windowheight'] = size[1]

        self.bus_history = self.bus_history[0:self.HISTORY_MAX_SIZE]

        settings.general['addbus_list'] = self.bus_history
        settings.write()
