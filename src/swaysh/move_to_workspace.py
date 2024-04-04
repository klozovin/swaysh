import gi
from i3ipc import Connection

gi.require_version("Gdk", "3.0")
gi.require_version("Gtk", "3.0")
gi.require_version("GtkLayerShell", "0.1")
from gi.repository import GLib, Gdk, Gtk, GtkLayerShell


class WorkspaceMoveTo(Gtk.Window):
    styling = b"""
    box {
        margin: 4px;
    }
    window {
        border: 3px solid #458588;
    }
    """

    def __init__(self):
        super().__init__(title="SwaySh: move-to-workspace")
        self.connect("key-press-event", self.key_pressed)

        # Setup sway connection
        self.sway = Connection()

        # Load CSS
        screen = Gdk.Screen.get_default()
        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(self.styling)
        style_context = Gtk.StyleContext()
        style_context.add_provider_for_screen(screen, css_provider,
                                              Gtk.STYLE_PROVIDER_PRIORITY_USER)

        # Use "wlr_layer_shell" protocol to float the window above everything else
        GtkLayerShell.init_for_window(self)
        GtkLayerShell.set_keyboard_mode(self, GtkLayerShell.KeyboardMode.ON_DEMAND)
        GtkLayerShell.set_layer(self, GtkLayerShell.Layer.TOP)

        # SearchEntry
        self.search = Gtk.SearchEntry()
        self.search.connect("activate", self.search_entry_activate)
        self.search.connect("search-changed", self.search_entry_changed)
        self.search.connect("key-press-event", self.search_entry_key_pressed)

        # List of workspaces where it's possible to move the window to. Exclude the currently
        # focused one.
        other_workspaces = [w for w in self.sway.get_workspaces() if not w.focused]

        self.list_box = Gtk.ListBox()
        # Make so that the user can't deselect the workspace
        self.list_box.set_selection_mode(Gtk.SelectionMode.BROWSE)
        self.list_box.set_filter_func(self.list_box_filter, None, False)
        self.list_box.connect("row-activated", self.list_box_row_activated)
        self.list_box.set_placeholder(Gtk.Label(label="No workspaces match"))
        for w in other_workspaces:
            label = Gtk.Label(label=f"{w.name}")
            self.list_box.insert(label, -1)
        # Can't use [self.list_box_select_first_visible_row] because nothing is visible yet!
        self.list_box_select_first_row()

        # Box
        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, homogeneous=False)
        self.box.pack_start(self.search, False, True, 0)
        self.box.pack_start(self.list_box, True, True, 0)
        self.add(self.box)

    #
    # SearchEntry
    #

    def search_entry_changed(self, _entry):
        # Re-filter the list of workspaces
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
        selected_workspace = self.list_box_get_selected_workspace()
        if selected_workspace is not None:
            self.move_window_to_workspace(selected_workspace)

    #
    # ListBox
    #

    def list_box_visible_rows(self) -> list[Gtk.ListBoxRow] | None:
        visible_rows = [child for child in self.list_box.get_children() if child.get_mapped()]
        if visible_rows:
            return visible_rows
        else:
            return None

    def list_box_select_first_visible_row(self):
        visible_rows = self.list_box_visible_rows()
        if visible_rows is not None:
            self.list_box.select_row(visible_rows[0])

    def list_box_select_first_row(self):
        self.list_box.select_row(self.list_box.get_children()[0])

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

    def list_box_get_selected_workspace(self) -> str | None:
        selected_row = self.list_box.get_selected_row()
        if selected_row is not None:
            return selected_row.get_child().get_text()
        else:
            return None

    def move_window_to_workspace(self, workspace: str):
        GLib.idle_add(self.move_container_to_workspace, workspace)
        self.close()

    def key_pressed(self, _widget, event):
        if event.keyval == Gdk.KEY_Escape:
            self.close()

    def list_box_row_activated(self, box: Gtk.ListBox, activated_row: Gtk.ListBoxRow):
        workspace_name = activated_row.get_child().get_text()
        self.move_window_to_workspace(workspace_name)

    def list_box_filter(self, row, data, notify_destroy) -> bool:
        current_search = self.search.get_text()
        if current_search in row.get_child().get_text().lower():
            return True
        else:
            return False

    @staticmethod
    def move_container_to_workspace(workspace: str):
        sway = Connection()
        sway.command(f"move container to workspace {workspace}")


if __name__ == "__main__":
    window = WorkspaceMoveTo()
    window.connect("destroy", Gtk.main_quit)
    window.show_all()
    Gtk.main()
