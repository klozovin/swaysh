from datetime import datetime
from threading import Thread
from time import sleep

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("GtkLayerShell", "0.1")

from gi.repository import GLib, Gtk, GtkLayerShell


class Clock(Gtk.Label):
    def __init__(self):
        super().__init__(label="n/a")
        self.thread = Thread(target=self.loop)
        self.thread.daemon = True
        self.thread.start()

    def update_time(self):
        now = datetime.now()
        self.set_text(now.strftime("%H:%M:%S"))

    def loop(self):
        while True:
            sleep(1)
            GLib.idle_add(self.update_time)


class TaskbarWindow(Gtk.Window):
    def __init__(self):
        super().__init__()
        self.connect("destroy", Gtk.main_quit)

        # Use wlr_layer_shell to position the taskbar at the bottom of the screen
        GtkLayerShell.init_for_window(self)
        GtkLayerShell.auto_exclusive_zone_enable(self)
        GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.BOTTOM, True)
        GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.LEFT, True)
        GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.RIGHT, True)

        # Box to keep workspace buttons and blocks
        self.box = Gtk.Box()

        # Workspace buttons
        for i in range(10):
            self.box.pack_start(Gtk.Button(label=f"{i}"), False, True, 0)

        # Blocks
        self.clock = Clock()
        self.box.pack_end(self.clock, False, True, 10)
        self.box.pack_end(Gtk.Label(label="✲ 50"), False, True, 10)
        self.box.pack_end(Gtk.Label(label="𝅘𝅥𝅯 30"), False, True, 10)

        # Add everything to widow
        self.add(self.box)


def main():
    window = TaskbarWindow()
    window.show_all()
    Gtk.main()


if __name__ == '__main__':
    main()
