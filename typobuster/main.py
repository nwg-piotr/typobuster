"""
Lightweight editor with text transformations and auto-correction.
Project: https://github.com/nwg-piotr/typobuster
Author's email: nwg.piotr@gmail.com
Copyright (c) 2025 Piotr Miller & Contributors
License: GPL3
"""

import argparse
import cairo
import os.path
import subprocess

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("GtkSource", "4")
from gi.repository import Gtk, Gdk, GLib, GtkSource

from typobuster.ui_components import MenuBar, ButtonBar, SanitizationDialog, AboutWindow, SearchBar, PreferencesDialog
from typobuster.tools import *

from typobuster.__about__ import __version__
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
        self.button_bar = None
        self.drag_in_progress = False
        self.settings = load_settings()
        self.syntax_dict = load_syntax()

        if self.settings["window-width"] and self.settings["window-height"]:
            self.set_default_size(self.settings["window-width"], self.settings["window-height"])
        else:
            self.set_default_size(800, 600)

        self.voc = voc
        self.set_title(f"{voc['untitled']} - Typobuster")

        self.last_dir_path = ""
        self.search_bar = None

        self.gtk_settings = Gtk.Settings.get_default()

        self.initial_text = ""
        self.file_stat = None

        self.gspell_available = False
        self.gspell_text_view = None

        self.connect("delete-event", self.on_close)
        self.connect("key-release-event", self.handle_keyboard_release)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.add(vbox)

        # Create a GtkSourceView and configure it
        self.source_view = GtkSource.View()

        self.source_view.get_style_context().add_class("sourceview")
        if self.settings["view-line-numbers"]:
            self.source_view.set_show_line_numbers(True)  # Enable line numbers

        self.source_view.set_right_margin_position(self.settings["right-margin-position"])
        self.source_view.set_show_right_margin(self.settings["right-margin-show"])

        space_drawer = self.source_view.get_space_drawer()
        space_drawer.set_enable_matrix(self.settings["whitespaces"])  # Whether to enable whitespaces view

        self.source_view.set_highlight_current_line(
            self.settings["highlight-current-row"])  # Highlight the current line

        if self.settings["wrap-lines"]:
            self.source_view.set_wrap_mode(Gtk.WrapMode.WORD)
        else:
            self.source_view.set_wrap_mode(Gtk.WrapMode.NONE)

        self.set_tab_width()

        self.set_tab_mode()

        self.set_auto_indent()

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
        self.buffer.connect("mark-set", self.on_cursor_moved)

        self.clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)

        self.menu_bar = MenuBar(self)
        vbox.pack_start(self.menu_bar, False, False, 0)

        self.button_bar_wrapper = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.button_bar_wrapper.set_property("name", "bar-wrapper")
        vbox.pack_start(self.button_bar_wrapper, False, False, 0)

        self.create_button_bar()

        # Create a scrollable window and add the source view
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_hexpand(True)
        scrolled_window.set_vexpand(True)
        scrolled_window.add(self.source_view)

        self.connect("enter-notify-event", self.check_file_change)

        # Add the scrollable window to the main window
        vbox.add(scrolled_window)

        self.search_bar = SearchBar(self)
        vbox.pack_end(self.search_bar, False, False, 0)

        if "syntax" in self.settings:
            language = self.lang_manager.get_language(self.settings["syntax"])
            self.buffer.set_language(language)
            if self.settings["syntax"] == "none":
                s_lbl = self.voc["plain-text"]
            else:
                s_lbl = self.syntax_dict[self.settings["syntax"]]
            self.search_bar.syntax_lbl.set_text(s_lbl)

        # Add initial (empty) text to the buffer
        self.buffer.begin_not_undoable_action()
        self.buffer.set_text("")
        self.reset_initial_text()
        self.update_stats()
        self.buffer.end_not_undoable_action()

        try:
            gi.require_version("Gspell", "1")
            from gi.repository import Gspell
            self.gspell_available = True
        except:
            self.gspell_available = False
            print(f"Gspell is NOT installed, spell check unavailable")

        if self.gspell_available:
            # Initialize gspell
            self.gspell_text_view = Gspell.TextView.get_from_gtk_text_view(self.source_view)

            language = None
            # set language from the value in settings
            if self.settings["gspell-lang"]:
                language = Gspell.Language.lookup(self.settings["gspell-lang"])
            # if language unset or erroneous, use the system default
            if not language:
                language = Gspell.Language.get_default()

            # the above might have not worked if hunspell missing
            if language:
                self.checker = Gspell.Checker.new(language)
                print(f"Spell check language: {language.get_code()}")
                self.checker.set_language(language)

                buffer = Gspell.TextBuffer.get_from_gtk_text_buffer(self.buffer)
                buffer.set_spell_checker(self.checker)
                self.gspell_text_view.set_enable_language_menu(True)
                self.gspell_available = True
                self.gspell_text_view.set_inline_spell_checking(
                    self.settings["gspell-enable"] and self.gspell_text_view)
                print("Loaded Gspell module")
            else:
                self.gspell_available = False
                print("Couldn't initialize spell check. Are hunspell, hunspell-en_us, hspell, nuspell, aspell and "
                      "libvoikko installed?")

        self.set_view_style()
        self.set_gtk_theme()

        # Connect the delete event to quit the application
        self.connect("destroy", on_destroy_event)

        self.source_view.grab_focus()

    def create_button_bar(self):
        if self.settings["show-bar"]:
            # we need to destroy and build from scratch in case icon size changed
            if len(self.button_bar_wrapper.get_children()) > 0:
                self.button_bar_wrapper.get_children()[0].destroy()
            self.button_bar = ButtonBar(self, dir_name)
            self.button_bar_wrapper.pack_start(self.button_bar, False, False, 0)
            self.button_bar_wrapper.show_all()
        else:
            self.button_bar_wrapper.hide()

    def text_changed(self):
        return self.buffer.get_text(self.buffer.get_start_iter(), self.buffer.get_end_iter(), True) != self.initial_text

    def reset_initial_text(self):
        self.initial_text = self.buffer.get_text(self.buffer.get_start_iter(), self.buffer.get_end_iter(), True)

    def on_text_changed(self, buffer):
        self.update_cursor_position()
        self.update_stats()

    def update_cursor_position(self):
        """ Get and print the cursor position. """
        insert_mark = self.buffer.get_insert()
        iter_ = self.buffer.get_iter_at_mark(insert_mark)
        line = iter_.get_line()
        column = iter_.get_line_offset()
        self.search_bar.pos_lbl.set_text(f'{self.voc["row"]}: {line + 1} {self.voc["column"]}: {column}')

    def on_cursor_moved(self, buffer, iter_, mark):
        """ Fires when the cursor moves. """
        if mark == buffer.get_insert():  # Ignore selection mark
            self.update_cursor_position()
        else:
            if self.settings["show-stats"]:
                self.update_stats()

    def update_stats(self):
        if self.settings["show-stats"]:
            txt, s, e = selected_text(self.buffer)
            selection = txt[s:e]
            self.search_bar.stat_lbl.set_text(
                f'{self.voc["characters"]}: {len(selection)} {self.voc["words"]}: {len(selection.split())}')

        self.mark_changes_in_ui()

    def mark_changes_in_ui(self):
        if self.text_changed():
            if not self.get_title().startswith("*"):
                self.set_window_title(f"*{self.get_title()}")
                self.search_bar.change_lbl.set_text("*")
        else:
            if self.get_title().startswith("*"):
                self.set_window_title(self.get_title()[1:])
                self.search_bar.change_lbl.set_text("")

    def switch_stats_visibility(self):
        if self.search_bar:
            self.search_bar.stat_lbl.set_visible(self.settings["show-stats"])

    def switch_change_visibility(self):
        if self.search_bar:
            self.search_bar.change_lbl.set_visible(self.settings["show-change"])

    def handle_keyboard_release(self, widget, event):
        if event.keyval == Gdk.KEY_Escape:
            if self.search_bar.search_entry.is_focus() and self.search_bar.search_entry.get_text():
                self.search_bar.search_entry.set_text("")
            else:
                self.source_view.grab_focus()
        elif event.keyval == Gdk.KEY_n and event.state & Gdk.ModifierType.CONTROL_MASK:
            self.new_file()
        elif event.keyval == Gdk.KEY_o and event.state & Gdk.ModifierType.CONTROL_MASK:
            self.open_file()
        elif event.keyval == Gdk.KEY_s and event.state & Gdk.ModifierType.CONTROL_MASK:
            self.save_file()
        elif event.keyval == Gdk.KEY_S and (event.state & Gdk.ModifierType.CONTROL_MASK) and (
                event.state & Gdk.ModifierType.SHIFT_MASK):
            self.save_file_as()
        elif event.keyval == Gdk.KEY_p and event.state & Gdk.ModifierType.CONTROL_MASK:
            self.on_print_btn()
        elif event.keyval == Gdk.KEY_q and event.state & Gdk.ModifierType.CONTROL_MASK:
            self.quit()
        elif event.keyval == Gdk.KEY_z and event.state & Gdk.ModifierType.CONTROL_MASK:
            self.undo()
        elif event.keyval == Gdk.KEY_y and event.state & Gdk.ModifierType.CONTROL_MASK:
            self.redo()
        elif event.keyval == Gdk.KEY_f and event.state & Gdk.ModifierType.CONTROL_MASK:
            self.search_selection()

    def search_selection(self):
        txt, s, e = selected_text(self.buffer)
        selection = txt[s:e]
        if not (s == 0 and e == len(txt)):
            self.search_bar.search_entry.set_text(selection)
        else:
            self.search_bar.search_entry.set_text("")

        self.search_bar.search_entry.grab_focus()

    def on_close(self, widget, event):
        # remember last window dimensions
        size = self.get_size()
        self.settings["window-width"] = size.width
        self.settings["window-height"] = size.height

        # remember last used spell check language
        if self.gspell_available and self.settings["gspell-lang"] != self.checker.get_language().get_code():
            print(f"Storing changed spell check language: {self.checker.get_language().get_code()}")
            self.settings["gspell-lang"] = self.checker.get_language().get_code()

        save_settings(self.settings)

        if self.text_changed():
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
                return False  # Allow closing
            else:
                return True  # Prevent closing
        return False  # Allow closing

    def save_on_exit(self):
        if self.get_title() == f"{voc['untitled']} - Typobuster":
            self.save_file_as(None)
        else:
            self.save_file(None)

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

    def undo(self, *args):
        if self.buffer.can_undo():
            self.buffer.undo()

    def redo(self, *args):
        if self.buffer.can_redo():
            self.buffer.redo()

    def cut_text(self, *args):
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

    def toggle_whitespaces(self, widget):
        self.settings["whitespaces"] = widget.get_active()
        space_drawer = self.source_view.get_space_drawer()
        space_drawer.set_enable_matrix(self.settings["whitespaces"])
        save_settings(self.settings)

    def toggle_highlight_current_row(self, widget):
        self.settings["highlight-current-row"] = widget.get_active()
        self.source_view.set_highlight_current_line(self.settings["highlight-current-row"])
        save_settings(self.settings)

    def toggle_highlight_matching_brackets(self, widget):
        self.settings["highlight-matching-brackets"] = widget.get_active()
        self.source_view.get_buffer().set_highlight_matching_brackets(self.settings["highlight-matching-brackets"])
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

    def on_margin_position_selected(self, sb):
        self.settings["right-margin-position"] = int(sb.get_value())
        self.source_view.set_right_margin_position(self.settings["right-margin-position"])
        save_settings(self.settings)

    def on_icon_size_selected(self, sb):
        self.settings["icon-size"] = int(sb.get_value())
        save_settings(self.settings)
        self.create_button_bar()

    def on_right_margin_toggled(self, cb):
        self.settings["right-margin-show"] = cb.get_active()
        self.source_view.set_show_right_margin(self.settings["right-margin-show"])
        save_settings(self.settings)

    def on_bar_show_toggled(self, cb):
        self.settings["show-bar"] = cb.get_active()
        save_settings(self.settings)
        self.create_button_bar()

    def on_tab_mode_changed(self, combo):
        self.settings["tab-mode"] = combo.get_active_id()
        self.set_tab_mode()
        save_settings(self.settings)

    def on_icon_set_changed(self, combo):
        self.settings["icon-set"] = combo.get_active_id()
        save_settings(self.settings)
        self.create_button_bar()

    def on_auto_indent_changed(self, check_button):
        self.settings["auto-indent"] = check_button.get_active()
        self.set_auto_indent()
        save_settings(self.settings)

    def on_spell_check_switched(self, check_button):
        self.settings["gspell-enable"] = check_button.get_active()
        if self.gspell_available and self.gspell_text_view:
            self.gspell_text_view.set_inline_spell_checking(self.settings["gspell-enable"])
        save_settings(self.settings)

    def on_stats_cb_toggled(self, check_button):
        self.settings["show-stats"] = check_button.get_active()
        self.switch_stats_visibility()
        save_settings(self.settings)
        self.update_stats()

    def on_change_cb_toggled(self, check_button):
        self.settings["show-change"] = check_button.get_active()
        self.switch_change_visibility()
        save_settings(self.settings)
        self.update_stats()

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

    def set_tab_mode(self):
        self.source_view.set_insert_spaces_instead_of_tabs(self.settings["tab-mode"] == "spaces")

    def set_auto_indent(self):
        self.source_view.set_auto_indent(self.settings["auto-indent"])

    def on_theme_changed(self, combo):
        self.settings["gtk-theme-name"] = combo.get_active_id()
        save_settings(self.settings)
        self.set_gtk_theme()

    def set_gtk_theme(self):
        if self.settings["gtk-theme-name"]:
            self.gtk_settings.set_property("gtk-theme-name", self.settings["gtk-theme-name"])
        else:
            theme = subprocess.check_output("gsettings get org.gnome.desktop.interface gtk-theme", shell=True).decode(
                "utf-8")
            self.gtk_settings.set_property("gtk-theme-name", theme[1:-2])

    def on_drag_data_received(self, widget, drag_context, x, y, data, info, time):
        # workaround for drag-data-received being fired twice
        if self.drag_in_progress:
            return
        self.drag_in_progress = True

        """Handle file drop event."""
        uris = data.get_uris()
        if uris:
            f_p = uris[0].replace("file://", "").strip()
            self.load_file(None, f_p)
            global file_path
            file_path = f_p
        self.drag_in_progress = False

    def transform_text(self, widget, transformation):
        start = self.buffer.get_start_iter()
        end = self.buffer.get_end_iter()
        if self.buffer.get_has_selection():
            start, end = self.buffer.get_selection_bounds()
        if start and end:
            text = self.buffer.get_text(start, end, True)

            if transformation == "sentence":
                transformed_text = as_in_sentence(text)
            elif transformation == "title":
                transformed_text = as_in_title(text)
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
            elif transformation == "merge-rows":
                transformed_text = merge_lines(text)
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
        self.set_title(filename)

    def new_file(self, *args):
        title = file_path.split("/")[-1] if file_path else self.voc["untitled"]
        if self.text_changed():
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

        self.buffer.begin_not_undoable_action()
        self.update_text("")
        self.reset_initial_text()
        self.buffer.end_not_undoable_action()
        self.update_stats()
        self.set_window_title(f"{voc['untitled']} - Typobuster")

    def load_file(self, widget, path):
        if self.text_changed():
            resp = self.on_close(None, None)
            if resp:
                return  # Prevent from closing

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
            self.file_stat = os.stat(file_path)
            self.update_recent(path)
            self.menu_bar.recent_menu_item.set_sensitive(True)
        self.buffer.begin_not_undoable_action()
        self.update_text(text)
        self.reset_initial_text()
        self.buffer.end_not_undoable_action()
        self.update_stats()
        self.set_window_title(path)

        self.search_bar.clear()
        self.source_view.grab_focus()

    def open_file(self, *args):
        if self.text_changed():
            if self.on_close(None, None):
                return  # Prevent from closing

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

    def save_file(self, *args):
        if file_path:
            text = self.buffer.get_text(self.buffer.get_start_iter(), self.buffer.get_end_iter(), True)
            result = save_text_file(text, file_path)
            if result == "ok":
                print(f"Saved text to {file_path}")
                self.update_recent(file_path)
                self.file_stat = os.stat(file_path)
                self.reset_initial_text()
                self.update_stats()
            else:
                eprint(f"Error saving text to {file_path}: {result}")
        else:
            self.save_file_as(None)

    def save_file_as(self, *args):
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
                self.file_stat = os.stat(file_path)
                self.update_recent(file_path)
                self.reset_initial_text()
                self.update_stats()
            else:
                eprint(f"Error saving text to {filename}: {result}")
        dialog.destroy()

    def check_file_change(self, widget, event):
        if self.file_stat:
            current_stat = os.stat(file_path)
            if current_stat.st_size != self.file_stat.st_size or current_stat.st_mtime != self.file_stat.st_mtime:
                dialog = Gtk.MessageDialog(
                    parent=self,
                    message_type=Gtk.MessageType.QUESTION,
                    buttons=Gtk.ButtonsType.YES_NO,
                    text=self.voc["file-changed-externally"],
                )
                dialog.format_secondary_text(self.voc["reload-file"])

                response = dialog.run()
                dialog.destroy()

                if response == Gtk.ResponseType.YES:
                    self.load_file(None, file_path)
                    self.file_stat = os.stat(file_path)

                self.file_stat = os.stat(file_path)

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

    def on_print_btn(self, *args):
        print_settings = Gtk.PrintSettings()
        page_setup = Gtk.PageSetup()

        print_operation = Gtk.PrintOperation()
        print_operation.set_print_settings(print_settings)
        print_operation.set_default_page_setup(page_setup)
        print_operation.connect("begin-print", self.begin_print)
        print_operation.connect("draw-page", self.draw_page)

        result = print_operation.run(Gtk.PrintOperationAction.PRINT_DIALOG, self)
        if result == Gtk.PrintOperationResult.APPLY:
            print("Printing in progress...")
        elif result == Gtk.PrintOperationResult.CANCEL:
            print("Print canceled")
        elif result == Gtk.PrintOperationResult.ERROR:
            print("Print error occurred")
        else:
            print(f"Unknown result: {result}")

    def begin_print(self, print_operation, context):
        print("Begin print")
        self.pages = self.paginate_text(context)
        print_operation.set_n_pages(len(self.pages))

    def draw_page(self, print_operation, context, page_nr):
        print("Drawing page")
        cr = context.get_cairo_context()
        cr.set_source_rgb(0, 0, 0)
        cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        cr.set_font_size(10)

        lines = self.pages[page_nr]
        line_height = 14
        y = 10

        for line in lines:
            cr.move_to(10, y)
            cr.show_text(line)
            y += line_height

    def wrap_text(self, cr, text, max_width):
        lines = []
        paragraphs = text.split('\n')

        for paragraph in paragraphs:
            if paragraph.strip() == "":
                lines.append("")  # Preserve empty line
                continue

            words = paragraph.split()
            current_line = []

            for word in words:
                current_line.append(word)
                line_width = cr.text_extents(" ".join(current_line)).width
                if line_width > max_width:
                    current_line.pop()
                    lines.append(" ".join(current_line))
                    current_line = [word]

            if current_line:
                lines.append(" ".join(current_line))

        return lines

    def paginate_text(self, context):
        cr = context.get_cairo_context()
        text = self.buffer.get_text(self.buffer.get_start_iter(), self.buffer.get_end_iter(), True)
        lines = self.wrap_text(cr, text, 450)  # Adjust according to the actual page width in points
        line_height = 14
        page_height = 800  # Adjust according to the actual page height
        max_lines_per_page = int(page_height / line_height)

        pages = []
        current_page = []

        for line in lines:
            if len(current_page) >= max_lines_per_page:
                pages.append(current_page)
                current_page = []

            current_page.append(line)

        if current_page:
            pages.append(current_page)

        return pages

    def quit(self, *args):
        self.close()


def main():
    parser = argparse.ArgumentParser(description="Simple text editor")
    parser.add_argument("file_path", type=str, nargs="?", help="Path of the file to open")
    parser.add_argument("-v",
                        "--version",
                        action="version",
                        version="%(prog)s version {}".format(__version__),
                        help="display version information")

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
        #searchentry-error {
            color: red;
        }
        #bar-button {
            min-width: 16px;
            min-height: 16px;
            background: none;
            border: none;
            padding: 0px;
        }
        #bar-button:hover {
            background-color: rgba(0, 255, 255, 0.5);
        }
        #bar-wrapper {
            padding: 3px;
        }
        """
    provider.load_from_data(css)

    if args.file_path:
        window.load_file(None, args.file_path)

    window.show_all()
    window.switch_stats_visibility()
    window.switch_change_visibility()
    Gtk.main()


# Run the application
if __name__ == "__main__":
    sys.exit(main())
