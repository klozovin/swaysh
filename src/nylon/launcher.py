import os
import subprocess
from pathlib import Path

from gi.repository import Gdk, Gtk, GtkLayerShell


class Launcher:
    def __init__(self):
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
        self.window = None

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
    styling = b"""
    box {
        margin: 4px;
    }
    window {
        border: 3px solid #458588;
    }
    """

    def __init__(self, launcher: Launcher):
        super().__init__()
        self.launcher = launcher
        self.connect("key-press-event", self.key_pressed)

        # Without this GTK sizes the window to small
        self.set_size_request(512, 1024)
        # self.set_default_size(512, 512)

        # Load CSS
        screen = Gdk.Screen.get_default()
        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(self.styling)
        style_context = Gtk.StyleContext()
        style_context.add_provider_for_screen(screen,
                                              css_provider,
                                              Gtk.STYLE_PROVIDER_PRIORITY_USER)

        # Use "wlr_layer_shell" protocol to float the window above everything else
        GtkLayerShell.init_for_window(self)
        GtkLayerShell.set_keyboard_mode(self, GtkLayerShell.KeyboardMode.ON_DEMAND)
        GtkLayerShell.set_layer(self, GtkLayerShell.Layer.TOP)

        # SearchEntry: filter executables
        self.search_entry = Gtk.SearchEntry()
        self.search_entry.connect("activate", self.search_entry_activate)
        self.search_entry.connect("search-changed", self.search_entry_changed)
        self.search_entry.connect("key-press-event", self.search_entry_key_pressed)

        #
        # ListBox: list of executables to run
        #
        self.list_box = Gtk.ListBox()
        self.list_box.set_selection_mode(Gtk.SelectionMode.BROWSE)
        self.list_box.set_filter_func(self.list_box_filter, None, False)
        self.list_box.connect("row-activated", self.list_box_row_activated)

        placeholder_label = Gtk.Label(label="No executables match")
        placeholder_label.set_visible(True)
        self.list_box.set_placeholder(placeholder_label)

        # Populate with list of executables
        for executable in self.launcher.executables_in_path:
            label = Gtk.Label(label=f"{executable.name} ({executable})")
            label.set_halign(Gtk.Align.START)
            label.path = executable
            self.list_box.insert(label, -1)
        # Can't use self.list_box_select_first_visible_row() because nothing is visible yet!
        self.list_box_select_first_row()

        # ScrolledWindow: make the ListBox scrollable
        self.scrolled = Gtk.ScrolledWindow()
        self.scrolled.add(self.list_box)

        # Box
        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.box.pack_start(self.search_entry, False, True, 0)
        self.box.pack_start(self.scrolled, True, True, 2)
        self.add(self.box)

    def key_pressed(self, widget, event):
        if event.keyval == Gdk.KEY_Escape:
            self.launcher.close()

    #
    # SearchEntry
    #
    def search_entry_changed(self, _entry):
        self.list_box.invalidate_filter()
        self.list_box_select_first_visible_row()

    def search_entry_key_pressed(self, _widget, event) -> bool:
        control_key = (event.state & Gdk.ModifierType.CONTROL_MASK)
        match event.keyval:
            case Gdk.KEY_Down:
                self.list_box_select_next_visible_row()
                return True
            case Gdk.KEY_Up:
                self.list_box_select_previous_visible_row()
                return True
            case Gdk.KEY_n if control_key:
                self.list_box_select_next_visible_row()
                return True
            case Gdk.KEY_p if control_key:
                self.list_box_select_previous_visible_row()
                return True
            case _:
                return False

    def search_entry_activate(self, entry: Gtk.SearchEntry):
        selected_executable = self.list_box_get_selected_executable()
        if selected_executable is not None:
            self.launcher.launch(selected_executable)
        else:
            return

    #
    # ListBox
    #
    def list_box_filter(self, row, data, notify_destroy) -> bool:
        current_search = self.search_entry.get_text()
        if current_search in row.get_child().get_text().lower():
            return True
        else:
            return False

    def list_box_row_activated(self, box: Gtk.ListBox, activated_row: Gtk.ListBoxRow):
        executable: Path = activated_row.get_child().path
        self.launcher.launch(executable)

    def list_box_visible_rows(self) -> list[Gtk.ListBoxRow] | None:
        visible_rows = [child for child in self.list_box.get_children() if child.get_mapped()]
        if visible_rows:
            return visible_rows
        else:
            return None

    def list_box_get_selected_executable(self) -> Path | None:
        selected_row = self.list_box.get_selected_row()
        if selected_row is not None:
            # return selected_row.get_child().get_text()
            return selected_row.get_child().path
        else:
            return None

    def list_box_select_first_row(self):
        self.list_box.select_row(self.list_box.get_children()[0])

    def list_box_select_first_visible_row(self):
        visible_rows = self.list_box_visible_rows()
        if visible_rows is not None:
            self.list_box.select_row(visible_rows[0])

    def list_box_select_next_visible_row(self):
        visible_rows = self.list_box_visible_rows()
        current_row = self.list_box.get_selected_row()
        assert (current_row is not None)
        assert (current_row in visible_rows)
        current_row_idx = visible_rows.index(current_row)

        # Select next if not on last row
        if current_row != visible_rows[-1]:
            self.list_box.select_row(visible_rows[current_row_idx + 1])
        # Select first row if currently on last
        else:
            self.list_box.select_row(visible_rows[0])

    def list_box_select_previous_visible_row(self):
        visible_rows = self.list_box_visible_rows()
        current_row = self.list_box.get_selected_row()
        current_row_idx = visible_rows.index(current_row)

        # Select previous if not on first row
        if current_row != visible_rows[0]:
            self.list_box.select_row(visible_rows[current_row_idx - 1])
        # Select last row if currently on first
        else:
            self.list_box.select_row(visible_rows[-1])
