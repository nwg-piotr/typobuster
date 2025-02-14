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

        # Key accelerator group
        accel_group = Gtk.AccelGroup()
        parent_window.add_accel_group(accel_group)

        # File menu
        file_menu = Gtk.Menu()
        file_menu.connect("show", self.update_menu_items_sensitivity)
        file_menu_item = Gtk.MenuItem(label=parent_window.voc["file"])
        file_menu_item.set_submenu(file_menu)

        # New menu item
        self.new_menu_item = Gtk.MenuItem(label=parent_window.voc["new"])
        file_menu.append(self.new_menu_item)
        key, mod = Gtk.accelerator_parse("<Control>N")
        self.new_menu_item.add_accelerator("activate", accel_group, key, mod, Gtk.AccelFlags.VISIBLE)
        accel_group.connect(key, mod, Gtk.AccelFlags.VISIBLE, parent_window.new_file)
        self.new_menu_item.connect("activate", parent_window.new_file)

        # Open menu item
        open_menu_item = Gtk.MenuItem(label=parent_window.voc["open"])
        file_menu.append(open_menu_item)
        key, mod = Gtk.accelerator_parse("<Control>O")
        open_menu_item.add_accelerator("activate", accel_group, key, mod, Gtk.AccelFlags.VISIBLE)
        accel_group.connect(key, mod, Gtk.AccelFlags.VISIBLE, parent_window.open_file)
        open_menu_item.connect("activate", parent_window.open_file)

        # Open recent files menu item
        self.recent_menu_item = Gtk.MenuItem(label=parent_window.voc["recent-files"])
        file_menu.append(self.recent_menu_item)
        self.recent_menu_item.set_sensitive(os.path.isfile(os.path.join(config_dir(), "recent")))
        file_menu.connect("show", add_recent_menu, self.recent_menu_item, self.parent_window)

        # Save menu item
        save_menu_item = Gtk.MenuItem(label=parent_window.voc["save"])
        key, mod = Gtk.accelerator_parse("<Control>S")
        save_menu_item.add_accelerator("activate", accel_group, key, mod, Gtk.AccelFlags.VISIBLE)
        accel_group.connect(key, mod, Gtk.AccelFlags.VISIBLE, parent_window.save_file)
        file_menu.append(save_menu_item)
        save_menu_item.connect("activate", parent_window.save_file)

        # Save As menu item
        save_as_menu_item = Gtk.MenuItem(label=parent_window.voc["save-as"])
        key, mod = Gtk.accelerator_parse("<Shift><Control>S")
        save_as_menu_item.add_accelerator("activate", accel_group, key, mod, Gtk.AccelFlags.VISIBLE)
        accel_group.connect(key, mod, Gtk.AccelFlags.VISIBLE, parent_window.save_file_as)
        file_menu.append(save_as_menu_item)
        save_as_menu_item.connect("activate", parent_window.save_file_as)

        sep = Gtk.SeparatorMenuItem()
        file_menu.append(sep)

        # Print menu item
        print_menu_item = Gtk.MenuItem(label=parent_window.voc["print"])
        key, mod = Gtk.accelerator_parse("<Control>P")
        print_menu_item.add_accelerator("activate", accel_group, key, mod, Gtk.AccelFlags.VISIBLE)
        accel_group.connect(key, mod, Gtk.AccelFlags.VISIBLE, parent_window.on_print_btn)
        file_menu.append(print_menu_item)
        print_menu_item.connect("activate", parent_window.on_print_btn)

        sep = Gtk.SeparatorMenuItem()
        file_menu.append(sep)

        # Quit menu item
        quit_menu_item = Gtk.MenuItem(label=parent_window.voc["quit"])
        key, mod = Gtk.accelerator_parse("<Control>Q")
        quit_menu_item.add_accelerator("activate", accel_group, key, mod, Gtk.AccelFlags.VISIBLE)
        accel_group.connect(key, mod, Gtk.AccelFlags.VISIBLE, parent_window.quit)
        file_menu.append(quit_menu_item)
        quit_menu_item.connect("activate", parent_window.quit)

        # Edit menu
        edit_menu = Gtk.Menu()
        edit_menu.connect("show", self.update_menu_items_sensitivity)
        edit_menu_item = Gtk.MenuItem(label=parent_window.voc["edit"])
        edit_menu_item.set_submenu(edit_menu)

        # Undo menu item
        self.undo_menu_item = Gtk.MenuItem(label=parent_window.voc["undo"])
        key, mod = Gtk.accelerator_parse("<Control>Z")
        self.undo_menu_item.add_accelerator("activate", accel_group, key, mod, Gtk.AccelFlags.VISIBLE)
        edit_menu.append(self.undo_menu_item)
        self.undo_menu_item.connect("activate", parent_window.undo)

        # Redo menu item
        self.redo_menu_item = Gtk.MenuItem(label=parent_window.voc["redo"])
        key, mod = Gtk.accelerator_parse("<Control>Y")
        self.redo_menu_item.add_accelerator("activate", accel_group, key, mod, Gtk.AccelFlags.VISIBLE)
        edit_menu.append(self.redo_menu_item)
        self.redo_menu_item.connect("activate", parent_window.redo)

        # Cut menu item
        cut_menu_item = Gtk.MenuItem(label=parent_window.voc["cut"])
        key, mod = Gtk.accelerator_parse("<Control>X")
        cut_menu_item.add_accelerator("activate", accel_group, key, mod, Gtk.AccelFlags.VISIBLE)
        edit_menu.append(cut_menu_item)
        cut_menu_item.connect("activate", parent_window.cut_text)

        # Copy menu item
        copy_menu_item = Gtk.MenuItem(label=parent_window.voc["copy"])
        key, mod = Gtk.accelerator_parse("<Control>C")
        copy_menu_item.add_accelerator("activate", accel_group, key, mod, Gtk.AccelFlags.VISIBLE)
        edit_menu.append(copy_menu_item)
        copy_menu_item.connect("activate", parent_window.copy_text)

        # Paste menu item
        paste_menu_item = Gtk.MenuItem(label=parent_window.voc["paste"])
        key, mod = Gtk.accelerator_parse("<Control>V")
        paste_menu_item.add_accelerator("activate", accel_group, key, mod, Gtk.AccelFlags.VISIBLE)
        edit_menu.append(paste_menu_item)
        paste_menu_item.connect("activate", parent_window.paste_text)

        # Delete menu item
        delete_menu_item = Gtk.MenuItem(label=parent_window.voc["delete"])
        edit_menu.append(delete_menu_item)
        delete_menu_item.connect("activate", parent_window.delete_text)

        # Transform menu item
        transform_menu_item = Gtk.MenuItem(label=parent_window.voc["transform"])
        edit_menu.append(transform_menu_item)

        # As in sentence menu item
        transform_as_in_sentence_menu_item = Gtk.MenuItem(label=parent_window.voc["as-in-sentence"])
        transform_menu_item.set_submenu(Gtk.Menu())
        transform_menu_item.get_submenu().append(transform_as_in_sentence_menu_item)
        transform_as_in_sentence_menu_item.connect("activate", parent_window.transform_text, "sentence")

        # As In Title menu item
        transform_as_in_title_menu_item = Gtk.MenuItem(label=parent_window.voc["as-in-title"])
        transform_menu_item.get_submenu().append(transform_as_in_title_menu_item)
        transform_as_in_title_menu_item.connect("activate", parent_window.transform_text, "title")

        # Transform to Uppercase menu item
        transform_uppercase_menu_item = Gtk.MenuItem(label=parent_window.voc["uppercase"])
        transform_menu_item.get_submenu().append(transform_uppercase_menu_item)
        transform_uppercase_menu_item.connect("activate", parent_window.transform_text, "uppercase")

        # Transform to Lowercase menu item
        transform_lowercase_menu_item = Gtk.MenuItem(label=parent_window.voc["lowercase"])
        transform_menu_item.get_submenu().append(transform_lowercase_menu_item)
        transform_lowercase_menu_item.connect("activate", parent_window.transform_text, "lowercase")

        # Transform to CamelCase menu item
        transform_camelcase_menu_item = Gtk.MenuItem(label=parent_window.voc["camel-case"])
        transform_menu_item.get_submenu().append(transform_camelcase_menu_item)
        transform_camelcase_menu_item.connect("activate", parent_window.transform_text, "camelcase")

        # Transform to Snake Case menu item
        transform_snakecase_menu_item = Gtk.MenuItem(label=parent_window.voc["snake-case"])
        transform_menu_item.get_submenu().append(transform_snakecase_menu_item)
        transform_snakecase_menu_item.connect("activate", parent_window.transform_text, "snakecase")

        # Transform to Kebab Case menu item
        transform_kebabcase_menu_item = Gtk.MenuItem(label=parent_window.voc["kebab-case"])
        transform_menu_item.get_submenu().append(transform_kebabcase_menu_item)
        transform_kebabcase_menu_item.connect("activate", parent_window.transform_text, "kebabcase")

        # Transform to unordered list menu item
        transform_unordered_list_menu_item = Gtk.MenuItem(label=parent_window.voc["unordered-list"])
        transform_menu_item.get_submenu().append(transform_unordered_list_menu_item)
        transform_unordered_list_menu_item.connect("activate", parent_window.transform_text, "unordered")

        # Transform to ordered list menu item
        transform_ordered_list_menu_item = Gtk.MenuItem(label=parent_window.voc["ordered-list"])
        transform_menu_item.get_submenu().append(transform_ordered_list_menu_item)
        transform_ordered_list_menu_item.connect("activate", parent_window.transform_text, "ordered")

        # First word to the end menu item
        first_to_end_item = Gtk.MenuItem(label=parent_window.voc["move-to-end"])
        transform_menu_item.get_submenu().append(first_to_end_item)
        first_to_end_item.connect("activate", parent_window.transform_text, "first-to-end")

        # Last word to the beginning menu item
        last_to_beginning_item = Gtk.MenuItem(label=parent_window.voc["last-to-beginning"])
        transform_menu_item.get_submenu().append(last_to_beginning_item)
        last_to_beginning_item.connect("activate", parent_window.transform_text, "last-to-beginning")

        separator = Gtk.SeparatorMenuItem()
        edit_menu.append(separator)

        # Preferences menu item
        preferences_menu_item = Gtk.MenuItem(label=parent_window.voc["preferences"])
        edit_menu.append(preferences_menu_item)
        preferences_menu_item.connect("activate", parent_window.show_preferences)

        # View menu
        view_menu = Gtk.Menu()
        # view_menu.set_reserve_toggle_size(False)
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

        self.tab_width_label = Gtk.Label(label=parent.voc["tab-width"], halign=Gtk.Align.START)
        self.grid.attach(self.tab_width_label, 0, 3, 1, 1)

        tab_width_sb = Gtk.SpinButton.new_with_range(1, 32.0, 1)
        tab_width_sb.set_value(parent.settings["tab-width"])
        tab_width_sb.connect("value-changed", parent.on_tab_with_selected)
        self.grid.attach(tab_width_sb, 1, 3, 1, 1)

        self.tab_mode_label = Gtk.Label(label=parent.voc["tab-mode"], halign=Gtk.Align.START)
        self.grid.attach(self.tab_mode_label, 0, 4, 1, 1)

        self.tab_mode_combo = Gtk.ComboBoxText()
        self.tab_mode_combo.append("tabs", parent.voc["insert-tabs"])
        self.tab_mode_combo.append("spaces", parent.voc["insert-spaces"])
        self.tab_mode_combo.set_active_id(parent.settings["tab-mode"])
        self.tab_mode_combo.connect("changed", parent.on_tab_mode_changed)
        self.grid.attach(self.tab_mode_combo, 1, 4, 1, 1)

        self.auto_indent_cb = Gtk.CheckButton(label=parent.voc["auto-indent"])
        self.auto_indent_cb.set_active(parent.settings["auto-indent"])
        self.auto_indent_cb.connect("toggled", parent.on_auto_indent_changed)
        self.grid.attach(self.auto_indent_cb, 0, 5, 1, 1)

        self.spell_check_cb = Gtk.CheckButton(label=parent.voc["spell-check"])
        self.spell_check_cb.set_sensitive(parent.gspell_available)
        if not parent.gspell_available:
            self.spell_check_cb.set_tooltip_text(parent.voc["gspell-missing"])
        self.spell_check_cb.set_active(parent.settings["gspell-enable"])
        self.spell_check_cb.connect("toggled", parent.on_spell_check_switched)
        self.grid.attach(self.spell_check_cb, 0, 6, 1, 1)

        self.stats_cb = Gtk.CheckButton(label=parent.voc["show-stats"])
        self.stats_cb.set_active(parent.settings["show-stats"])
        self.stats_cb.connect("toggled", parent.on_stats_cb_toggled)
        self.grid.attach(self.stats_cb, 0, 7, 1, 1)

        # OK Button
        hbox = Gtk.Box(Gtk.Orientation.HORIZONTAL, 0)
        self.grid.attach(hbox, 0, 7, 3, 1)
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
        self.replace_entry.set_icon_from_icon_name(Gtk.EntryIconPosition.PRIMARY, "edit-find-replace-symbolic")
        self.replace_entry.set_tooltip_text(parent_window.voc["replace-with"])
        self.pack_start(self.replace_entry, False, False, 0)

        btn = Gtk.Button.new_from_icon_name("emblem-ok-symbolic", Gtk.IconSize.MENU)
        self.pack_start(btn, False, False, 0)
        btn.connect("clicked", self.replace)

        self.pos_lbl = Gtk.Label.new(f'{parent_window.voc["row"]}: 1 {parent_window.voc["column"]}: 0')
        self.pack_end(self.pos_lbl, False, False, 6)

        self.stat_lbl = Gtk.Label.new("0")
        self.pack_end(self.stat_lbl, False, False, 0)

        if parent_window.settings["syntax"] == "none":
            s_lbl = parent_window.voc["plain-text"]
        else:
            s_lbl = parent_window.syntax_dict[parent_window.settings["syntax"]]
        self.syntax_lbl = Gtk.Label.new(s_lbl)
        self.pack_end(self.syntax_lbl, False, False, 6)

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
