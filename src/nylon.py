import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from nylon.taskbar import TaskbarWindow
from nylon.remote import RemoteControl

remote_control = RemoteControl()
taskbar = TaskbarWindow()

remote_control.start()
taskbar.show_all()

Gtk.main()
