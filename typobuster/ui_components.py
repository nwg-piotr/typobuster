import os.path

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GdkPixbuf

from typobuster.tools import *
from typobuster.__about__ import __version__


class MenuBar(Gtk.MenuBar):
    def __init__(self, parent_window):
        super().__init__()
        self.settings = parent_window.settings
        self.set_take_focus(False)

        self.parent_window = parent_window

        # File menu
        file_menu = Gtk.Menu()
        file_menu.connect("show", self.update_menu_items_sensitivity)
        file_menu_item = Gtk.MenuItem(label=parent_window.voc["file"])
        file_menu_item.set_submenu(file_menu)

        # File/New
        self.new_menu_item = CustomMenuItem(parent_window.voc["new"], "Ctrl+N")
        file_menu.append(self.new_menu_item)
        self.new_menu_item.connect("activate", parent_window.new_file)

        # File/Open
        open_menu_item = CustomMenuItem(parent_window.voc["open"], "Ctrl+O")
        file_menu.append(open_menu_item)
        open_menu_item.connect("activate", parent_window.open_file)

        # File/Open recent
        self.recent_menu_item = Gtk.MenuItem(label=parent_window.voc["recent-files"])
        file_menu.append(self.recent_menu_item)
        self.recent_menu_item.set_sensitive(os.path.isfile(os.path.join(config_dir(), "recent")))
        file_menu.connect("show", add_recent_menu, self.recent_menu_item, self.parent_window)

        # File/Save
        save_menu_item = CustomMenuItem(parent_window.voc["save"], "Ctrl+S")
        file_menu.append(save_menu_item)
        save_menu_item.connect("activate", parent_window.save_file)

        # File/Save As
        save_as_menu_item = CustomMenuItem(parent_window.voc["save-as"], "Ctrl+Shift+S")
        file_menu.append(save_as_menu_item)
        save_as_menu_item.connect("activate", parent_window.save_file_as)

        sep = Gtk.SeparatorMenuItem()
        file_menu.append(sep)

        # File/Print
        print_menu_item = CustomMenuItem(parent_window.voc["print"], "Ctrl+P")
        file_menu.append(print_menu_item)
        print_menu_item.connect("activate", parent_window.on_print_btn)

        sep = Gtk.SeparatorMenuItem()
        file_menu.append(sep)

        # Quit menu item
        quit_menu_item = CustomMenuItem(parent_window.voc["quit"], "Ctrl+Q")
        file_menu.append(quit_menu_item)
        quit_menu_item.connect("activate", parent_window.quit)

        # Edit menu
        edit_menu = Gtk.Menu()
        edit_menu.connect("show", self.update_menu_items_sensitivity)
        edit_menu_item = Gtk.MenuItem(label=parent_window.voc["edit"])
        edit_menu_item.set_submenu(edit_menu)

        # Edit/Undo
        self.undo_menu_item = CustomMenuItem(parent_window.voc["undo"], "Ctrl+Z")
        edit_menu.append(self.undo_menu_item)
        self.undo_menu_item.connect("activate", parent_window.undo)

        # Edit/Redo
        self.redo_menu_item = CustomMenuItem(parent_window.voc["redo"], "Ctrl+Y")
        edit_menu.append(self.redo_menu_item)
        self.redo_menu_item.connect("activate", parent_window.redo)

        # Edit/Copy
        copy_menu_item = CustomMenuItem(parent_window.voc["copy"], "Ctrl+C")
        edit_menu.append(copy_menu_item)
        copy_menu_item.connect("activate", parent_window.copy_text)

        # Edit/Cut
        cut_menu_item = CustomMenuItem(parent_window.voc["cut"], "Ctrl+X")
        edit_menu.append(cut_menu_item)
        cut_menu_item.connect("activate", parent_window.cut_text)

        # Edit/Paste
        paste_menu_item = CustomMenuItem(parent_window.voc["paste"], "Ctrl+V")
        edit_menu.append(paste_menu_item)
        paste_menu_item.connect("activate", parent_window.paste_text)

        # Edit/Delete
        delete_menu_item = CustomMenuItem(parent_window.voc["delete"], "Delete")
        edit_menu.append(delete_menu_item)
        delete_menu_item.connect("activate", parent_window.delete_text)

        # Transform menu item
        transform_menu_item = Gtk.MenuItem(label=parent_window.voc["transform"])
        edit_menu.append(transform_menu_item)

        # Transform/As in sentence
        transform_as_in_sentence_menu_item = Gtk.MenuItem(label=parent_window.voc["as-in-sentence"])
        transform_menu_item.set_submenu(Gtk.Menu())
        transform_menu_item.get_submenu().append(transform_as_in_sentence_menu_item)
        transform_as_in_sentence_menu_item.connect("activate", parent_window.transform_text, "sentence")

        # Transform/As In Title
        transform_as_in_title_menu_item = Gtk.MenuItem(label=parent_window.voc["as-in-title"])
        transform_menu_item.get_submenu().append(transform_as_in_title_menu_item)
        transform_as_in_title_menu_item.connect("activate", parent_window.transform_text, "title")

        # Transform/To Uppercase
        transform_uppercase_menu_item = Gtk.MenuItem(label=parent_window.voc["uppercase"])
        transform_menu_item.get_submenu().append(transform_uppercase_menu_item)
        transform_uppercase_menu_item.connect("activate", parent_window.transform_text, "uppercase")

        # Transform/to lowercase
        transform_lowercase_menu_item = Gtk.MenuItem(label=parent_window.voc["lowercase"])
        transform_menu_item.get_submenu().append(transform_lowercase_menu_item)
        transform_lowercase_menu_item.connect("activate", parent_window.transform_text, "lowercase")

        # Transform/toCamelCase
        transform_camelcase_menu_item = Gtk.MenuItem(label=parent_window.voc["camel-case"])
        transform_menu_item.get_submenu().append(transform_camelcase_menu_item)
        transform_camelcase_menu_item.connect("activate", parent_window.transform_text, "camelcase")

        # Transform/to_snake_case
        transform_snakecase_menu_item = Gtk.MenuItem(label=parent_window.voc["snake-case"])
        transform_menu_item.get_submenu().append(transform_snakecase_menu_item)
        transform_snakecase_menu_item.connect("activate", parent_window.transform_text, "snakecase")

        # Transform/to-kebab-case
        transform_kebabcase_menu_item = Gtk.MenuItem(label=parent_window.voc["kebab-case"])
        transform_menu_item.get_submenu().append(transform_kebabcase_menu_item)
        transform_kebabcase_menu_item.connect("activate", parent_window.transform_text, "kebabcase")

        # Transform/- unordered list
        transform_unordered_list_menu_item = Gtk.MenuItem(label=parent_window.voc["unordered-list"])
        transform_menu_item.get_submenu().append(transform_unordered_list_menu_item)
        transform_unordered_list_menu_item.connect("activate", parent_window.transform_text, "unordered")

        # Transform/1. ordered list
        transform_ordered_list_menu_item = Gtk.MenuItem(label=parent_window.voc["ordered-list"])
        transform_menu_item.get_submenu().append(transform_ordered_list_menu_item)
        transform_ordered_list_menu_item.connect("activate", parent_window.transform_text, "ordered")

        # Transform/First word to the end
        first_to_end_item = Gtk.MenuItem(label=parent_window.voc["first-to-end"])
        transform_menu_item.get_submenu().append(first_to_end_item)
        first_to_end_item.connect("activate", parent_window.transform_text, "first-to-end")

        # TransformLast word to the beginning
        last_to_beginning_item = Gtk.MenuItem(label=parent_window.voc["last-to-beginning"])
        transform_menu_item.get_submenu().append(last_to_beginning_item)
        last_to_beginning_item.connect("activate", parent_window.transform_text, "last-to-beginning")

        # Merge lines
        merge_lines_menu_item = Gtk.MenuItem(label=parent_window.voc["merge-rows"])
        transform_menu_item.get_submenu().append(merge_lines_menu_item)
        merge_lines_menu_item.connect("activate", parent_window.transform_text, "merge-rows")

        separator = Gtk.SeparatorMenuItem()
        edit_menu.append(separator)

        # Preferences menu item
        preferences_menu_item = Gtk.MenuItem(label=parent_window.voc["preferences"])
        edit_menu.append(preferences_menu_item)
        preferences_menu_item.connect("activate", parent_window.show_preferences)

        # View menu
        view_menu = Gtk.Menu()
        view_menu_item = Gtk.MenuItem(label=parent_window.voc["view"])
        view_menu_item.set_submenu(view_menu)

        # Line numbers menu item
        self.line_numbers_menu_item = Gtk.CheckMenuItem(parent_window.voc["line-numbers"])
        view_menu.append(self.line_numbers_menu_item)
        self.line_numbers_menu_item.set_active(self.settings["view-line-numbers"])
        self.line_numbers_menu_item.connect("toggled", parent_window.toggle_line_numbers)

        # Whitespaces menu item
        whitespaces_menu_item = Gtk.CheckMenuItem(parent_window.voc["whitespaces"])
        view_menu.append(whitespaces_menu_item)
        whitespaces_menu_item.set_active(self.settings["whitespaces"])
        whitespaces_menu_item.connect("toggled", parent_window.toggle_whitespaces)

        # Highlight current row item
        self.highlight_current_row_menu_item = Gtk.CheckMenuItem(parent_window.voc["highlight-current-row"])
        view_menu.append(self.highlight_current_row_menu_item)
        self.highlight_current_row_menu_item.set_active(self.settings["highlight-current-row"])
        self.highlight_current_row_menu_item.connect("toggled", parent_window.toggle_highlight_current_row)

        # Highlight matching brackets
        self.highlight_matching_brackets_menu_item = Gtk.CheckMenuItem(parent_window.voc["highlight-matching-brackets"])
        view_menu.append(self.highlight_matching_brackets_menu_item)
        self.highlight_matching_brackets_menu_item.set_active(self.settings["highlight-matching-brackets"])
        self.highlight_matching_brackets_menu_item.connect("toggled", parent_window.toggle_highlight_matching_brackets)

        # Wrap menu item
        self.wrap_menu_item = Gtk.CheckMenuItem(parent_window.voc["wrap-lines"])
        view_menu.append(self.wrap_menu_item)
        self.wrap_menu_item.set_active(self.settings["wrap-lines"])
        self.wrap_menu_item.connect("toggled", parent_window.toggle_line_wrap)

        # Syntax menu item
        syntax_menu_item = Gtk.MenuItem(label=parent_window.voc["syntax-highlight"])
        view_menu.append(syntax_menu_item)
        view_menu.connect("show", add_syntax_menu, syntax_menu_item, self.parent_window)

        # Tools menu
        tools_menu = Gtk.Menu()
        tools_menu.connect("show", self.update_menu_items_sensitivity)
        tools_menu_item = Gtk.MenuItem(label=parent_window.voc["tools"])
        tools_menu_item.set_submenu(tools_menu)

        # Sanitize menu item
        self.sanitize_menu_item = Gtk.MenuItem(label=parent_window.voc["web-cleanup"])
        tools_menu.append(self.sanitize_menu_item)
        self.sanitize_menu_item.connect("show", self.update_menu_items_sensitivity)
        self.sanitize_menu_item.connect("activate", parent_window.sanitize_text)
        self.sanitize_menu_item.set_can_focus(False)

        # Sort menu item
        sort_menu_item = Gtk.MenuItem(label=parent_window.voc["sort-rows"])
        tools_menu.append(sort_menu_item)

        sort_menu = Gtk.Menu()
        sort_asc_menu_item = Gtk.MenuItem(label=parent_window.voc["ascending"])
        sort_menu.append(sort_asc_menu_item)
        sort_asc_menu_item.connect("activate", parent_window.transform_text, "sort-asc")
        sort_desc_menu_item = Gtk.MenuItem(label=parent_window.voc["descending"])
        sort_menu.append(sort_desc_menu_item)
        sort_desc_menu_item.connect("activate", parent_window.transform_text, "sort-desc")
        sort_menu_item.set_submenu(sort_menu)

        remove_empty_rows_item = Gtk.MenuItem(label=parent_window.voc["remove-empty-rows"])
        tools_menu.append(remove_empty_rows_item)
        remove_empty_rows_item.connect("activate", parent_window.transform_text, "remove-empty-rows")

        remove_non_ascii_item = Gtk.MenuItem(label=parent_window.voc["remove-non-ascii"])
        tools_menu.append(remove_non_ascii_item)
        remove_non_ascii_item.connect("activate", parent_window.transform_text, "remove-non-ascii")

        # Help menu
        help_menu = Gtk.Menu()
        help_menu_item = Gtk.MenuItem(label=parent_window.voc["help"])
        help_menu_item.set_submenu(help_menu)

        # About menu item
        about_menu_item = Gtk.MenuItem(label=parent_window.voc["about"])
        help_menu.append(about_menu_item)
        about_menu_item.connect("activate", parent_window.show_about)

        # Append menu items to the menu bar
        self.append(file_menu_item)
        self.append(edit_menu_item)
        self.append(view_menu_item)
        self.append(tools_menu_item)
        self.append(help_menu_item)

        self.update_menu_items_sensitivity()

    def update_menu_items_sensitivity(self, *args):
        self.undo_menu_item.set_sensitive(self.parent_window.buffer.can_undo())
        self.redo_menu_item.set_sensitive(self.parent_window.buffer.can_redo())
        self.new_menu_item.set_sensitive(self.parent_window.buffer.get_char_count() > 0)
        self.sanitize_menu_item.set_sensitive(self.parent_window.buffer.get_char_count() > 0)


