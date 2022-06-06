from datetime import datetime
from threading import Thread, current_thread
from time import sleep

import gi
import i3ipc

gi.require_version("Gdk", "3.0")
gi.require_version("Gtk", "3.0")
gi.require_version("GtkLayerShell", "0.1")
from gi.repository import GLib, Gdk, Gtk, GtkLayerShell


def print_current_thread():
    print(f"Current thread native_id: {current_thread().native_id}")


class WorkspaceSwitcher(Gtk.Box):
    styling = b"""
    .active-workspace {
        font-weight: bold;
    }
    """

    def __init__(self):
        super().__init__()
        self.current_workspace: str | None = None

        # Load CSS
        screen = Gdk.Screen.get_default()
        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(self.styling)
        style_context = Gtk.StyleContext()
        style_context.add_provider_for_screen(screen, css_provider,
                                              Gtk.STYLE_PROVIDER_PRIORITY_USER)

        # Connect to sway, get workspaces and create button
        self.sway_connection = i3ipc.Connection()
        workspaces = self.sway_connection.get_workspaces()
        for w in workspaces:
            button = Gtk.Button(label=f"{w.name}")
            if w.focused:
                button.get_style_context().add_class("active-workspace")
            self.pack_start(button, expand=False, fill=True, padding=8)

        # Start the thread listening on sway events
        self.thread = Thread(target=self.sway_ipc_thread)
        self.thread.daemon = True
        self.thread.start()

    def sway_ipc_thread(self):
        # Subscribe to sway workspace events
        print(self.sway_connection)
        self.sway_connection.on(i3ipc.Event.WORKSPACE_FOCUS, self.dummy)

        # Start i3ipc main loop (should be run in separate thread)
        self.sway_connection.main()

    def update_focused_workspace(self):
        if self.current_workspace is None:
            return

        workspace_buttons = self.get_children()
        for workspace in workspace_buttons:
            workspace.get_style_context().remove_class("active-workspace")
        focused_workspace_button = next(filter(lambda x: x.get_label() == self.current_workspace,
                                               self.get_children()))
        focused_workspace_button.get_style_context().add_class("active-workspace")

    def dummy(self, _sway: i3ipc.Connection, event: i3ipc.events.IpcBaseEvent):
        self.current_workspace = event.current.name
        print(f"Current workspace: {self.current_workspace}")
        GLib.idle_add(self.update_focused_workspace)


class Clock(Gtk.Label):
    def __init__(self):
        super().__init__(label="n/a")
        self.thread = Thread(target=self.loop)
        self.thread.daemon = True
        self.thread.start()

    def update_time(self):
        now = datetime.now()
        self.set_text(now.strftime("%H:%M:%S"))

    def loop(self):
        while True:
            sleep(1)
            GLib.idle_add(self.update_time)


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
        self.workspace_switcher = WorkspaceSwitcher()
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
    print_current_thread()
    Gtk.main()


if __name__ == '__main__':
    main()
