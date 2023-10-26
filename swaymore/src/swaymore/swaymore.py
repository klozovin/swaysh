import gi
gi.require_version("Gtk", "3.0")

from gi.repository import Gtk
from .remote import RemoteControl
from .taskbar import TaskbarWindow


class Swaymore:
    def __init__(self):
        self.remote_control = RemoteControl(self)
        self.taskbar = TaskbarWindow()

    def start(self):
        self.remote_control.start()
        self.taskbar.show_all()
        Gtk.main()
