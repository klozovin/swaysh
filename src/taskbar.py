import gi

gi.require_version("Gtk", "3.0")
gi.require_version("GtkLayerShell", "0.1")

from gi.repository import Gtk, GtkLayerShell


def on_button_click(button: Gtk.Button):
    print("Hello, world!")


def main():
    window = Gtk.Window()
    button = Gtk.Button(label="Click Me!")
    button.connect("clicked", on_button_click)
    window.add(button)

    GtkLayerShell.init_for_window(window)
    GtkLayerShell.auto_exclusive_zone_enable(window)
    GtkLayerShell.set_margin(window, GtkLayerShell.Edge.TOP, 10)
    GtkLayerShell.set_margin(window, GtkLayerShell.Edge.BOTTOM, 10)
    GtkLayerShell.set_anchor(window, GtkLayerShell.Edge.TOP, 1)

    window.show_all()
    window.connect("destroy", Gtk.main_quit)
    Gtk.main()


if __name__ == '__main__':
    main()
