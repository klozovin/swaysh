from threading import Thread

import i3ipc
from gi.repository import GLib, Gdk, Gtk


class Workspaces(Gtk.EventBox):
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

        # Create the workspace buttons
        self._create_buttons()

        # Enable mouse scroll events for this widget
        self.add_events(Gdk.EventMask.SCROLL_MASK)
        self.connect("scroll-event", self.mouse_scrolled)

        # Start the thread listening on sway events
        self.thread = Thread(target=self.sway_ipc_thread)
        self.thread.daemon = True
        self.thread.start()

    def _create_buttons(self):
        # Clear all existing buttons
        print("Clearing all buttons")
        for button in self.box.get_children():
            self.box.remove(button)

        # Create new buttons
        workspaces = self.sway_connection.get_workspaces()
        for w in workspaces:
            print(f"Creating button for workspace: {w.name}")
            button = Gtk.Button(label=f"{w.name}")
            button.connect("clicked", self.button_clicked)
            if w.focused:
                button.get_style_context().add_class("active-workspace")
            self.box.pack_start(button, expand=False, fill=True, padding=8)

        # Have to call this, otherwise the new buttons will not be visible.
        self.box.show_all()

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
            lambda x: x[1].focused,
            enumerate(workspaces)
        ))[0]
        return focused_workspace_idx, workspaces

    #
    # Sway event handlers
    #

    def sway_ipc_thread(self):
        event_handlers = [
            (i3ipc.Event.WORKSPACE_INIT, self.sway_workspace_init_handler),
            (i3ipc.Event.WORKSPACE_FOCUS, self.sway_workspace_focus_handler),
            (i3ipc.Event.WORKSPACE_RENAME, self.sway_workspace_rename_handler),
            (i3ipc.Event.WORKSPACE_EMPTY, self.sway_workspace_empty_handler)
        ]
        for event, handler in event_handlers:
            self.sway_connection.on(
                event,
                # OMG, WTF, for loop scoping?!?
                lambda con, evt, handler=handler: GLib.idle_add(handler, evt))
        self.sway_connection.main()

    # Should run in GTK main loop: sway_workspace_*_handler()

    def sway_workspace_init_handler(self, event: i3ipc.WorkspaceEvent):
        """
        New workspace created.
        """
        # TODO: just add the new workspace button instead of recreating everything?
        self._create_buttons()
        print(f"INIT: {event.change}/{event.current.name}")

    def sway_workspace_focus_handler(self, event: i3ipc.WorkspaceEvent):
        """
        Change in focused workspace.
        """
        print(f"FOCUS: {event.change}/{event.current.name}")
        self.update_focused_workspace(event.current.name)

    def sway_workspace_rename_handler(self, event: i3ipc.WorkspaceEvent):
        """
         Workspace renamed.
         """
        self._create_buttons()

    def sway_workspace_empty_handler(self, event: i3ipc.WorkspaceEvent):
        """
        Workspace deleted.
        """
        print(f"EMPTY: {event.change}/{event.current.name}")
        for button in self.box.get_children():
            if button.get_label() == event.current.name:
                self.box.remove(button)