class CustomMenuItem(Gtk.MenuItem):
    def __init__(self, label, desc=""):
        super().__init__()
        hbox = Gtk.Box(Gtk.Orientation.HORIZONTAL, spacing=0)
        self.add(hbox)
        label = Gtk.Label.new(label)
        label.set_property("xalign", 0)
        label.set_property("yalign", 0.5)
        hbox.pack_start(label, True, True, 0)
        if desc:
            desc = Gtk.Label(label=desc)
            desc.set_property("xalign", 1)
            desc.set_property("yalign", 0.5)
            hbox.pack_start(desc, True, True, 0)


def add_recent_menu(widget, parent_item, parent_window):
    menu = Gtk.Menu()
    recent_file = os.path.join(config_dir(), "recent")
    recent_paths = load_text_file(recent_file).splitlines() if os.path.isfile(recent_file) else []
    for path in recent_paths:
        item = Gtk.MenuItem(label=path)
        item.connect("activate", parent_window.load_file, path)
        menu.append(item)
        menu.show_all()
    parent_item.set_submenu(menu)


def add_syntax_menu(widget, parent_item, parent_window):
    menu = Gtk.Menu()
    item = Gtk.MenuItem(label=parent_window.voc["plain-text"])
    item.connect("activate", parent_window.set_syntax, "none")
    menu.append(item)
    for key in parent_window.syntax_dict:
        item = Gtk.MenuItem(label=parent_window.syntax_dict[key])
        item.connect("activate", parent_window.set_syntax, key)
        menu.append(item)
    menu.show_all()
    parent_item.set_submenu(menu)


