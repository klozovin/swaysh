import gi
from i3ipc import Connection

gi.require_version("Gdk", "3.0")
gi.require_version("Gtk", "3.0")
gi.require_version("GtkLayerShell", "0.1")
from gi.repository import Gdk, Gtk, GtkLayerShell


class WorkspaceRename(Gtk.Window):
    styling = b"""
    box {
        margin: 4px;
    }
    window {
        border: 3px solid #458588;
    }
    """

    def __init__(self):
        super().__init__(title="Nylon: rename-workspace")
        self.connect("key-press-event", self.key_pressed)

        # Setup sway connection
        self.sway = Connection()
        self.sway_workspaces = self.sway.get_workspaces()

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

        # Rename Entry: create, fill with current workspace name
        self.rename_entry = Gtk.Entry()
        self.rename_entry.set_text(self.get_focused_workspace())
        self.rename_entry.connect("activate", self.rename_entry_activate)

        # Box
        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, homogeneous=False)
        self.box.pack_start(self.rename_entry, False, True, 0)
        self.add(self.box)

    def get_focused_workspace(self) -> str:
        """
        Return the name of the currently focused sway workspace.
        """
        return next(w for w in self.sway_workspaces if w.focused).name

    def rename_workspace(self, workspace_name: str):
        self.sway.command(f"rename workspace to {workspace_name}")
        self.close()

    def key_pressed(self, _widget, event):
        if event.keyval == Gdk.KEY_Escape:
            self.close()

    def rename_entry_activate(self, entry: Gtk.SearchEntry):
        # rename the current workspace
        new_workspace_name = self.rename_entry.get_text().strip()
        if new_workspace_name:
            self.rename_workspace(new_workspace_name)


if __name__ == "__main__":
    window = WorkspaceRename()
    window.connect("destroy", Gtk.main_quit)
    window.show_all()
    Gtk.main()