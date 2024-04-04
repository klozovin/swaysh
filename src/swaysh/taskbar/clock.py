from datetime import datetime

from gi.repository import GLib, Gtk


class Clock(Gtk.Label):
    def __init__(self):
        super().__init__(label="n/a")
        self.update_time()
        GLib.timeout_add(1000, self.update_time)

    def update_time(self) -> bool:
        self.set_text(datetime.now().strftime("%a, w%V: %-d.%-m.%y | %H:%M"))
        return True
