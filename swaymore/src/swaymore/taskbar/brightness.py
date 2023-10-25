import subprocess
import threading
from concurrent.futures import ThreadPoolExecutor

from gi.repository import GLib, Gtk

thread_pool = ThreadPoolExecutor(max_workers=None, thread_name_prefix="swm_")


def threaded(block):
    def wrapper(*args, **kwargs):
        thread_pool.submit(block, *args, **kwargs)

    return wrapper


class Brightness(Gtk.Label):
    def __init__(self):
        super().__init__(label="✲ n/a")
        print(threading.get_ident())
        self.update_backlight_level()

    @threaded
    def update_backlight_level(self):
        current, percent, max = self._brightnessctl_info()
        print(percent)
        GLib.idle_add(lambda: self.set_text(f"✲ {percent}"))

    def set_brightness_up(self):
        pass

    def set_brightness_down(self):
        current, percent, max = self._brightnessctl_info()
        if percent <= 1:
            change = 0
        elif 1 < percent <= 10:
            change = 1
        elif 10 < percent <= 20:
            change = 2
        else:
            change = 5
        self._brightnessctl_set(percent - change)

    def _brightnessctl_info(self) -> tuple[int, int, int]:
        backlight_info = (subprocess
                          .run(["brightnessctl", "-m", "info"], capture_output=True)
                          .stdout
                          .decode("utf-8")
                          .strip()
                          .split(","))
        (device, type, current_brightness, percentage, max_brightness) = backlight_info
        current_brightness: int = int(current_brightness)
        percentage: int = int(percentage.strip("%"))
        max_brightness = int(max_brightness)
        return current_brightness, percentage, max_brightness

    def _brightnessctl_set(self, percentage: int) -> None:
        result = (subprocess
                  .run(["brightnessctl", "-m", "set", f"{percentage}%"], capture_output=True)
                  .stdout
                  .decode("utf-8")
                  .strip()
                  .split(","))
        new_percent = int(result[3].strip("%"))
        # TODO: raise warning instead of asserting
        assert percentage == new_percent
