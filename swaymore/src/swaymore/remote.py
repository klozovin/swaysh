from __future__ import annotations
import os
import threading
import typing

from gi.repository import GLib, Gtk
from .launcher import Launcher
from . import rename_workspace, switch_workspace, move_to_workspace

if typing.TYPE_CHECKING:
    from .swaymore import Swaymore


class RemoteControl:
    pipe_path: str = os.path.expanduser("~/.local/share/swaymore/command")

    def __init__(self, swm: Swaymore):
        self.swaymore = swm
        self.thread = threading.Thread(target=self._pipe_reader)
        self.thread.daemon = True
        self.launcher: Launcher | None = None

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
            # Reopen the file on every line (inefficient, but fine)
            # TODO: why use idle_add() here?
            with open(self.pipe_path) as pipe_file:
                line = pipe_file.readline()
                if "rename-workspace" in line:
                    GLib.idle_add(self.workspace_rename)
                elif "switch-workspace" in line:
                    GLib.idle_add(self.workspace_switch)
                elif "move-to-workspace" in line:
                    GLib.idle_add(self.workspace_move_to)
                elif "brightness-up" in line:
                    GLib.idle_add(self.brightness_up)
                elif "brightness-down" in line:
                    GLib.idle_add(self.brightness_down)
                elif "launcher" in line:
                    GLib.idle_add(self.show_launcher)
                elif "exit" in line:
                    GLib.idle_add(self.close_taskbar)
                else:
                    # TODO: Use logging for this
                    print(f"Unknown command: {line}")

    @staticmethod
    def workspace_rename():
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

    @staticmethod
    def brightness_up():
        print("let there be light")

    def brightness_down(self):
        self.swaymore.taskbar.brightness.set_brightness_down()
        print("let there be no light")

    def show_launcher(self):
        if self.launcher:
            self.launcher.show()
        else:
            self.launcher = Launcher()
            self.launcher.show()

    @staticmethod
    def close_taskbar():
        Gtk.main_quit()
