from dataclasses import dataclass
import re
import subprocess

from gi.repository import GLib, Gtk


@dataclass
class VolumeResult:
    percent: int
    muted: bool


class Volume(Gtk.Label):
    def __init__(self):
        super().__init__(label="𝅘𝅥𝅯 n/a")
        self._update_volume()

    def volume_up(self):
        self._set_volume(delta=5, direction="+")
        self._update_volume()

    def volume_down(self):
        self._set_volume(delta=5, direction="-")
        self._update_volume()

    def volume_toggle(self):
        self._toggle_mute()
        self._update_volume()

    def _update_volume(self):
        volume = self._get_volume()
        icon = "🔊" if not volume.muted else "🔇"
        self.set_text(f"{icon} {volume.percent}")

    @staticmethod
    def _get_volume() -> VolumeResult:
        command = ["wpctl", "get-volume", "@DEFAULT_AUDIO_SINK@"]
        command_output = subprocess.run(command, capture_output=True, text=True).stdout
        percent, muted = re.search("Volume:\s(\d+\.?\d+)\s?(\[MUTED])?", command_output).groups()
        return VolumeResult(percent=int(float(percent) * 100),
                            muted=True if muted is not None else False)

    def _set_volume(self, delta: int, direction: str):
        command = ["wpctl", "set-volume", "--limit", "1.5", "@DEFAULT_AUDIO_SINK@",
                   f"{str(delta)}%{direction}"]
        print(command)
        subprocess.run(command)
        self._update_volume()

    @staticmethod
    def _toggle_mute():
        command = ["wpctl", "set-mute", "@DEFAULT_AUDIO_SINK@", "toggle"]
        subprocess.run(command)