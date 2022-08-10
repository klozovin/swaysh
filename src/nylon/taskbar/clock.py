from datetime import datetime
from threading import Thread
from time import sleep

from gi.repository import GLib, Gtk


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