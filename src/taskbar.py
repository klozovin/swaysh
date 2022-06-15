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


class WorkspaceSwitcher(Gtk.EventBox):
    styling = b"""
    .active-workspace {
        font-weight: bold;
    }
    """

    def __init__(self):
        super().__init__()

        # Box for the workspace buttons
        self.box = Gtk.Box()
        self.add(self.box)

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
            button.connect("clicked", self.button_clicked)
            if w.focused:
                button.get_style_context().add_class("active-workspace")
            self.box.pack_start(button, expand=False, fill=True, padding=8)

        # Enable mouse scroll events for this widget
        self.add_events(Gdk.EventMask.SCROLL_MASK)
        self.connect("scroll-event", self.mouse_scrolled)

        # Start the thread listening on sway events
        self.thread = Thread(target=self.sway_ipc_thread)
        self.thread.daemon = True
        self.thread.start()

    def button_clicked(self, button):
        self.sway_connection.command(f"workspace {button.get_label()}")

    def mouse_scrolled(self, widget, event: Gdk.EventScroll):
        """
        Handle mouse scroll event.

        Switch to next/previous workspace, don't wrap around.
        """
        focused_workspace_idx, workspaces = self.get_workspaces_with_focused()
        workspace_to_focus: i3ipc.WorkspaceReply | None = None
        match event.get_scroll_direction()[1]:
            case Gdk.ScrollDirection.DOWN:
                if focused_workspace_idx != len(workspaces) - 1:
                    workspace_to_focus = workspaces[focused_workspace_idx + 1]
            case Gdk.ScrollDirection.UP:
                if focused_workspace_idx != 0:
                    workspace_to_focus = workspaces[focused_workspace_idx - 1]

        if workspace_to_focus is not None:
            self.sway_connection.command(f"workspace {workspace_to_focus.name}")

    def sway_ipc_thread(self):
        # Subscribe to sway workspace events
        self.sway_connection.on(i3ipc.Event.WORKSPACE_FOCUS, self.on_workspace_focus)

        # Start i3ipc main loop (should be run in separate thread)
        self.sway_connection.main()

    def update_focused_workspace(self, current_workspace: str):
        """
        Change the styling of the button corresponding to the currently focused workspace.
        """
        workspace_buttons = self.box.get_children()
        for workspace in workspace_buttons:
            workspace.get_style_context().remove_class("active-workspace")
        focused_workspace_button = next(filter(lambda x: x.get_label() == current_workspace,
                                               self.box.get_children()))
        focused_workspace_button.get_style_context().add_class("active-workspace")

    def get_workspaces_with_focused(self) -> (int, [i3ipc.WorkspaceReply]):
        workspaces = self.sway_connection.get_workspaces()
        focused_workspace_idx: int = next(filter(
            lambda x: x[1].focused == True,
            enumerate(workspaces)
        ))[0]
        return focused_workspace_idx, workspaces

    def on_workspace_focus(self, _sway: i3ipc.Connection, event: i3ipc.events.IpcBaseEvent):
        """
        Handler for sway event: change in focused workspace.
        """
        print(f"Current workspace: {event.current.name}")
        GLib.idle_add(lambda: self.update_focused_workspace(event.current.name))


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
    Gtk.main()


if __name__ == '__main__':
    main()
