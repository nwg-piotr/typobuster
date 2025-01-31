import gi

gi.require_version("Gtk", "3.0")
gi.require_version("GtkSource", "4")
from gi.repository import Gtk, Gdk, GLib, GtkSource

file_path = ""

from typobuster.ui_components import MenuBar, SanitizationDialog, AboutWindow
from typobuster.tools import *


class Scratchpad(Gtk.Window):
    def __init__(self):
        super().__init__(title="Untitled - Typobuster")
        self.set_default_size(800, 600)
        self.settings = load_settings()
        self.text_states = []

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.add(vbox)

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

        self.clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)

        self.menu_bar = MenuBar(self)
        vbox.pack_start(self.menu_bar, False, False, 0)

        # Create a scrollable window and add the source view
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_hexpand(True)
        scrolled_window.set_vexpand(True)
        scrolled_window.add(self.source_view)

        # Add the scrollable window to the main window
        vbox.add(scrolled_window)

        # Add sample text to the buffer
        self.buffer.begin_not_undoable_action()
        self.buffer.set_text("")
        self.buffer.end_not_undoable_action()

        # Connect the delete event to quit the application
        self.connect("destroy", Gtk.main_quit)

    def undo(self, widget):
        if self.buffer.can_undo():
            self.buffer.undo()

    def redo(self, widget):
        if self.buffer.can_redo():
            self.buffer.redo()

    def cut_text(self, widget):
        self.buffer.begin_user_action()
        self.buffer.cut_clipboard(self.clipboard, True)  # True -> delete after copying
        self.buffer.end_user_action()

    def copy_text(self, widget):
        self.buffer.copy_clipboard(self.clipboard)

    def paste_text(self, widget):
        self.buffer.begin_user_action()
        self.buffer.paste_clipboard(self.clipboard, None, True)
        self.buffer.end_user_action()

    def delete_text(self, widget):
        self.buffer.begin_user_action()
        self.buffer.delete_selection(True, True)
        self.buffer.end_user_action()

    def toggle_line_numbers(self, widget):
        self.settings["view-line-numbers"] = not self.settings["view-line-numbers"]
        self.source_view.set_show_line_numbers(self.settings["view-line-numbers"])
        save_settings(self.settings)
        self.menu_bar.line_numbers_menu_item.set_image("view-line-numbers")

    def show_about(self, widget):
        about = AboutWindow(self)
        about.run()


    def sanitize_text(self, widget):
        d = SanitizationDialog(self, self.buffer)

    def set_window_title(self, path):
        filename = os.path.basename(path)
        self.set_title(f"{filename} - Typobuster")

    def new_file(self, widget):
        if self.buffer.get_text(self.buffer.get_start_iter(), self.buffer.get_end_iter(), True):
            dialog = Gtk.MessageDialog(
                transient_for=self,
                flags=0,
                message_type=Gtk.MessageType.QUESTION,
                buttons=Gtk.ButtonsType.YES_NO,
                text="Do you want to save the changes to Untitled?",
            )
            dialog.format_secondary_text("Your changes will be lost if you don't save them.")
            response = dialog.run()
            dialog.destroy()
            if response == Gtk.ResponseType.YES:
                self.save_file(self.buffer.get_text(self.buffer.get_start_iter(), self.buffer.get_end_iter(), True))

        self.update_text("")
        global file_path
        file_path = ""
        self.set_window_title("Untitled - Typobuster")

    def open_file(self, widget):
        dialog = Gtk.FileChooserDialog(
            title="Open File",
            parent=self,
            action=Gtk.FileChooserAction.OPEN,
        )
        dialog.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK)
        dialog.set_current_folder(os.getenv("HOME"))

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            filename = dialog.get_filename()
            global file_path
            file_path = filename
            text = load_text_file(filename)
            if text:
                self.update_text(text)
                self.set_window_title(filename)
        dialog.destroy()

    def save_file(self, widget):
        if file_path:
            text = self.buffer.get_text(self.buffer.get_start_iter(), self.buffer.get_end_iter(), True)
            result = save_text_file(text, file_path)
            if result == "ok":
                print(f"Saved text to {file_path}")
            else:
                eprint(f"Error saving text to {file_path}: {result}")
        else:
            self.save_file_as(None)

    def save_file_as(self, widget):
        global file_path
        dialog = Gtk.FileChooserDialog(
            title="Save File",
            parent=self,
            action=Gtk.FileChooserAction.SAVE,
        )
        dialog.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_SAVE, Gtk.ResponseType.OK)
        if file_path:
            dialog.set_filename(file_path)
        else:
            dialog.set_current_folder(os.getenv("HOME"))

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            filename = dialog.get_filename()
            text = self.buffer.get_text(self.buffer.get_start_iter(), self.buffer.get_end_iter(), True)
            result = save_text_file(text, filename)
            if result == "ok":
                print(f"Saved text to {filename}")
                file_path = filename
                self.set_window_title(filename)
            else:
                eprint(f"Error saving text to {filename}: {result}")
        dialog.destroy()

    def update_text(self, text):
        start, end = self.buffer.get_bounds()
        self.buffer.begin_user_action()  # Mark as a single undoable action
        self.buffer.delete(start, end)
        self.buffer.insert_at_cursor(text)
        self.buffer.end_user_action()  # End the undoable action

    def quit(self, widget):
        Gtk.main_quit()


# Run the application
if __name__ == "__main__":
    # set app_id for Wayland
    GLib.set_prgname('typobuster')
    window = Scratchpad()
    window.show_all()
    Gtk.main()
