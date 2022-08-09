import os
import threading

from gi.repository import GLib, Gtk

from src import rename_workspace, switch_workspace


class CommandListener:
    pipe_path: str = os.path.expanduser("~/.local/share/nylon/command")

    def __init__(self):
        self.thread = threading.Thread(target=self._listener)
        self.thread.daemon = True

    def start(self):
        # Clear any possible leftover commands by recreating the named pipe
        try:
            os.mkfifo(self.pipe_path)
        except FileExistsError:
            os.unlink(self.pipe_path)
            os.mkfifo(self.pipe_path)

        # Start the thread reading the pipe
        self.thread.start()

    def _listener(self):
        while True:
            # Reopen the file on every line (inefficient, but fine)
            with open(self.pipe_path) as pipe_file:
                line = pipe_file.readline()
                if "rename-workspace" in line:
                    GLib.idle_add(self.workspace_rename)
                elif "switch-workspace" in line:
                    GLib.idle_add(self.workspace_switch)
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
    def close_taskbar():
        Gtk.main_quit()
