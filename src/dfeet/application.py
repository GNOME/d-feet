# -*- coding: utf-8 -*-

from __future__ import print_function
from gi.repository import Gtk, Gio, GObject, Gdk
from dfeet.window import DFeetWindow
import gettext
import os

_ = gettext.gettext


class DFeetApp(Gtk.Application):

    def __init__(self, package, version, data_dir):
        self.package = package
        self.version = version
        self.data_dir = data_dir
        Gtk.Application.__init__(self, application_id="org.gnome.dfeet",
                                 flags=Gio.ApplicationFlags.FLAGS_NONE)

    # Note that the function in C activate() becomes do_activate() in Python
    def do_activate(self):
        self._main_win = DFeetWindow(self, self.version, self.data_dir)

    # Note that the function in C startup() becomes do_startup() in Python
    def do_startup(self):
        Gtk.Application.do_startup(self)

        # create actions
        action = Gio.SimpleAction.new("about", None)
        action.connect("activate", self.action_about_cb)
        self.add_action(action)

        action = Gio.SimpleAction.new("help", None)
        action.connect("activate", self.action_help_cb)
        self.add_action(action)

        action = Gio.SimpleAction.new("quit", None)
        action.connect("activate", self.action_quit_cb)
        self.add_action(action)

    def action_quit_cb(self, action, parameter):
        self.quit()

    def action_about_cb(self, action, parameter):
        aboutdialog = DFeetAboutDialog(self.package, self.version,
                                       self.props.application_id)
        aboutdialog.set_transient_for(self._main_win)
        aboutdialog.show()

    def action_help_cb(self, action, parameter):
        screen = Gdk.Screen.get_default()
        link = "help:d-feet"
        Gtk.show_uri(screen, link, Gtk.get_current_event_time())


class DFeetAboutDialog(Gtk.AboutDialog):
    def __init__(self, package, version, icon_name):
        Gtk.AboutDialog.__init__(self)
        self.set_program_name(_("D-Feet"))
        self.set_version(version)
        self.set_license_type(Gtk.License.GPL_2_0)
        self.set_website("https://wiki.gnome.org/Apps/DFeet/")
        self.set_logo_icon_name(icon_name)
        self.connect("response", self.on_close_cb)

    def on_close_cb(self, action, parameter):
        action.destroy()
