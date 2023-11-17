import enum
from dataclasses import dataclass
import re
import subprocess
from swaymore.util import thread_pool

from gi.repository import GLib, Gtk


class BatteryState(enum.Enum):
    CHARGING = enum.auto()
    DISCHARGING = enum.auto()


class BatteryInfo:
    state: BatteryState


class Battery(Gtk.Label):
    def __init__(self):
        super().__init__(label="⏻ n/a")
        self.update()
        GLib.timeout_add_seconds(32, self.update)

    def update(self) -> bool:
        status: str
        capacity: int

        with open("/sys/class/power_supply/BAT0/status", "r") as file:
            status = file.read().strip()
        with open("/sys/class/power_supply/BAT0/capacity", "r") as file:
            capacity = int(file.read().strip())

        self.set_text(f"⏻ {status}: {capacity}%")
        return True