class ButtonBar(Gtk.Box):
    def __init__(self, parent_window, dir_name):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        self.settings = parent_window.settings
        self.icons_path = os.path.join(dir_name, "icons", self.settings["icon-set"])

        btn_new = self.create_button("file-new.svg")
        btn_new.set_tooltip_text(parent_window.voc["new"])
        self.pack_start(btn_new, False, False, 0)
        btn_new.connect("clicked", parent_window.new_file)

        btn_open = self.create_button("file-open.svg")
        btn_open.set_tooltip_text(parent_window.voc["open"])
        self.pack_start(btn_open, False, False, 0)
        btn_open.connect("clicked", parent_window.open_file)

        btn_save = self.create_button("file-save.svg")
        btn_save.set_tooltip_text(parent_window.voc["save"])
        self.pack_start(btn_save, False, False, 0)
        btn_save.connect("clicked", parent_window.save_file)

        btn_save_as = self.create_button("file-save-as.svg")
        btn_save_as.set_tooltip_text(parent_window.voc["save-as"])
        self.pack_start(btn_save_as, False, False, 0)
        btn_save_as.connect("clicked", parent_window.save_file_as)

        self.pack_start(self.create_separator(), False, False, 0)

        btn_undo = self.create_button("edit-undo.svg")
        btn_undo.set_tooltip_text(parent_window.voc["undo"])
        self.pack_start(btn_undo, False, False, 0)
        btn_undo.connect("clicked", parent_window.undo)

        btn_redo = self.create_button("edit-redo.svg")
        btn_redo.set_tooltip_text(parent_window.voc["redo"])
        self.pack_start(btn_redo, False, False, 0)
        btn_redo.connect("clicked", parent_window.redo)

        btn_copy = self.create_button("edit-copy.svg")
        btn_copy.set_tooltip_text(parent_window.voc["copy"])
        self.pack_start(btn_copy, False, False, 0)
        btn_copy.connect("clicked", parent_window.copy_text)

        btn_cut = self.create_button("edit-cut.svg")
        btn_cut.set_tooltip_text(parent_window.voc["cut"])
        self.pack_start(btn_cut, False, False, 0)
        btn_cut.connect("clicked", parent_window.cut_text)

        btn_paste = self.create_button("edit-paste.svg")
        btn_paste.set_tooltip_text(parent_window.voc["paste"])
        self.pack_start(btn_paste, False, False, 0)
        btn_paste.connect("clicked", parent_window.paste_text)

        self.pack_start(self.create_separator(), False, False, 0)

        btn_sentence = self.create_button("as-in-sentence.svg")
        btn_sentence.set_tooltip_text(parent_window.voc["as-in-sentence"])
        self.pack_start(btn_sentence, False, False, 0)
        btn_sentence.connect("clicked", parent_window.transform_text, "sentence")

        btn_title = self.create_button("as-in-title.svg")
        btn_title.set_tooltip_text(parent_window.voc["as-in-title"])
        self.pack_start(btn_title, False, False, 0)
        btn_title.connect("clicked", parent_window.transform_text, "title")

        btn_uppercase = self.create_button("uppercase.svg")
        btn_uppercase.set_tooltip_text(parent_window.voc["uppercase"])
        self.pack_start(btn_uppercase, False, False, 0)
        btn_uppercase.connect("clicked", parent_window.transform_text, "uppercase")

        btn_lowercase = self.create_button("lowercase.svg")
        btn_lowercase.set_tooltip_text(parent_window.voc["lowercase"])
        self.pack_start(btn_lowercase, False, False, 0)
        btn_lowercase.connect("clicked", parent_window.transform_text, "lowercase")

        btn_camelcase = self.create_button("camel-case.svg")
        btn_camelcase.set_tooltip_text(parent_window.voc["camel-case"])
        self.pack_start(btn_camelcase, False, False, 0)
        btn_camelcase.connect("clicked", parent_window.transform_text, "camelcase")

        btn_snakecase = self.create_button("snake-case.svg")
        btn_snakecase.set_tooltip_text(parent_window.voc["snake-case"])
        self.pack_start(btn_snakecase, False, False, 0)
        btn_snakecase.connect("clicked", parent_window.transform_text, "snakecase")

        btn_kebabcase = self.create_button("kebab-case.svg")
        btn_kebabcase.set_tooltip_text(parent_window.voc["kebab-case"])
        self.pack_start(btn_kebabcase, False, False, 0)
        btn_kebabcase.connect("clicked", parent_window.transform_text, "kebabcase")

        btn_unordered = self.create_button("unordered-list.svg")
        btn_unordered.set_tooltip_text(parent_window.voc["unordered-list"])
        self.pack_start(btn_unordered, False, False, 0)
        btn_unordered.connect("clicked", parent_window.transform_text, "unordered")

        btn_ordered = self.create_button("ordered-list.svg")
        btn_ordered.set_tooltip_text(parent_window.voc["ordered-list"])
        self.pack_start(btn_ordered, False, False, 0)
        btn_ordered.connect("clicked", parent_window.transform_text, "ordered")

        btn_first = self.create_button("first-to-end.svg")
        btn_first.set_tooltip_text(parent_window.voc["first-to-end"])
        self.pack_start(btn_first, False, False, 0)
        btn_first.connect("clicked", parent_window.transform_text, "first-to-end")

        btn_last = self.create_button("last-to-beginning.svg")
        btn_last.set_tooltip_text(parent_window.voc["last-to-beginning"])
        self.pack_start(btn_last, False, False, 0)
        btn_last.connect("clicked", parent_window.transform_text, "last-to-beginning")

        btn_merge = self.create_button("merge-rows.svg")
        btn_merge.set_tooltip_text(parent_window.voc["merge-rows"])
        self.pack_start(btn_merge, False, False, 0)
        btn_merge.connect("clicked", parent_window.transform_text, "merge-rows")

        self.pack_start(self.create_separator(), False, False, 0)

        btn_web = self.create_button("web-cleanup.svg")
        btn_web.set_tooltip_text(parent_window.voc["web-cleanup"])
        self.pack_start(btn_web, False, False, 0)
        btn_web.connect("clicked", parent_window.sanitize_text)

        btn_sort_ascending = self.create_button("sort-ascending.svg")
        btn_sort_ascending.set_tooltip_text(parent_window.voc["ascending"])
        self.pack_start(btn_sort_ascending, False, False, 0)
        btn_sort_ascending.connect("clicked", parent_window.transform_text, "sort-asc")

        btn_sort_descending = self.create_button("sort-descending.svg")
        btn_sort_descending.set_tooltip_text(parent_window.voc["descending"])
        self.pack_start(btn_sort_descending, False, False, 0)
        btn_sort_descending.connect("clicked", parent_window.transform_text, "sort-desc")

        btn_remove_empty = self.create_button("remove-empty-rows.svg")
        btn_remove_empty.set_tooltip_text(parent_window.voc["remove-empty-rows"])
        self.pack_start(btn_remove_empty, False, False, 0)
        btn_remove_empty.connect("clicked", parent_window.transform_text, "remove-empty-rows")

        btn_remove_non_ascii = self.create_button("remove-non-ascii.svg")
        btn_remove_non_ascii.set_tooltip_text(parent_window.voc["remove-non-ascii"])
        self.pack_start(btn_remove_non_ascii, False, False, 0)
        btn_remove_non_ascii.connect("clicked", parent_window.transform_text, "remove-non-ascii")

        self.show_all()

    def create_button(self, icon_name):
        btn = Gtk.Button()
        btn.set_image(self.create_image(icon_name))
        btn.set_property("name", "bar-button")
        return btn

    def create_separator(self):
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(os.path.join(self.icons_path, "separator.svg"),
                                                        self.settings["icon-size"] / 2, self.settings["icon-size"])
        img = Gtk.Image.new_from_pixbuf(pixbuf)
        return img

    def create_image(self, icon_name):
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(os.path.join(self.icons_path, icon_name),
                                                        self.settings["icon-size"], self.settings["icon-size"])
        return Gtk.Image.new_from_pixbuf(pixbuf)


