import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk

from typobuster.tools import *
from typobuster.__about__ import __version__


class MenuBar(Gtk.MenuBar):
    def __init__(self, parent_window):
        super().__init__()
        self.settings = parent_window.settings
        self.set_take_focus(False)

        self.parent_window = parent_window

        # Create the File menu
        file_menu = Gtk.Menu()
        file_menu.connect("show", self.update_menu_items_sensitivity)
        file_menu_item = Gtk.MenuItem(label=parent_window.voc["file"])
        file_menu_item.set_submenu(file_menu)

        # Create the New menu item
        self.new_menu_item = Gtk.MenuItem(label=parent_window.voc["new"])
        file_menu.append(self.new_menu_item)
        self.new_menu_item.connect("activate", parent_window.new_file)

        # Create the Open menu item
        open_menu_item = Gtk.MenuItem(label=parent_window.voc["open"])
        file_menu.append(open_menu_item)
        open_menu_item.connect("activate", parent_window.open_file)

        # Create the Open recent files menu item
        self.recent_menu_item = Gtk.MenuItem(label=parent_window.voc["recent-files"])
        file_menu.append(self.recent_menu_item)
        self.recent_menu_item.set_sensitive(os.path.isfile(os.path.join(config_dir(), "recent")))
        file_menu.connect("show", add_recent_menu, self.recent_menu_item, self.parent_window)

        # Create the Save menu item
        save_menu_item = Gtk.MenuItem(label=parent_window.voc["save"])
        file_menu.append(save_menu_item)
        save_menu_item.connect("activate", parent_window.save_file)

        # Create the Save As menu item
        save_as_menu_item = Gtk.MenuItem(label=parent_window.voc["save-as"])
        file_menu.append(save_as_menu_item)
        save_as_menu_item.connect("activate", parent_window.save_file_as)

        # Create the Quit menu item
        quit_menu_item = Gtk.MenuItem(label=parent_window.voc["quit"])
        file_menu.append(quit_menu_item)
        quit_menu_item.connect("activate", parent_window.quit)

        # Create the Edit menu
        edit_menu = Gtk.Menu()
        edit_menu.connect("show", self.update_menu_items_sensitivity)
        edit_menu_item = Gtk.MenuItem(label=parent_window.voc["edit"])
        edit_menu_item.set_submenu(edit_menu)

        # Create key accelerator
        accel_group = Gtk.AccelGroup()
        parent_window.add_accel_group(accel_group)

        # Create the Undo menu item
        self.undo_menu_item = Gtk.MenuItem(label=parent_window.voc["undo"])
        key, mod = Gtk.accelerator_parse("<Control>Z")
        self.undo_menu_item.add_accelerator("activate", accel_group, key, mod, Gtk.AccelFlags.VISIBLE)
        edit_menu.append(self.undo_menu_item)
        self.undo_menu_item.connect("activate", parent_window.undo)

        # Create the Redo menu item
        self.redo_menu_item = Gtk.MenuItem(label=parent_window.voc["redo"])
        key, mod = Gtk.accelerator_parse("<Control>Y")
        self.redo_menu_item.add_accelerator("activate", accel_group, key, mod, Gtk.AccelFlags.VISIBLE)
        edit_menu.append(self.redo_menu_item)
        self.redo_menu_item.connect("activate", parent_window.redo)

        # Create the Cut menu item
        cut_menu_item = Gtk.MenuItem(label=parent_window.voc["cut"])
        key, mod = Gtk.accelerator_parse("<Control>X")
        cut_menu_item.add_accelerator("activate", accel_group, key, mod, Gtk.AccelFlags.VISIBLE)
        edit_menu.append(cut_menu_item)
        cut_menu_item.connect("activate", parent_window.cut_text)

        # Create the Copy menu item
        copy_menu_item = Gtk.MenuItem(label=parent_window.voc["copy"])
        key, mod = Gtk.accelerator_parse("<Control>C")
        copy_menu_item.add_accelerator("activate", accel_group, key, mod, Gtk.AccelFlags.VISIBLE)
        edit_menu.append(copy_menu_item)
        copy_menu_item.connect("activate", parent_window.copy_text)

        # Create the Paste menu item
        paste_menu_item = Gtk.MenuItem(label=parent_window.voc["paste"])
        key, mod = Gtk.accelerator_parse("<Control>V")
        paste_menu_item.add_accelerator("activate", accel_group, key, mod, Gtk.AccelFlags.VISIBLE)
        edit_menu.append(paste_menu_item)
        paste_menu_item.connect("activate", parent_window.paste_text)

        # Create the Delete menu item
        delete_menu_item = Gtk.MenuItem(label=parent_window.voc["delete"])
        key, mod = Gtk.accelerator_parse("Delete")
        delete_menu_item.add_accelerator("activate", accel_group, key, mod, Gtk.AccelFlags.VISIBLE)
        edit_menu.append(delete_menu_item)
        delete_menu_item.connect("activate", parent_window.delete_text)

        # Create the Transform menu item
        transform_menu_item = Gtk.MenuItem(label=parent_window.voc["transform"])
        edit_menu.append(transform_menu_item)

        # Create the As in sentence menu item
        transform_as_in_sentence_menu_item = Gtk.MenuItem(label=parent_window.voc["as-in-sentence"])
        transform_menu_item.set_submenu(Gtk.Menu())

        transform_menu_item.get_submenu().append(transform_as_in_sentence_menu_item)
        transform_as_in_sentence_menu_item.connect("activate", parent_window.transform_text, "sentence")

        # Create the Transform to Uppercase menu item
        transform_uppercase_menu_item = Gtk.MenuItem(label=parent_window.voc["uppercase"])
        transform_menu_item.get_submenu().append(transform_uppercase_menu_item)
        transform_uppercase_menu_item.connect("activate", parent_window.transform_text, "uppercase")

        # Create the Transform to Lowercase menu item
        transform_lowercase_menu_item = Gtk.MenuItem(label=parent_window.voc["lowercase"])
        transform_menu_item.get_submenu().append(transform_lowercase_menu_item)
        transform_lowercase_menu_item.connect("activate", parent_window.transform_text, "lowercase")

        # Create the Transform to CamelCase menu item
        transform_camelcase_menu_item = Gtk.MenuItem(label=parent_window.voc["camelcase"])
        transform_menu_item.get_submenu().append(transform_camelcase_menu_item)
        transform_camelcase_menu_item.connect("activate", parent_window.transform_text, "camelcase")

        # Create the Transform to Snake Case menu item
        transform_snakecase_menu_item = Gtk.MenuItem(label=parent_window.voc["snakecase"])
        transform_menu_item.get_submenu().append(transform_snakecase_menu_item)
        transform_snakecase_menu_item.connect("activate", parent_window.transform_text, "snakecase")

        # Create the Transform to Kebab Case menu item
        transform_kebabcase_menu_item = Gtk.MenuItem(label=parent_window.voc["kebabcase"])
        transform_menu_item.get_submenu().append(transform_kebabcase_menu_item)
        transform_kebabcase_menu_item.connect("activate", parent_window.transform_text, "kebabcase")

        # Create the Transform to unordered list menu item
        transform_unordered_list_menu_item = Gtk.MenuItem(label=parent_window.voc["unordered-list"])
        transform_menu_item.get_submenu().append(transform_unordered_list_menu_item)
        transform_unordered_list_menu_item.connect("activate", parent_window.transform_text, "unordered")

        # Create the Transform to ordered list menu item
        transform_ordered_list_menu_item = Gtk.MenuItem(label=parent_window.voc["ordered-list"])
        transform_menu_item.get_submenu().append(transform_ordered_list_menu_item)
        transform_ordered_list_menu_item.connect("activate", parent_window.transform_text, "ordered")

        separator = Gtk.SeparatorMenuItem()
        edit_menu.append(separator)

        # Create the Preferences menu item
        preferences_menu_item = Gtk.MenuItem(label=parent_window.voc["preferences"])
        edit_menu.append(preferences_menu_item)
        preferences_menu_item.connect("activate", parent_window.show_preferences)

        # Create the View menu
        view_menu = Gtk.Menu()
        # view_menu.set_reserve_toggle_size(False)
        view_menu_item = Gtk.MenuItem(label=parent_window.voc["view"])
        view_menu_item.set_submenu(view_menu)

        # Create the Line numbers menu item
        self.line_numbers_menu_item = Gtk.CheckMenuItem(parent_window.voc["line-numbers"])
        view_menu.append(self.line_numbers_menu_item)
        self.line_numbers_menu_item.set_active(self.settings["view-line-numbers"])
        self.line_numbers_menu_item.connect("toggled", parent_window.toggle_line_numbers)

        # Syntax menu item
        syntax_menu_item = Gtk.MenuItem(label=parent_window.voc["syntax-highlight"])
        view_menu.append(syntax_menu_item)
        view_menu.connect("show", add_syntax_menu, syntax_menu_item, self.parent_window)

        # Create the Tools menu
        tools_menu = Gtk.Menu()
        tools_menu.connect("show", self.update_menu_items_sensitivity)
        tools_menu_item = Gtk.MenuItem(label=parent_window.voc["tools"])
        tools_menu_item.set_submenu(tools_menu)

        # Create the Sanitize menu item
        self.sanitize_menu_item = Gtk.MenuItem(label=parent_window.voc["web-cleanup"])
        tools_menu.append(self.sanitize_menu_item)
        self.sanitize_menu_item.connect("show", self.update_menu_items_sensitivity)
        self.sanitize_menu_item.connect("activate", parent_window.sanitize_text)
        self.sanitize_menu_item.set_can_focus(False)

        # Create the Help menu
        help_menu = Gtk.Menu()
        help_menu_item = Gtk.MenuItem(label=parent_window.voc["help"])
        help_menu_item.set_submenu(help_menu)

        # Create the About menu item
        about_menu_item = Gtk.MenuItem(label=parent_window.voc["about"])
        help_menu.append(about_menu_item)
        about_menu_item.connect("activate", parent_window.show_about)

        # Append the menu items to the menu bar
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

        self.sanitize_hyphens = Gtk.CheckButton(label="Hyphens")
        self.sanitize_hyphens.set_active(self.settings["sanitize-hyphens"])
        self.sanitize_hyphens.connect("toggled", self.switch_settings_key, "sanitize-hyphens")
        vbox.pack_start(self.sanitize_hyphens, False, False, 0)

        self.sanitize_quotes = Gtk.CheckButton(label="Quotes")
        self.sanitize_quotes.set_active(self.settings["sanitize-quotes"])
        self.sanitize_quotes.connect("toggled", self.switch_settings_key, "sanitize-quotes")
        vbox.pack_start(self.sanitize_quotes, False, False, 0)

        self.sanitize_punctuation_marks = Gtk.CheckButton(label="Punctuation marks")
        self.sanitize_punctuation_marks.set_active(self.settings["sanitize-punctuation-marks"])
        self.sanitize_punctuation_marks.connect("toggled", self.switch_settings_key, "sanitize-punctuation-marks")
        vbox.pack_start(self.sanitize_punctuation_marks, False, False, 0)

        self.sanitize_spaces = Gtk.CheckButton(label="Spaces")
        self.sanitize_spaces.set_active(self.settings["sanitize-spaces"])
        self.sanitize_spaces.connect("toggled", self.switch_settings_key, "sanitize-spaces")
        vbox.pack_start(self.sanitize_spaces, False, False, 0)

        self.sanitize_eol = Gtk.CheckButton(label="End-of-line characters")
        self.sanitize_eol.set_active(self.settings["sanitize-eol"])
        self.sanitize_eol.connect("toggled", self.switch_settings_key, "sanitize-eol")
        vbox.pack_start(self.sanitize_eol, False, False, 0)

        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        hbox.set_property("margin-top", 12)
        vbox.pack_start(hbox, False, False, 0)

        button = Gtk.Button(label="Sanitize")
        hbox.pack_end(button, False, False, 0)
        button.connect("clicked", self.sanitize_text, buffer)

        button = Gtk.Button(label="Close")
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

        if self.settings["sanitize-spaces"]:
            text = sanitize_spaces(text, start_idx, end_idx)

        if self.settings["sanitize-eol"]:
            text = sanitize_eol(text, start_idx, end_idx)

        self.parent_window.update_text(text)
        self.destroy()


