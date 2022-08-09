import os.path
import threading
from threading import current_thread

import gi

gi.require_version("Gdk", "3.0")
gi.require_version("Gtk", "3.0")
gi.require_version("GtkLayerShell", "0.1")
from gi.repository import GLib, Gtk, GtkLayerShell

from clock import Clock
from workspaces import Workspaces
from src import rename_workspace
from src import switch_workspace

def print_current_thread():
    print(f"Current thread native_id: {current_thread().native_id}")


class CommandListener:
    named_pipe: str = os.path.expanduser("~/.local/share/nylon/command")

    def __init__(self):
        self.thread = threading.Thread(target=self.listener)
        self.thread.daemon = True
        self.thread.start()

    def listener(self):
        while True:
            with open(self.named_pipe) as named_pipe_file:
                line = named_pipe_file.readline()
                # If the line is empty, nothing to read, reopen the pipe and block waiting
                if not line:
                    continue

                # Dispatch command
                # todo: don't need this, just loop
                if "rename-workspace" in line:
                    print("rename workspace")
                    GLib.idle_add(self.workspace_rename)
                elif "switch-workspace" in line:
                    print("switch-workspace")
                    GLib.idle_add(self.workspace_switch)
                else:
                    print(f"Unknown command: {line}")

    @staticmethod
    def workspace_rename():
        window = rename_workspace.WorkspaceRename()
        window.show_all()

    @staticmethod
    def workspace_switch():
        window = switch_workspace.WorkspaceSwitch()
        window.show_all()


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

        # Workspace switcher
        self.workspace_switcher = Workspaces()
        self.box.pack_start(self.workspace_switcher, False, True, 0)

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

    # Command listener
    command_listener = CommandListener()

    Gtk.main()


if __name__ == '__main__':
    main()