class SanitizationDialog(Gtk.Window):
    def __init__(self, parent_window, buffer):
        super().__init__(title="Sanitize Text")
        self.set_transient_for(parent_window)
        self.set_modal(True)
        self.parent_window = parent_window
        self.settings = parent_window.settings

        self.connect("key-release-event", self.handle_keyboard_release)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        vbox.set_property("margin", 12)
        self.add(vbox)

        self.sanitize_hyphens = Gtk.CheckButton(label=parent_window.voc["hyphens"])
        self.sanitize_hyphens.set_active(self.settings["sanitize-hyphens"])
        self.sanitize_hyphens.connect("toggled", self.switch_settings_key, "sanitize-hyphens")
        vbox.pack_start(self.sanitize_hyphens, False, False, 0)

        self.sanitize_quotes = Gtk.CheckButton(label=parent_window.voc["quotes"])
        self.sanitize_quotes.set_active(self.settings["sanitize-quotes"])
        self.sanitize_quotes.connect("toggled", self.switch_settings_key, "sanitize-quotes")
        vbox.pack_start(self.sanitize_quotes, False, False, 0)

        self.sanitize_punctuation_marks = Gtk.CheckButton(label=parent_window.voc["punctuation-marks"])
        self.sanitize_punctuation_marks.set_active(self.settings["sanitize-punctuation-marks"])
        self.sanitize_punctuation_marks.connect("toggled", self.switch_settings_key, "sanitize-punctuation-marks")
        vbox.pack_start(self.sanitize_punctuation_marks, False, False, 0)

        self.sanitize_spaces = Gtk.CheckButton(label=parent_window.voc["spaces"])
        self.sanitize_spaces.set_active(self.settings["sanitize-spaces"])
        self.sanitize_spaces.connect("toggled", self.switch_settings_key, "sanitize-spaces")
        vbox.pack_start(self.sanitize_spaces, False, False, 0)

        self.add_spaces_after = Gtk.CheckButton(label=parent_window.voc["add-spaces-after-punctuation"])
        self.add_spaces_after.set_active(self.settings["sanitize-add-spaces-after-punctuation"])
        self.add_spaces_after.connect("toggled", self.switch_settings_key,
                                      "sanitize-add-spaces-after-punctuation")
        vbox.pack_start(self.add_spaces_after, False, False, 0)

        self.sanitize_eol = Gtk.CheckButton(label=parent_window.voc["eol-chars"])
        self.sanitize_eol.set_active(self.settings["sanitize-eol"])
        self.sanitize_eol.connect("toggled", self.switch_settings_key, "sanitize-eol")
        vbox.pack_start(self.sanitize_eol, False, False, 0)

        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        hbox.set_property("margin-top", 12)
        vbox.pack_start(hbox, False, False, 0)

        button = Gtk.Button(label=parent_window.voc["sanitize"])
        hbox.pack_end(button, False, False, 0)
        button.connect("clicked", self.sanitize_text, buffer)

        button = Gtk.Button(label=parent_window.voc["close"])
        hbox.pack_end(button, False, False, 0)
        button.connect("clicked", lambda x: self.destroy())

        self.show_all()

    def handle_keyboard_release(self, widget, event):
        if event.keyval == Gdk.KEY_Escape:
            self.destroy()

    def switch_settings_key(self, chekbox, key):
        if key in self.settings:
            self.settings[key] = chekbox.get_active()
            save_settings(self.settings)
        else:
            print(f"Key '{key}' not found in settings")

    def sanitize_text(self, widget, buffer):
        text, start_idx, end_idx = selected_text(buffer)

        if self.settings["sanitize-hyphens"]:
            text = sanitize_hyphens(text, start_idx, end_idx)

        if self.settings["sanitize-quotes"]:
            text = sanitize_quotes(text, start_idx, end_idx)

        if self.settings["sanitize-punctuation-marks"]:
            text = sanitize_punctuation_marks(text, start_idx, end_idx)

        if self.settings["sanitize-add-spaces-after-punctuation"]:
            text = add_spaces_after_punctuation_marks(text, start_idx, end_idx)

        if self.settings["sanitize-spaces"]:
            text = sanitize_spaces(text, start_idx, end_idx, self.settings["tab-mode"] == "insert-spaces",
                                   self.settings["tab-width"])

        if self.settings["sanitize-eol"]:
            text = sanitize_eol(text, start_idx, end_idx)

        self.parent_window.update_text(text)
        self.destroy()


