"""
A simple text editor that helps you correct common typos.
Project: https://github.com/nwg-piotr/typobuster
Author's email: nwg.piotr@gmail.com
Copyright (c) 2025 Piotr Miller
License: GPL3
"""

import argparse
import gi

gi.require_version("Gtk", "3.0")
gi.require_version("GtkSource", "4")
from gi.repository import Gtk, Gdk, GLib, GtkSource

from typobuster.ui_components import MenuBar, SanitizationDialog, AboutWindow
from typobuster.tools import *

dir_name = os.path.dirname(__file__)
file_path = ""
voc = {}


def load_vocabulary():
    global voc
    # basic vocabulary (for en_US)
    voc = load_json(os.path.join(dir_name, "langs", "en_US.json"))
    if not voc:
        eprint("Failed loading vocabulary, terminating")
        sys.exit(1)

    shell_data = load_shell_data()

    lang = os.getenv("LANG")
    if lang is None:
        lang = "en_US"
    else:
        lang = lang.split(".")[0] if not shell_data["interface-locale"] else shell_data["interface-locale"]

    # translate if translation available
    if lang != "en_US":
        loc_file = os.path.join(dir_name, "langs", "{}.json".format(lang))
        if os.path.isfile(loc_file):
            # localized vocabulary
            loc = load_json(loc_file)
            if not loc:
                eprint("Failed loading translation into '{}'".format(lang))
            else:
                for key in loc:
                    voc[key] = loc[key]


class Typobuster(Gtk.Window):
    def __init__(self):
        super().__init__(title="Untitled - Typobuster")
        self.set_default_size(800, 600)
        self.settings = load_settings()
        self.voc = voc

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.add(vbox)

        # Create a GtkSourceView and configure it
        self.source_view = GtkSource.View()
        if self.settings["view-line-numbers"]:
            self.source_view.set_show_line_numbers(True)  # Enable line numbers
        # self.source_view.set_highlight_current_line(True)  # Highlight the current line
        self.source_view.set_wrap_mode(Gtk.WrapMode.WORD)

        # Enable drag-and-drop for URI (file paths)
        self.source_view.drag_dest_set(Gtk.DestDefaults.ALL, [], Gdk.DragAction.COPY)
        self.source_view.drag_dest_add_uri_targets()
        self.source_view.connect("drag-data-received", self.on_drag_data_received)

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

    def on_drag_data_received(self, widget, drag_context, x, y, data, info, time):
        """Handle file drop event."""
        uris = data.get_uris()
        if uris:
            f_p = uris[0].replace("file://", "").strip()
            self.load_file_on_startup(f_p)
            global file_path
            file_path = f_p

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
        self.set_window_title(f"{voc['view']} - Typobuster")

    def load_file_on_startup(self, path):
        global file_path
        file_path = os.path.abspath(path)
        print(file_path)

        text = ""
        if os.path.isfile(path):
            text = load_text_file(path)
        self.update_text(text)
        self.set_window_title(path)

    def open_file(self, widget):
        dialog = Gtk.FileChooserDialog(
            title="Open File",
            parent=self,
            action=Gtk.FileChooserAction.OPEN,
        )
        dialog.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK)
        dialog.set_current_folder(os.getenv("HOME"))

        filter_text = Gtk.FileFilter()
        filter_text.set_name("Text files")
        filter_text.add_mime_type("text/plain")
        dialog.add_filter(filter_text)

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


def main():
    parser = argparse.ArgumentParser(description="Simple text editor")
    parser.add_argument("file_path", type=str, nargs="?", help="Path of the file to open")
    args = parser.parse_args()

    if args.file_path:
        global file_path
        file_path = args.file_path

    GLib.set_prgname('typobuster')
    load_vocabulary()
    window = Typobuster()

    if args.file_path:
        window.load_file_on_startup(args.file_path)

    window.show_all()
    Gtk.main()


# Run the application
if __name__ == "__main__":
    sys.exit(main())

