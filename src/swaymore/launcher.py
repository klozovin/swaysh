from __future__ import annotations

import gc
import os
import subprocess
from pathlib import Path

from gi.repository import Gdk, Gtk, GtkLayerShell


class Launcher:
    def __init__(self):
        print("Launcher.__init__()")
        self.window: Gtk.Window | None = None
        self.executables_in_path: [Path] = self._executables_in_path()

    def show(self):
        """
        Must run in GTK UI thread.
        """
        assert self.window is None
        self.window = LauncherWindow(self)
        self.window.show_all()

    def launch(self, executable: Path):
        """
        Launch an executable, close the Launcher window.
        """
        subprocess.Popen(executable,
                         start_new_session=True,
                         cwd=os.path.expanduser("~"))
        self.close()

    def close(self):
        self.window.close()
        del self.window
        self.window = None
        print(f"Garbage: {gc.garbage}")
        gc.collect()

    @staticmethod
    def _executables_in_path() -> [Path]:
        """
        Find all executables in users $PATH, try to deduplicate.
        """
        path_entries = [Path(d) for d in os.environ["PATH"].split(":")]

        # Resolve symlinks, deduplicate
        directories_in_path: set[Path] = set()
        for path_entry in path_entries:
            if path_entry.is_symlink():
                directories_in_path.add(path_entry.readlink())
            else:
                directories_in_path.add(path_entry)

        # There should be no more symlinked directories left!
        assert all([not d.is_symlink() for d in directories_in_path])

        # Collect all the executables
        executables: [Path] = list()
        for d in directories_in_path:
            # Skip non existent directories, or "." dir
            if not d.exists() or d == Path("."):
                continue
            for f in d.iterdir():
                if os.access(f, os.X_OK):
                    executables.append(f)

        return executables


class LauncherWindow(Gtk.Window):
    def __del__(self):
        print("and i'm gone!!!")

    def destroy(self, *args, **kwargs):
        print(f"LauncherWindow.destroy: {args}")
        # Without this there's a memory leak (possibly only older GTK
        # self.list_box.set_filter_func(None)

    def __init__(self, launcher: Launcher):
        super().__init__()
        self.launcher = launcher
        self.connect("key-press-event", self.key_pressed)
        self.connect("destroy", self.destroy)

        self.set_size_request(512, 1024)

        GtkLayerShell.init_for_window(self)
        GtkLayerShell.set_keyboard_mode(self, GtkLayerShell.KeyboardMode.ON_DEMAND)
        GtkLayerShell.set_layer(self, GtkLayerShell.Layer.TOP)

        # ListBox: list of executables to run
        self.list_box = Gtk.ListBox()
        self.list_box.set_filter_func(self.list_box_filter)

        for executable in self.launcher.executables_in_path:
            label = Gtk.Label(label=f"{executable}")
            self.list_box.insert(label, -1)

        # ScrolledWindow: make the ListBox scrollable
        self.scrolled = Gtk.ScrolledWindow()
        self.scrolled.add(self.list_box)

        # Box
        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.box.pack_start(self.scrolled, True, True, 2)
        self.add(self.box)

    def key_pressed(self, _widget, event):
        if event.keyval == Gdk.KEY_Escape:
            self.launcher.close()
        if event.keyval == Gdk.KEY_Break:
            Gtk.main_quit()

    @staticmethod
    def list_box_filter(_row) -> bool:
        return True
        # current_search = self.search_entry.get_text()
        # if current_search in row.get_child().get_text().lower():
        #     return True
        # else:
        #     return False