class AboutWindow(Gtk.AboutDialog):
    def __init__(self, parent_window):
        super().__init__()
        self.set_transient_for(parent_window)
        self.set_program_name("Typobuster")
        self.set_copyright(parent_window.voc["copyright"])
        self.set_comments(parent_window.voc["description"])
        self.set_website("https://github.com/nwg-piotr/typobuster")
        self.set_website_label("GitHub repository")
        self.set_authors(["Piotr Miller"])
        self.set_translator_credits("Marcelo dos Santos Mafra (pt_BR)\nPiotr Miller (pl_PL)")
        self.set_license_type(Gtk.License.GPL_3_0)
        self.set_version(f'{parent_window.voc["version"]}: {__version__}')

        # Load icon by name from the system theme
        icon_theme = Gtk.IconTheme.get_default()
        icon_name = "typobuster"
        pixbuf = icon_theme.load_icon(icon_name, 128, 0)  # 128x128 size
        self.set_logo(pixbuf)

        self.set_keep_above(True)
        self.connect("response", lambda x, y: self.destroy())
        self.show_all()


class PreferencesDialog(Gtk.Dialog):
    def __init__(self, parent):
        super().__init__(title="Preferences", transient_for=parent, modal=True)

        self.grid = Gtk.Grid(margin_top=10, margin_bottom=10, margin_start=10, margin_end=10, column_spacing=10,
                             row_spacing=10)
        self.get_content_area().pack_start(self.grid, False, False, 0)

        # Theme Selector
        self.theme_label = Gtk.Label(label=parent.voc["gtk-theme"], halign=Gtk.Align.START)
        self.grid.attach(self.theme_label, 0, 0, 1, 1)

        self.theme_combo = Gtk.ComboBoxText()
        self.theme_combo.append("", parent.voc["system-default"])
        for name in get_theme_names():
            self.theme_combo.append(name, name)

        if parent.settings["gtk-theme-name"]:
            self.theme_combo.set_active_id(parent.settings["gtk-theme-name"])
        else:
            self.theme_combo.set_active_id("")

        self.theme_combo.connect("changed", parent.on_theme_changed)
        self.grid.attach(self.theme_combo, 1, 0, 1, 1)

        # Font Selector
        self.font_size_label = Gtk.Label(label=parent.voc["editor-font"], halign=Gtk.Align.START)
        self.grid.attach(self.font_size_label, 0, 1, 1, 1)

        self.font_chooser_btn = Gtk.FontButton()
        self.font_chooser_btn.set_use_font(True)
        self.font_chooser_btn.set_font_name(parent.settings["gtk-font-name"])
        self.font_chooser_btn.connect("font-set", parent.on_font_selected)
        self.grid.attach(self.font_chooser_btn, 1, 1, 1, 1)

        self.right_margin_label = Gtk.Label(label=parent.voc["right-margin-position"], halign=Gtk.Align.START)
        self.grid.attach(self.right_margin_label, 0, 2, 1, 1)

        right_margin_sb = Gtk.SpinButton.new_with_range(1, 1024.0, 1)
        right_margin_sb.set_value(parent.settings["right-margin-position"])
        self.grid.attach(right_margin_sb, 1, 2, 1, 1)
        right_margin_sb.connect("value-changed", parent.on_margin_position_selected)

        right_margin_cb = Gtk.CheckButton.new_with_label(parent.voc["show"])
        right_margin_cb.set_active(parent.settings["right-margin-show"])
        self.grid.attach(right_margin_cb, 2, 2, 1, 1)
        right_margin_cb.connect("toggled", parent.on_right_margin_toggled)

        self.icon_size_label = Gtk.Label(label=parent.voc["button-bar-icon-size"], halign=Gtk.Align.START)
        self.grid.attach(self.icon_size_label, 0, 3, 1, 1)

        icon_bar_cb = Gtk.CheckButton.new_with_label(parent.voc["show"])
        icon_bar_cb.set_active(parent.settings["show-bar"])
        self.grid.attach(icon_bar_cb, 2, 3, 1, 1)
        icon_bar_cb.connect("toggled", parent.on_bar_show_toggled)

        icon_size_sb = Gtk.SpinButton.new_with_range(16, 128, 4)
        icon_size_sb.set_value(parent.settings["icon-size"])
        self.grid.attach(icon_size_sb, 1, 3, 1, 1)
        icon_size_sb.connect("value-changed", parent.on_icon_size_selected)

        icon_set_label = Gtk.Label(label=parent.voc["button-bar-icon-set"], halign=Gtk.Align.START)
        self.grid.attach(icon_set_label, 0, 4, 1, 1)

        icon_set_combo = Gtk.ComboBoxText()
        icon_set_combo.append("light", parent.voc["light"])
        icon_set_combo.append("dark", parent.voc["dark"])
        icon_set_combo.set_active_id(parent.settings["icon-set"])
        icon_set_combo.connect("changed", parent.on_icon_set_changed)
        self.grid.attach(icon_set_combo, 1, 4, 1, 1)

        self.tab_width_label = Gtk.Label(label=parent.voc["tab-width"], halign=Gtk.Align.START)
        self.grid.attach(self.tab_width_label, 0, 5, 1, 1)

        tab_width_sb = Gtk.SpinButton.new_with_range(1, 32.0, 1)
        tab_width_sb.set_value(parent.settings["tab-width"])
        tab_width_sb.connect("value-changed", parent.on_tab_with_selected)
        self.grid.attach(tab_width_sb, 1, 5, 1, 1)

        self.tab_mode_label = Gtk.Label(label=parent.voc["tab-mode"], halign=Gtk.Align.START)
        self.grid.attach(self.tab_mode_label, 0, 6, 1, 1)

        self.tab_mode_combo = Gtk.ComboBoxText()
        self.tab_mode_combo.append("tabs", parent.voc["insert-tabs"])
        self.tab_mode_combo.append("spaces", parent.voc["insert-spaces"])
        self.tab_mode_combo.set_active_id(parent.settings["tab-mode"])
        self.tab_mode_combo.connect("changed", parent.on_tab_mode_changed)
        self.grid.attach(self.tab_mode_combo, 1, 6, 1, 1)

        self.auto_indent_cb = Gtk.CheckButton(label=parent.voc["auto-indent"])
        self.auto_indent_cb.set_active(parent.settings["auto-indent"])
        self.auto_indent_cb.connect("toggled", parent.on_auto_indent_changed)
        self.grid.attach(self.auto_indent_cb, 0, 7, 1, 1)

        self.spell_check_cb = Gtk.CheckButton(label=parent.voc["spell-check"])
        self.spell_check_cb.set_sensitive(parent.gspell_available)
        if not parent.gspell_available:
            self.spell_check_cb.set_tooltip_text(parent.voc["gspell-missing"])
        self.spell_check_cb.set_active(parent.settings["gspell-enable"])
        self.spell_check_cb.connect("toggled", parent.on_spell_check_switched)
        self.grid.attach(self.spell_check_cb, 1, 7, 1, 1)

        self.stats_cb = Gtk.CheckButton(label=parent.voc["show-stats"])
        self.stats_cb.set_active(parent.settings["show-stats"])
        self.stats_cb.connect("toggled", parent.on_stats_cb_toggled)
        self.grid.attach(self.stats_cb, 0, 8, 1, 1)

        self.change_cb = Gtk.CheckButton(label=parent.voc["show-change-mark"])
        self.change_cb.set_active(parent.settings["show-change"])
        self.change_cb.connect("toggled", parent.on_change_cb_toggled)
        self.grid.attach(self.change_cb, 1, 8, 1, 1)

        # OK Button
        hbox = Gtk.Box(Gtk.Orientation.HORIZONTAL, 0)
        self.grid.attach(hbox, 0, 9, 3, 1)
        self.ok_button = Gtk.Button(label=parent.voc["close"])
        self.ok_button.connect("clicked", lambda x: self.close())
        hbox.pack_end(self.ok_button, False, False, 0)

        self.show_all()


