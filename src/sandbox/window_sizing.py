import gi

gi.require_version("Gdk", "3.0")
gi.require_version("Gtk", "3.0")
gi.require_version("GtkLayerShell", "0.1")

from gi.repository import Gtk, GtkLayerShell


def main():
    window = Gtk.Window()
    window.set_size_request(1024, 128)
    GtkLayerShell.init_for_window(window)

    # geometry = Gdk.Geometry()
    # geometry.max_height = 512
    # geometry.max_width = 512
    # window.set_geometry_hints(None, geometry, Gdk.WindowHints.MAX_SIZE)

    things = Gtk.ListBox()
    for i in range(100):
        things.insert(Gtk.Label(label=f"{i}."), -1)

    scrolled = Gtk.ScrolledWindow()
    scrolled.add(things)

    # box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
    # box.pack_start(things, False, True, 0)
    window.add(scrolled)

    window.show_all()
    Gtk.main()


if __name__ == '__main__':
    main()
