import gi

gi.require_version("Gtk", "3.0")
gi.require_version("GtkSource", "4")
from gi.repository import Gtk, GtkSource

from typobuster.ui_components import MenuBar, SanitizationDialog
from typobuster.tools import *


class Scratchpad(Gtk.Window):
    def __init__(self):
        super().__init__(title="Untitled - Typobuster")
        self.set_default_size(800, 600)
        self.settings = load_settings()

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.add(vbox)

        self.menu_bar = MenuBar(self)
        vbox.pack_start(self.menu_bar, False, False, 0)

        # Create a GtkSourceView and configure it
        self.source_view = GtkSource.View()
        if self.settings["view-line-numbers"]:
            self.source_view.set_show_line_numbers(True)  # Enable line numbers
        # self.source_view.set_highlight_current_line(True)  # Highlight the current line
        self.source_view.set_wrap_mode(Gtk.WrapMode.WORD)

        # Set a language for syntax highlighting
        lang_manager = GtkSource.LanguageManager()
        language = lang_manager.get_language("none")  # Set Python syntax
        self.buffer = GtkSource.Buffer()
        self.buffer.set_language(language)
        self.source_view.set_buffer(self.buffer)

        # Create a scrollable window and add the source view
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_hexpand(True)
        scrolled_window.set_vexpand(True)
        scrolled_window.add(self.source_view)

        # Add the scrollable window to the main window
        vbox.add(scrolled_window)

        # Add sample text to the buffer
        self.buffer.set_text("# This is a GtkSourceView example\nprint('Hello, World!')")

        # Connect the delete event to quit the application
        self.connect("destroy", Gtk.main_quit)

    def toggle_line_numbers(self, widget):
        self.settings["view-line-numbers"] = not self.settings["view-line-numbers"]
        self.source_view.set_show_line_numbers(self.settings["view-line-numbers"])
        save_settings(self.settings)
        self.menu_bar.line_numbers_menu_item.set_image("view-line-numbers")

    def sanitize_text(self, widget):
        d = SanitizationDialog(self, self.buffer)

    def update_text(self, text):
        self.buffer.set_text(text)

    def quit(self, widget):
        Gtk.main_quit()


# Run the application
if __name__ == "__main__":
    window = Scratchpad()
    window.show_all()
    Gtk.main()
