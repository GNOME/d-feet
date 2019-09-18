# -*- coding: utf-8 -*-
# copyright (C) 2013 Thomas Bechtold <thomasbechtold@jpberlin.de>

# This file is part of D-Feet.

# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

from gi.repository import GObject, Gtk, Gio

import gettext
from gettext import gettext as _
gettext.textdomain('d-feet')

from dfeet.bus_watch import BusWatch
from dfeet.settings import Settings
from dfeet.addconnectiondialog import AddConnectionDialog

@Gtk.Template(resource_path='/org/gnome/dfeet/mainwindow.ui')
class DFeetWindow(Gtk.ApplicationWindow):
    """the main window"""
    __gtype_name__ = 'DFeetWindow'
    
    buses_stack = Gtk.Template.Child()

    HISTORY_MAX_SIZE = 10

    def __init__(self):
        super(DFeetWindow, self).__init__()
        self.init_template('DFeetWindow')

        self.session_bus = None
        self.system_bus = None
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
        self.set_default_size(int(settings.general['windowwidth']),
                              int(settings.general['windowheight']))

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
    
    @Gtk.Template.Callback('stack_child_added')
    def __stack_child_added_cb(self, stack, child):
        existing = self.lookup_action('close-bus')
        if existing is None:
            action = Gio.SimpleAction.new('close-bus', None)
            action.connect('activate', self.__action_close_bus_cb)
            self.add_action(action)

    @Gtk.Template.Callback('stack_child_removed')
    def __stack_child_removed_cb(self, stack, child):
        current = self.buses_stack.get_visible_child()
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

    def __action_connect_system_bus_cb(self, action, parameter):
        """connect to system bus"""
        try:
            if self.system_bus is not None:
                return
            bw = BusWatch(Gio.BusType.SYSTEM)
            self.system_bus = bw.box_bus
            self.buses_stack.add_titled(self.system_bus, 'System Bus', 'System Bus')
            self.remove_action('connect-system-bus')
        except Exception as e:
            print(e)

    def __action_connect_session_bus_cb(self, action, parameter):
        """connect to session bus"""
        try:
            if self.session_bus is not None:
                return
            bw = BusWatch(Gio.BusType.SESSION)
            self.session_bus = bw.box_bus
            self.buses_stack.add_titled(self.session_bus, 'Session Bus', 'Session Bus')
            self.remove_action('connect-session-bus')
        except Exception as e:
            print(e)

    def __action_connect_other_bus_cb(self, action, parameter):
        """connect to other bus"""
        dialog = AddConnectionDialog(self, self.bus_history)
        result = dialog.start()
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
                    bw = BusWatch(address)
                    self.buses_stack.add_titled(bw.box_bus, address, address)
                    # Fill history
                    if address in self.bus_history:
                        self.bus_history.remove(address)
                    self.bus_history.insert(0, address)
                    # Truncating history
                    if (len(self.bus_history) > self.HISTORY_MAX_SIZE):
                        self.bus_history = self.bus_history[0:self.HISTORY_MAX_SIZE]
                except Exception as e:
                    print("can not connect to '%s': %s" % (address, str(e)))
        dialog.quit()

    def __action_close_bus_cb(self, action, parameter):
        """close current bus"""
        try:
            current = self.buses_stack.get_visible_child()
            self.buses_stack.remove(current)
        except Exception as e:
            print(e)

    @Gtk.Template.Callback('window_deleted')
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
