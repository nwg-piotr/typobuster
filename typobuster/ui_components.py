import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from typobuster.tools import *


class MenuBar(Gtk.MenuBar):
    def __init__(self, parent_window):
        super().__init__()
        self.settings = parent_window.settings
        self.set_take_focus(False)

        # Create the File menu
        file_menu = Gtk.Menu()
        file_menu_item = Gtk.MenuItem(label="File")
        file_menu_item.set_submenu(file_menu)

        # Create the New menu item
        new_menu_item = Gtk.MenuItem(label="New")
        file_menu.append(new_menu_item)

        # Create the Open menu item
        open_menu_item = Gtk.MenuItem(label="Open")
        file_menu.append(open_menu_item)

        # Create the Save menu item
        save_menu_item = Gtk.MenuItem(label="Save")
        file_menu.append(save_menu_item)

        # Create the Save As menu item
        save_as_menu_item = Gtk.MenuItem(label="Save As")
        file_menu.append(save_as_menu_item)

        # Create the Quit menu item
        quit_menu_item = Gtk.MenuItem(label="Quit")
        file_menu.append(quit_menu_item)
        quit_menu_item.connect("activate", parent_window.quit)

        # Create the Edit menu
        edit_menu = Gtk.Menu()
        edit_menu_item = Gtk.MenuItem(label="Edit")
        edit_menu_item.set_submenu(edit_menu)

        # Create the Cut menu item
        cut_menu_item = Gtk.MenuItem(label="Cut")
        edit_menu.append(cut_menu_item)

        # Create the Copy menu item
        copy_menu_item = Gtk.MenuItem(label="Copy")
        edit_menu.append(copy_menu_item)

        # Create the Paste menu item
        paste_menu_item = Gtk.MenuItem(label="Paste")
        edit_menu.append(paste_menu_item)

        # Create the Delete menu item
        delete_menu_item = Gtk.MenuItem(label="Delete")
        edit_menu.append(delete_menu_item)

        # Create the View menu
        view_menu = Gtk.Menu()
        view_menu.set_reserve_toggle_size(False)
        view_menu_item = Gtk.MenuItem(label="View")
        view_menu_item.set_submenu(view_menu)

        # Create the Line numbers menu item
        icon_name = "checkbox-checked-symbolic" if self.settings["view-line-numbers"] else "checkbox-symbolic"
        self.line_numbers_menu_item = CustomMenuItem(self.settings, icon_name, "Line Numbers")

        view_menu.append(self.line_numbers_menu_item)
        self.line_numbers_menu_item.connect("activate", parent_window.toggle_line_numbers)

        # Create the Tools menu
        tools_menu = Gtk.Menu()
        tools_menu_item = Gtk.MenuItem(label="Tools")
        tools_menu_item.set_submenu(tools_menu)

        # Create the Sanitize menu item
        sanitize_menu_item = Gtk.MenuItem(label="Sanitize")
        tools_menu.append(sanitize_menu_item)
        sanitize_menu_item.connect("activate", parent_window.sanitize_text)
        sanitize_menu_item.set_can_focus(False)

        # Create the Help menu
        help_menu = Gtk.Menu()
        help_menu_item = Gtk.MenuItem(label="Help")
        help_menu_item.set_submenu(help_menu)

        # Create the About menu item
        about_menu_item = Gtk.MenuItem(label="About")
        help_menu.append(about_menu_item)

        # Append the menu items to the menu bar
        self.append(file_menu_item)
        self.append(edit_menu_item)
        self.append(view_menu_item)
        self.append(tools_menu_item)
        self.append(help_menu_item)


class CustomMenuItem(Gtk.MenuItem):
    def __init__(self, settings, icon_name, label):
        super().__init__()
        self.settings = settings
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.add(box)
        self.image = Gtk.Image.new_from_icon_name(icon_name, Gtk.IconSize.MENU)
        box.pack_start(self.image, False, False, 6)
        label = Gtk.Label(label)
        box.pack_start(label, False, False, 0)

    def set_image(self, config_key):
        icon_name = "checkbox-checked-symbolic" if self.settings[config_key] else "checkbox-symbolic"
        self.image.set_from_icon_name(icon_name, Gtk.IconSize.MENU)


class SanitizationDialog(Gtk.Window):
    def __init__(self, parent_window, buffer):

        super().__init__(title="Sanitize Text")
        self.set_transient_for(parent_window)
        self.set_modal(True)
        self.parent_window = parent_window
        self.settings = parent_window.settings

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

        button = Gtk.Button(label="Sanitize")
        button.connect("clicked", self.sanitize_text, buffer)
        vbox.pack_start(button, False, False, 0)

        self.show_all()

    def switch_settings_key(self, chekbox, key):
        if key in self.settings:
            self.settings[key] = chekbox.get_active()
            save_settings(self.settings)
        else:
            print(f"Key '{key}' not found in settings")

    def sanitize_text(self, widget, buffer):
        text, start_idx, end_idx = text_to_modify(buffer)

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


def text_to_modify(buffer):
    start = buffer.get_start_iter()
    end = buffer.get_end_iter()

    if buffer.get_has_selection():
        start_iter, end_iter = buffer.get_selection_bounds()
    else:
        start_iter = start
        end_iter = end

    return buffer.get_text(start, end, True), start_iter.get_offset(), end_iter.get_offset()
