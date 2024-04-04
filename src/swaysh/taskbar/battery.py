import enum
from dataclasses import dataclass
import os
import re
import subprocess
from typing import Self
from swaysh.util import thread_pool

from gi.repository import GLib, Gtk


class BatteryState(enum.Enum):
    CHARGING = enum.auto()
    DISCHARGING = enum.auto()


class BatteryInfo:
    state: BatteryState



class Battery(Gtk.Label):
    BATTERY_STATUS: str = "/sys/class/power_supply/BAT0/status"
    BATTERY_CAPACITY: str = "/sys/class/power_supply/BAT0/capacity"

    @staticmethod
    def create() -> Self | None:
        if os.path.exists(Battery.BATTERY_STATUS) and os.path.exists(Battery.BATTERY_CAPACITY):
            return Battery()
        else:
            return None

    def __init__(self):
        super().__init__(label="⏻ n/a")
        self.update()
        GLib.timeout_add_seconds(32, self.update)

    def update(self) -> bool:
        status: str
        capacity: int

        with open(Battery.BATTERY_STATUS, "r") as file:
            status = file.read().strip()
        with open(Battery.BATTERY_CAPACITY, "r") as file:
            capacity = int(file.read().strip())

        self.set_text(f"⏻ {status}: {capacity}%")
        return True