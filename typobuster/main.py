"""
A simple text editor that helps you correct common typos.
Project: https://github.com/nwg-piotr/typobuster
Author's email: nwg.piotr@gmail.com
Copyright (c) 2025 Piotr Miller
License: GPL3
"""

import argparse
import os.path
import subprocess

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("GtkSource", "4")
from gi.repository import Gtk, Gdk, GLib, GtkSource, Pango

from typobuster.ui_components import MenuBar, SanitizationDialog, AboutWindow, SearchBar, PreferencesDialog
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


def on_destroy_event(widget):
    print("Terminating gracefully")
    Gtk.main_quit()


class Typobuster(Gtk.Window):
    def __init__(self):
        super().__init__()
        self.set_default_size(800, 600)
        self.settings = load_settings()
        self.syntax_dict = load_syntax()

        self.voc = voc
        self.set_title(f"{voc['untitled']} - Typobuster")

        self.last_dir_path = ""
        self.search_bar = None

        self.gtk_settings = Gtk.Settings.get_default()

        self.unsaved_changes = False
        self.connect("delete-event", self.on_close)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.add(vbox)

        # Create a GtkSourceView and configure it
        self.source_view = GtkSource.View()
        self.source_settings = self.source_view.get_settings()

        self.source_view.get_style_context().add_class("sourceview")
        if self.settings["view-line-numbers"]:
            self.source_view.set_show_line_numbers(True)  # Enable line numbers

        self.source_view.set_highlight_current_line(
            self.settings["highlight-current-row"])  # Highlight the current line

        if self.settings["wrap-lines"]:
            self.source_view.set_wrap_mode(Gtk.WrapMode.WORD)
        else:
            self.source_view.set_wrap_mode(Gtk.WrapMode.NONE)

        # Enable drag-and-drop for URI (file paths)
        self.source_view.drag_dest_set(Gtk.DestDefaults.ALL, [], Gdk.DragAction.COPY)
        self.source_view.drag_dest_add_uri_targets()
        self.source_view.connect("drag-data-received", self.on_drag_data_received)

        # Set a language for syntax highlighting
        self.lang_manager = GtkSource.LanguageManager()
        self.buffer = GtkSource.Buffer()

        self.buffer.set_highlight_matching_brackets(
            self.settings["highlight-matching-brackets"])  # Highlight matching brackets

        self.source_view.set_buffer(self.buffer)
        self.buffer.connect("changed", self.on_text_changed)

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

        self.search_bar = SearchBar(self)
        vbox.pack_end(self.search_bar, False, False, 0)

        if "syntax" in self.settings:
            self.set_syntax(None, self.settings["syntax"])

        # Add sample text to the buffer
        self.buffer.begin_not_undoable_action()
        self.buffer.set_text("")
        self.buffer.end_not_undoable_action()

        self.set_view_style()
        self.set_gtk_theme()

        # Connect the delete event to quit the application
        self.connect("destroy", on_destroy_event)

    def on_text_changed(self, buffer):
        self.unsaved_changes = True

    def on_close(self, widget, event):
        if self.unsaved_changes:
            dialog = Gtk.MessageDialog(
                transient_for=self,
                flags=0,
                message_type=Gtk.MessageType.WARNING,

                text=self.voc["unsaved-changes"]
            )
            dialog.add_buttons(self.voc["save"], Gtk.ResponseType.YES, self.voc["dont-save"], Gtk.ResponseType.NO,
                               self.voc["cancel"], Gtk.ResponseType.CANCEL)
            dialog.format_secondary_text(self.voc["unsaved-changes-question"])
            response = dialog.run()
            dialog.destroy()

            if response == Gtk.ResponseType.YES:
                self.save_on_exit()
                return False  # Allow closing
            elif response == Gtk.ResponseType.NO:
                self.unsaved_changes = False
                return False  # Allow closing
            else:
                return True  # Prevent closing
        return False  # Allow closing

    def save_on_exit(self):
        if self.get_title() == f"{voc['untitled']} - Typobuster":
            self.save_file_as(None)
        else:
            self.save_file(None)
        self.unsaved_changes = False

    def set_syntax(self, widget, name):
        language = self.lang_manager.get_language(name)
        self.buffer.set_language(language)
        self.settings["syntax"] = name
        save_settings(self.settings)
        if self.settings["syntax"] == "none":
            s_lbl = self.voc["plain-text"]
        else:
            s_lbl = self.syntax_dict[self.settings["syntax"]]
        self.search_bar.syntax_lbl.set_text(s_lbl)

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
        self.settings["view-line-numbers"] = widget.get_active()
        self.source_view.set_show_line_numbers(self.settings["view-line-numbers"])
        save_settings(self.settings)

    def toggle_highlight_current_row(self, widget):
        self.settings["highlight-current-row"] = widget.get_active()
        self.source_view.set_highlight_current_line(self.settings["highlight-current-row"])
        save_settings(self.settings)

    def toggle_highlight_matching_brackets(self, widget):
        self.settings["highlight-matching-brackets"] = widget.get_active()
        self.source_view.get_buffer().set_highlight_matching_brackets(self.settings["highlight-matching-brackets"])
        save_settings(self.settings)

    def toggle_whitespaces(self, widget):
        self.settings["whitespaces"] = widget.get_active()
        if self.settings["whitespaces"]:
            self.source_settings.set_property("draw-spaces-types", "all")
        else:
            self.source_settings.set_property("draw-spaces-types", "none")
        save_settings(self.settings)

    def toggle_line_wrap(self, widget):
        self.settings["wrap-lines"] = widget.get_active()
        if self.settings["wrap-lines"]:
            self.source_view.set_wrap_mode(Gtk.WrapMode.WORD)
        else:
            self.source_view.set_wrap_mode(Gtk.WrapMode.NONE)
        save_settings(self.settings)

    def show_about(self, widget):
        about = AboutWindow(self)
        about.run()

    def show_preferences(self, widget):
        PreferencesDialog(self)

    def on_font_selected(self, font_btn):
        self.settings["gtk-font-name"] = font_btn.get_font()
        self.set_view_style()
        save_settings(self.settings)

    def on_tab_with_selected(self, sb):
        self.settings["tab-width"] = int(sb.get_value())
        self.set_tab_width()
        save_settings(self.settings)

    def set_view_style(self):
        if self.settings["gtk-font-name"]:
            # Create a CssProvider and parse "gtk-font-name" into CSS
            css_provider = Gtk.CssProvider()
            font = self.settings["gtk-font-name"].replace(",", "")
            parts = font.split()
            family = " ".join(parts[0:-1])
            size = parts[-1]
            css = f'.sourceview {{ font-family: "{family}"; font-size: {size}pt; }}'.encode()
            css_provider.load_from_data(css)

            # Get the style context of self.source_view and add the CSS provider
            style_context = self.source_view.get_style_context()
            style_context.add_provider(css_provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)

    def set_tab_width(self):
        self.source_view.set_tab_width(self.settings["tab-width"])

    def on_theme_changed(self, combo):
        self.settings["gtk-theme-name"] = combo.get_active_id()
        save_settings(self.settings)
        self.set_gtk_theme()

    def set_gtk_theme(self):
        if self.settings["gtk-theme-name"]:
            self.gtk_settings.set_property("gtk-theme-name", self.settings["gtk-theme-name"])
        else:
            # TODO we need to get from gsettings and apply here
            theme = subprocess.check_output("gsettings get org.gnome.desktop.interface gtk-theme", shell=True).decode(
                "utf-8")
            self.gtk_settings.set_property("gtk-theme-name", theme[1:-2])

    def on_drag_data_received(self, widget, drag_context, x, y, data, info, time):
        """Handle file drop event."""
        uris = data.get_uris()
        if uris:
            f_p = uris[0].replace("file://", "").strip()
            self.load_file(None, f_p)
            global file_path
            file_path = f_p

    def transform_text(self, widget, transformation):
        start = self.buffer.get_start_iter()
        end = self.buffer.get_end_iter()
        if self.buffer.get_has_selection():
            start, end = self.buffer.get_selection_bounds()
        if start and end:
            text = self.buffer.get_text(start, end, True)

            if transformation == "sentence":
                transformed_text = as_in_sentence(text)
            elif transformation == "lowercase":
                transformed_text = to_lower_case(text)
            elif transformation == "uppercase":
                transformed_text = to_upper(text)
            elif transformation == "camelcase":
                transformed_text = to_camel_case(text)
            elif transformation == "snakecase":
                transformed_text = to_snake_case(text)
            elif transformation == "kebabcase":
                transformed_text = to_kebab_case(text)
            elif transformation == "unordered":
                transformed_text = unordered_list(text)
            elif transformation == "ordered":
                transformed_text = ordered_list(text)
            elif transformation == "sort-asc":
                transformed_text = sort_lines(text)
            elif transformation == "sort-desc":
                transformed_text = sort_lines(text, order="desc")
            elif transformation == "remove-empty-rows":
                transformed_text = remove_empty_lines(text)
            elif transformation == "remove-non-ascii":
                transformed_text = remove_non_ascii(text)
            elif transformation == "first-to-end":
                transformed_text = move_first_word_to_end(text)
            elif transformation == "last-to-beginning":
                transformed_text = move_last_word_to_beginning(text)
            else:
                transformed_text = text

            self.buffer.begin_user_action()
            self.buffer.delete(start, end)
            self.buffer.insert(start, transformed_text)
            self.buffer.end_user_action()

    def select_range(self, start, end):
        start_iter = self.buffer.get_iter_at_offset(start)
        end_iter = self.buffer.get_iter_at_offset(end)
        self.buffer.select_range(start_iter, end_iter)

    def sanitize_text(self, widget):
        # Apply some basic predefined sanitization
        d = SanitizationDialog(self, self.buffer)

    def replace(self, old, new):
        start = self.buffer.get_start_iter()
        end = self.buffer.get_end_iter()

        text = self.buffer.get_text(start, end, True)
        text = replace_all(text, old, new)
        self.update_text(text)

    def set_window_title(self, path):
        filename = os.path.basename(path)
        self.set_title(f"{filename} - Typobuster")

    def new_file(self, widget):
        title = file_path.split("/")[-1] if file_path else self.voc["untitled"]
        if self.unsaved_changes:
            if self.buffer.get_text(self.buffer.get_start_iter(), self.buffer.get_end_iter(), True):
                dialog = Gtk.MessageDialog(
                    transient_for=self,
                    flags=0,
                    message_type=Gtk.MessageType.QUESTION,
                    buttons=Gtk.ButtonsType.YES_NO,
                    text=f"{self.voc['want-save-changes']} {title}?",
                )
                dialog.format_secondary_text(self.voc["chages-will-be-lost"])
                response = dialog.run()
                dialog.destroy()
                if response == Gtk.ResponseType.YES:
                    self.save_file(self.buffer.get_text(self.buffer.get_start_iter(), self.buffer.get_end_iter(), True))

        self.update_text("")
        self.unsaved_changes = False
        self.set_window_title(f"{voc['untitled']} - Typobuster")

    def load_file(self, widget, path):
        if self.unsaved_changes:
            self.on_close(None, None)

        global file_path
        file_path = os.path.abspath(path)
        if os.path.isfile(file_path):
            print(f"Opening {file_path}")
        else:
            eprint(f"'{file_path}' does not exist")

            dialog = Gtk.MessageDialog(
                parent=self,
                transient_for=self,
                flags=0,
                message_type=Gtk.MessageType.ERROR,
                buttons=Gtk.ButtonsType.OK,
                text=voc["file-not-found"],
            )
            dialog.run()
            dialog.destroy()

            self.update_recent(file_path, remove=True)
            return

        text = ""
        if os.path.isfile(path):
            self.last_dir_path = os.path.dirname(path)  # remember last opened dir for file chooser
            text = load_text_file(path)
            self.update_recent(path)
            self.menu_bar.recent_menu_item.set_sensitive(True)
        self.update_text(text)
        self.set_window_title(path)

        self.search_bar.clear()
        self.source_view.grab_focus()

        self.unsaved_changes = False

    def open_file(self, widget):
        if self.unsaved_changes:
            self.on_close(None, None)

        dialog = Gtk.FileChooserDialog(
            title="Open File",
            parent=self,
            action=Gtk.FileChooserAction.OPEN,
        )
        dialog.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK)
        if self.last_dir_path:
            dialog.set_current_folder(self.last_dir_path)
        else:
            dialog.set_current_folder(os.getenv("HOME"))

        filter_text = Gtk.FileFilter()
        filter_text.set_name("Text files")
        filter_text.add_mime_type("text/plain")
        dialog.add_filter(filter_text)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            filename = dialog.get_filename()
            self.load_file(None, filename)
        dialog.destroy()

    def save_file(self, widget):
        if file_path:
            text = self.buffer.get_text(self.buffer.get_start_iter(), self.buffer.get_end_iter(), True)
            result = save_text_file(text, file_path)
            if result == "ok":
                print(f"Saved text to {file_path}")
                self.unsaved_changes = False
                self.update_recent(file_path)
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
                self.unsaved_changes = False
                self.update_recent(file_path)
            else:
                eprint(f"Error saving text to {filename}: {result}")
        dialog.destroy()

    def update_text(self, text):
        start, end = self.buffer.get_bounds()
        self.buffer.begin_user_action()  # Mark as a single undoable action
        self.buffer.delete(start, end)
        self.buffer.insert_at_cursor(text)
        self.buffer.end_user_action()  # End the undoable action

    def update_recent(self, path, remove=False):
        recent_file = os.path.join(config_dir(), "recent")
        recent_paths = load_text_file(recent_file).splitlines() if os.path.isfile(recent_file) else []
        if path in recent_paths:
            recent_paths.remove(path)
        if len(recent_paths) >= 10:
            last = recent_paths.pop()
            print(f"Removing from recent: '{last}'")
        if not remove:
            recent_paths.insert(0, path)
        save_text_file("\n".join(recent_paths), recent_file)

    def quit(self, widget):
        self.close()


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

    screen = Gdk.Screen.get_default()
    provider = Gtk.CssProvider()
    style_context = Gtk.StyleContext()
    style_context.add_provider_for_screen(screen, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
    css = b"""
        #searchentry {
            color: white;
        }
        #searchentry-error {
            color: red;
        }
        """
    provider.load_from_data(css)

    if args.file_path:
        window.load_file(None, args.file_path)

    window.show_all()
    Gtk.main()


# Run the application
if __name__ == "__main__":
    sys.exit(main())
