from __future__ import annotations
import os
import threading
from typing import TYPE_CHECKING, Callable

from gi.repository import GLib, Gtk
from .launcher import Launcher
from . import rename_workspace, switch_workspace, move_to_workspace

if TYPE_CHECKING:
    from .swaymore import Swaymore


class RemoteControl:
    pipe_path: str = os.path.expanduser("~/.local/share/swaymore/command")

    def __init__(self, swm: Swaymore):
        self.swaymore = swm
        self.thread = threading.Thread(target=self._pipe_reader)
        self.thread.daemon = True
        self.launcher: Launcher | None = None

        self.dispatch_table: list[tuple[str, Callable]] = [
            ("rename-workspace", self.workspace_rename),
            ("switch-workspace", self.workspace_switch),
            ("move-to-workspace", self.workspace_move_to),

            ("volume-toggle", self.volume_toggle),
            ("volume-up", self.volume_up),
            ("volume-down", self.volume_down),

            ("brightness-up", self.brightness_up),
            ("brightness-down", self.brightness_down),

            ("launcher", self.show_launcher),

            ("exit", self.close_taskbar),
        ]


    def start(self):
        # Clear any possible leftover commands by recreating the named pipe
        try:
            os.mkfifo(self.pipe_path)
        except FileExistsError:
            os.unlink(self.pipe_path)
            os.mkfifo(self.pipe_path)

        # Start the thread reading the pipe
        self.thread.start()

    def _pipe_reader(self):
        while True:
            with open(self.pipe_path) as pipe_file:
                line = pipe_file.readline()
                for command, callback in self.dispatch_table:
                    if command in line:
                        GLib.idle_add(callback)
                        break
                else:
                    print(f"remote.py> Unknown command: [{line}]")

    def workspace_rename(self):
        window = rename_workspace.WorkspaceRename()
        window.show_all()

    @staticmethod
    def workspace_switch():
        window = switch_workspace.WorkspaceSwitch()
        window.show_all()

    @staticmethod
    def workspace_move_to():
        window = move_to_workspace.WorkspaceMoveTo()
        window.show_all()

    def volume_toggle(self):
        self.swaymore.taskbar.volume.volume_toggle()

    def volume_up(self):
        self.swaymore.taskbar.volume.volume_up()

    def volume_down(self):
        self.swaymore.taskbar.volume.volume_down()

    def brightness_up(self):
        self.swaymore.taskbar.brightness.set_brightness_up()

    def brightness_down(self):
        self.swaymore.taskbar.brightness.set_brightness_down()

    def show_launcher(self):
        if self.launcher:
            self.launcher.show()
        else:
            self.launcher = Launcher()
            self.launcher.show()

    @staticmethod
    def close_taskbar():
        Gtk.main_quit()