class AboutWindow(Gtk.AboutDialog):
    def __init__(self, parent_window):
        super().__init__()
        self.set_transient_for(parent_window)
        self.set_program_name("Typobuster")
        self.set_comments(parent_window.voc["description"])
        self.set_website("https://github.com/nwg-piotr/typobuster")
        self.set_website_label("GitHub repository")
        self.set_authors(["Piotr Miller"])
        self.set_license_type(Gtk.License.GPL_3_0)
        self.set_version(f"Version: {__version__}")

        # Load icon by name from the system theme
        icon_theme = Gtk.IconTheme.get_default()
        icon_name = "typobuster"  # Change to your preferred icon name

        # Load and scale the icon
        pixbuf = icon_theme.load_icon(icon_name, 128, 0)  # 128x128 size
        self.set_logo(pixbuf)

        self.set_keep_above(True)
        self.connect("response", lambda x, y: self.destroy())
        self.show_all()


class PreferencesDialog(Gtk.Dialog):
    def __init__(self, parent):
        super().__init__(title="Preferences", transient_for=parent, modal=True)

        self.grid = Gtk.Grid(margin_top=10, margin_bottom=10, margin_start=10, margin_end=10, column_spacing=10, row_spacing=10)
        self.get_content_area().pack_start(self.grid, False, False, 0)

        # Theme Selector
        self.theme_label = Gtk.Label(label="Theme:", halign=Gtk.Align.START)
        self.grid.attach(self.theme_label, 0, 0, 1, 1)

        self.theme_combo = Gtk.ComboBoxText()
        for name in get_theme_names():
            self.theme_combo.append(name, name)

        if parent.settings["gtk-theme-name"]:
            self.theme_combo.set_active_id(parent.settings["gtk-theme-name"])
        else:
            self.theme_combo.set_active_id(parent.gtk_settings.get_property("gtk-theme-name"))

        self.theme_combo.set_active(0)  # Default to Light
        self.theme_combo.connect("changed", self.on_theme_changed)
        self.grid.attach(self.theme_combo, 1, 0, 1, 1)

        # Font Selector
        self.font_size_label = Gtk.Label(label=parent.voc["font"], halign=Gtk.Align.START)
        self.grid.attach(self.font_size_label, 0, 1, 1, 1)

        self.font_chooser_btn = Gtk.FontButton()
        self.font_chooser_btn.set_use_font(True)
        self.font_chooser_btn.set_font_name(parent.settings["gtk-font-name"])
        self.font_chooser_btn.connect("font-set", parent.on_font_selected)
        self.grid.attach(self.font_chooser_btn, 1, 1, 1, 1)

        # OK Button
        self.ok_button = Gtk.Button(label="OK")
        self.ok_button.connect("clicked", lambda x: self.close())
        self.grid.attach(self.ok_button, 0, 2, 2, 1)

        self.show_all()

    def on_theme_changed(self, combo):
        theme = combo.get_active_id()
        print(f"Selected Theme: {theme}")


