import enum
from dataclasses import dataclass
import os
import re
import subprocess
from swaysh.util import thread_pool

from gi.repository import GLib, Gtk


class BatteryState(enum.Enum):
    CHARGING = enum.auto()
    DISCHARGING = enum.auto()


class BatteryInfo:
    state: BatteryState



class Battery(Gtk.Label):

    BATTERY_STATUS = "/sys/class/power_supply/BAT0/status"
    BATTERY_CAPACITY = "/sys/class/power_supply/BAT0/capacity"

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


def createBattery() -> Battery | None:
    if os.path.exists(Battery.BATTERY_STATUS) and os.path.exists(Battery.BATTERY_CAPACITY):
        return Battery()
    else:
        return None