class SearchBar(Gtk.Box):
    def __init__(self, parent_window):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.HORIZONTAL, spacing=3)
        self.set_property("margin", 3)
        self.parent_window = parent_window
        self.matches = None
        self.match_idx = -1

        self.search_entry = Gtk.SearchEntry()
        self.pack_start(self.search_entry, False, False, 1)
        self.search_entry.set_property("name", "searchentry")
        self.search_entry.set_tooltip_text(parent_window.voc["search"])
        self.search_entry.connect("search-changed", self.on_search_changed, parent_window.buffer)
        self.search_entry.connect("key-release-event", self.handle_keyboard_release)

        btn = Gtk.Button.new_from_icon_name("go-up-symbolic", Gtk.IconSize.MENU)
        self.pack_start(btn, False, False, 0)
        btn.connect("clicked", self.highlight_match, "up")

        btn = Gtk.Button.new_from_icon_name("go-down-symbolic", Gtk.IconSize.MENU)
        self.pack_start(btn, False, False, 0)
        btn.connect("clicked", self.highlight_match, "down")

        self.replace_entry = Gtk.Entry()
        self.replace_entry.set_icon_from_icon_name(Gtk.EntryIconPosition.SECONDARY, "edit-find-replace-symbolic")
        self.replace_entry.set_tooltip_text(parent_window.voc["replace-with"])
        self.replace_entry.connect("icon-press", lambda x, y, z: self.replace_entry.set_text(""))
        self.pack_start(self.replace_entry, False, False, 0)

        btn = Gtk.Button.new_from_icon_name("emblem-ok-symbolic", Gtk.IconSize.MENU)
        self.pack_start(btn, False, False, 0)
        btn.connect("clicked", self.replace)

        self.pos_lbl = Gtk.Label.new(f'{parent_window.voc["row"]}: 1 {parent_window.voc["column"]}: 0')
        self.pack_end(self.pos_lbl, False, False, 3)

        self.stat_lbl = Gtk.Label.new("0")
        self.pack_end(self.stat_lbl, False, False, 3)

        if parent_window.settings["syntax"] == "none":
            s_lbl = parent_window.voc["plain-text"]
        else:
            s_lbl = parent_window.syntax_dict[parent_window.settings["syntax"]]
        self.syntax_lbl = Gtk.Label.new(s_lbl)
        self.pack_end(self.syntax_lbl, False, False, 0)

        self.change_lbl = Gtk.Label.new("")
        self.pack_end(self.change_lbl, False, False, 0)

        self.show_all()

    def handle_keyboard_release(self, widget, event):
        if event.keyval == Gdk.KEY_Return:
            self.highlight_match(widget, "down")

    def on_search_changed(self, widget, buffer):
        self.match_idx = -1
        phrase = self.search_entry.get_text()
        if phrase:
            start = buffer.get_start_iter()
            end = buffer.get_end_iter()
            text = buffer.get_text(start, end, True)

            if phrase in text:
                self.search_entry.set_property("name", "searchentry")
            else:
                self.search_entry.set_property("name", "searchentry-error")

            self.matches = list(re.finditer(re.escape(phrase), text))

    def highlight_match(self, widget, direction):
        if self.search_entry.get_text():
            if direction == "down":
                if self.match_idx == -1:
                    self.match_idx = 0

                start, end = self.matches[self.match_idx].span()
                self.parent_window.select_range(start, end)
                iter_start = self.parent_window.buffer.get_iter_at_offset(start)
                self.parent_window.source_view.scroll_to_iter(iter_start, 0.2, False, 0.5, 0.5)

                if self.match_idx < len(self.matches) - 1:
                    self.match_idx += 1
                else:
                    self.match_idx = 0

            elif direction == "up":
                if self.match_idx == -1:
                    self.match_idx = len(self.matches) - 1

                start, end = self.matches[self.match_idx].span()
                self.parent_window.select_range(start, end)
                iter_start = self.parent_window.buffer.get_iter_at_offset(start)
                self.parent_window.source_view.scroll_to_iter(iter_start, 0.2, False, 0.5, 0.5)

                if self.match_idx > 0:
                    self.match_idx -= 1
                else:
                    self.match_idx = len(self.matches) - 1

    def replace(self, widget):
        old = self.search_entry.get_text()
        new = self.replace_entry.get_text()
        if old and new:
            self.parent_window.replace(old, new)

    def clear(self):
        self.search_entry.set_text("")
        self.replace_entry.set_text("")