def selected_text(buffer):
    start = buffer.get_start_iter()
    end = buffer.get_end_iter()

    if buffer.get_has_selection():
        start_iter, end_iter = buffer.get_selection_bounds()
    else:
        start_iter = start
        end_iter = end

    return buffer.get_text(start, end, True), start_iter.get_offset(), end_iter.get_offset()


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
        self.search_entry.connect("search-changed", self.on_search_changed, parent_window.buffer)

        btn = Gtk.Button.new_from_icon_name("go-up-symbolic", Gtk.IconSize.MENU)
        self.pack_start(btn, False, False, 0)
        btn.connect("clicked", self.highlight_match, "up")

        btn = Gtk.Button.new_from_icon_name("go-down-symbolic", Gtk.IconSize.MENU)
        self.pack_start(btn, False, False, 0)
        btn.connect("clicked", self.highlight_match, "down")

        lbl = Gtk.Label.new(parent_window.voc["replace-all-with"])
        self.pack_start(lbl, False, False, 6)

        self.replace_entry = Gtk.Entry()
        self.pack_start(self.replace_entry, False, False, 0)

        btn = Gtk.Button.new_from_icon_name("emblem-ok-symbolic", Gtk.IconSize.MENU)
        self.pack_start(btn, False, False, 0)
        btn.connect("clicked", self.replace)

        if parent_window.settings["syntax"] == "none":
            s_lbl = parent_window.voc["plain-text"]
        else:
            s_lbl = parent_window.syntax_dict[parent_window.settings["syntax"]]
        self.syntax_lbl = Gtk.Label.new(s_lbl)
        self.pack_end(self.syntax_lbl, False, False, 6)

        self.show_all()

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
