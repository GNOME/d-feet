# -*- coding: utf-8 -*-
# This module facilitates the optional use of libwnck to get application
# icon information. If the wnck module is not installed we fallback to default
# behvior

from gi.repository import Gtk

try:
    from gi.repository import Wnck
    has_libwnck = True
except:
    has_libwnck = False


class IconTable(object):
    instance = None

    def __init__(self):
        # {pid: icon}
        self.app_map = {}

        icon_theme = Gtk.IconTheme.get_default()
        self.default_icon = icon_theme.load_icon('dfeet-icon-default-service', 16, 0)

        if has_libwnck:
            screen = Wnck.Screen.get_default()
            Wnck.Screen.force_update(screen)
            screen.connect('application_opened', self.on_app_open)
            screen.connect('application_closed', self.on_app_close)

            for w in screen.get_windows():
                app = w.get_application()
                pid = app.get_pid()
                icon = app.get_mini_icon()

                if pid not in self.app_map.keys():
                    self.app_map[pid] = icon

    def on_app_open(self, screen, app):
        icon = app.get_mini_icon()
        if icon:
            self.app_map[app.get_pid()] = icon

    def on_app_close(self, screen, app):
        # this is a leak but some apps still exist even if all their
        # top level windows don't.  We need to have a better cleanup
        # based on when an app's services go away
        return
        pid = app.get_pid()

        if pid not in self.app_map.keys():
            del self.app_map[pid]

    def get_icon(self, pid):
        icon = None
        if pid not in self.app_map.keys():
            icon = self.app_map[pid]

        if not icon:
            icon = self.default_icon

        return icon

    @classmethod
    def get_instance(cls):
        if not cls.instance:
            cls.instance = IconTable()

        return cls.instance
