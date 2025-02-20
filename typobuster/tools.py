import json
import os
import re
import sys
import unicodedata


def config_dir():
    xdg_config_home = os.getenv('XDG_CONFIG_HOME')
    config_home = xdg_config_home if xdg_config_home else os.path.join(os.getenv("HOME"), ".config")

    return os.path.join(config_home, "typobuster")


def get_theme_names():
    theme_dirs = []
    for d in get_data_dirs():
        p = os.path.join(d, "themes")
        if os.path.isdir(p):
            theme_dirs.append(p)

    home = os.getenv("HOME")
    if home:
        p = os.path.join(home, ".themes")
        if os.path.isdir(p):
            theme_dirs.append(p)

    names = []
    exclusions = ["Default", "Emacs"]
    for d in theme_dirs:
        for item in os.listdir(d):
            if os.path.isdir(os.path.join(d, item)) and item not in exclusions:
                content = os.listdir(os.path.join(d, item))
                for name in content:
                    if name.startswith("gtk-"):
                        if item not in names:
                            names.append(item)
                            break
    names.sort()
    return names


def get_data_dirs():
    dirs = [get_data_home()]
    xdg_data_dirs = os.getenv("XDG_DATA_DIRS") if os.getenv("XDG_DATA_DIRS") else "/usr/local/share/:/usr/share/"
    for d in xdg_data_dirs.split(":"):
        dirs.append(d)
    confirmed = []
    for d in dirs:
        if os.path.isdir(d):
            confirmed.append(d)

    return confirmed


def get_data_home():
    d_home = os.getenv('XDG_DATA_HOME') if os.getenv('XDG_DATA_HOME') else os.path.join(
        os.getenv("HOME"), ".local/share")
    return d_home


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def load_json(path):
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except Exception as e:
        eprint("Error loading json: {}".format(e))
        return {}


def save_json(src_dict, path):
    try:
        with open(path, 'w') as f:
            json.dump(src_dict, f, indent=2)
        return "ok"
    except Exception as e:
        return e


def load_settings():
    # check if config dir exists, create if not
    if not os.path.isdir(config_dir()):
        os.makedirs(config_dir())
        print(f"Created {config_dir()}")

    config_path = os.path.join(config_dir(), "config")

    defaults = {
        "gtk-font-name": "",
        "gtk-theme-name": "",
        "sanitize-spaces": True,
        "sanitize-punctuation-marks": True,
        "sanitize-add-spaces-after-punctuation": True,
        "sanitize-hyphens": True,
        "sanitize-quotes": True,
        "sanitize-eol": True,
        "syntax": "none",
        "view-line-numbers": False,
        "highlight-current-row": False,
        "highlight-matching-brackets": False,
        "right-margin-position": 80,
        "right-margin-show": False,
        "wrap-lines": True,
        "tab-width": 4,
        "tab-mode": "spaces",
        "auto-indent": True,
        "whitespaces": False,
        "gspell-enable": False,
        "show-stats": False,
        "show-change": False
    }
    settings = load_json(config_path)

    # if config file empty or not found
    if not settings:
        result = save_json(defaults, config_path)
        if result == "ok":
            print(f"Saved default settings to {config_path}")
        else:
            eprint(f"Error saving default settings to {config_path}: {result}")

    # add missing keys
    changed = False
    for key in defaults:
        if key not in settings:
            settings[key] = defaults[key]
            changed = True

    if changed:
        result = save_json(settings, config_path)
        if result == "ok":
            print(f"Updated settings in {config_path}")
        else:
            eprint(f"Error updating settings in {config_path}: {result}")

    return settings


def save_settings(settings):
    config_path = os.path.join(config_dir(), "config")
    result = save_json(settings, config_path)
    if result == "ok":
        print(f"Saved settings to {config_path}")
    else:
        eprint(f"Error saving settings to {config_path}: {result}")


def load_syntax():
    syntax_path = os.path.join(config_dir(), "syntax")

    defaults = {
        'c': 'C',
        'cpp': 'C++',
        'css': 'CSS',
        'csv': 'CSV',
        'desktop': '.desktop',
        'diff': 'Diff',
        'go': 'Go',
        'html': 'HTML',
        'java': 'Java',
        'js': 'JavaScript',
        'json': 'JSON',
        'kotlin': 'Kotlin',
        'makefile': 'Makefile',
        'markdown': 'Markdown',
        'meson': 'Meson',
        'php': 'PHP',
        'python3': 'Python',
        'python': 'Python2',
        'r': 'R',
        'sh': 'sh',
        'sql': 'SQL',
        'vala': 'Vala',
        'xml': 'XML',
        'yaml': 'YAML'
    }
    syntax = load_json(syntax_path)

    # if syntax file empty or not found
    if not syntax:
        result = save_json(defaults, syntax_path)
        if result == "ok":
            print(f"Saved default syntax dictionary to {syntax_path}")
        else:
            eprint(f"Error saving default settings to {syntax_path}: {result}")

    # add missing keys
    changed = False
    for key in defaults:
        if key not in syntax:
            syntax[key] = defaults[key]
            changed = True

    if changed:
        result = save_json(syntax, syntax_path)
        if result != "ok":
            eprint(f"Error updating settings in {syntax_path}: {result}")

    return syntax


def load_text_file(path):
    try:
        with open(path, 'r') as file:
            data = file.read()
            return data
    except Exception as e:
        eprint(e)
        return ""


def save_text_file(text, path):
    try:
        with open(path, 'w') as file:
            file.write(text)
            return "ok"
    except Exception as e:
        eprint(e)
        return e


def selected_text(buffer):
    start = buffer.get_start_iter()
    end = buffer.get_end_iter()

    if buffer.get_has_selection():
        start_iter, end_iter = buffer.get_selection_bounds()
    else:
        start_iter = start
        end_iter = end

    return buffer.get_text(start, end, True), start_iter.get_offset(), end_iter.get_offset()


def replace_all(text, old, new):
    return re.sub(re.escape(old), new, text)


def sanitize_hyphens(text, start_idx, end_idx):
    selection = text[start_idx:end_idx]
    selection = selection.replace("–", "-")  # Replace en-dashes with hyphens
    selection = selection.replace(" -", " - ")  # Add spaces around hyphens
    selection = selection.replace("- ", " - ")  # Add spaces around hyphens
    return text[:start_idx] + selection + text[end_idx:]


def sanitize_quotes(text, start_idx, end_idx):
    selection = text[start_idx:end_idx]
    selection = selection.replace(',,', '"')  # Replace double comma with English-style quotes
    selection = re.sub(r"[„”]", '"', selection)  # Replace German-style quotes with English-style quotes
    return text[:start_idx] + selection + text[end_idx:]


def sanitize_punctuation_marks(text, start_idx, end_idx):
    selection = text[start_idx:end_idx]
    selection = re.sub(r'\s+([.,!?;:])', r'\1', selection)  # Remove spaces before punctuation marks
    selection = selection.replace('. ,', '.,')
    return text[:start_idx] + selection + text[end_idx:]


def add_spaces_after_punctuation_marks(text, start_idx, end_idx):
    selection = text[start_idx:end_idx]
    selection = re.sub(r'([.,!?;:])([A-Za-z])', r'\1 \2', selection)  # Add a space after punctuation marks
    return text[:start_idx] + selection + text[end_idx:]


def sanitize_spaces(text, start_idx, end_idx, convert_tabs, tab_width):
    selection = text[start_idx:end_idx]
    selection = re.sub(r" {2,}", " ", selection)  # Replace two or more spaces with a single space
    if convert_tabs:
        selection = re.sub(r'\t+', ' ' * tab_width, selection).strip()  # Replace tabs with a single space
    selection = selection.replace(" \n", "\n")  # Remove spaces before end-of-line characters
    selection = selection.replace("\n ", "\n")  # Remove spaces right after end-of-line characters
    return text[:start_idx] + selection + text[end_idx:]


def sanitize_eol(text, start_idx, end_idx):
    selection = text[start_idx:end_idx]
    selection = re.sub(r"\n{2,}", "\n", selection)  # Replace two or more end-of-line characters with a single one
    selection = selection.replace("\n", "\n\n")  # Double all end-of-line characters
    return text[:start_idx] + selection + text[end_idx:]


def get_shell_data_dir():
    data_dir = ""
    home = os.getenv("HOME")
    xdg_data_home = os.getenv("XDG_DATA_HOME")

    if xdg_data_home:
        data_dir = os.path.join(xdg_data_home, "nwg-shell/")
    else:
        if home:
            data_dir = os.path.join(home, ".local/share/nwg-shell/")

    return data_dir


def load_shell_data():
    shell_data_file = os.path.join(get_shell_data_dir(), "data")
    shell_data = load_json(shell_data_file) if os.path.isfile(shell_data_file) else {}

    defaults = {
        "interface-locale": ""
    }

    for key in defaults:
        if key not in shell_data:
            shell_data[key] = defaults[key]

    return shell_data


def to_snake_case(text):
    lines = text.splitlines()
    result = []
    for line in lines:
        line = line.lower().replace(" ", "_")
        result.append(line)
    return "\n".join(result)


def to_kebab_case(text):
    lines = text.splitlines()
    result = []
    for line in lines:
        line = line.lower().replace(" ", "-")
        result.append(line)
    return "\n".join(result)


def to_camel_case(text):
    lines = text.splitlines()
    result = []
    for line in lines:
        line = ''.join(x for x in line.title() if not x.isspace())
        line = line[0].lower() + line[1:]
        result.append(line)
    return "\n".join(result)


def to_upper(text):
    return text.upper()


def to_lower_case(text):
    return text.lower()


def as_in_sentence(text):
    lines = text.splitlines()
    result = []
    for line in lines:
        line = line.lower()
        line = line[0].upper() + line[1:]
        result.append(line)
    return "\n".join(result)


def as_in_title(text):
    return ' '.join(word.capitalize() for word in text.split())


def unordered_list(text):
    text = remove_empty_lines(text)
    lines = text.splitlines()
    output = []
    for line in lines:
        line = line.strip().rstrip()
        if not line.startswith('- '):
            line = "- " + line
        output.append(line)

    return "\n".join(output)


def ordered_list(text):
    text = remove_empty_lines(text)
    lines = text.splitlines()
    output = []
    for i in range(len(lines)):
        line = lines[i]
        line = line.strip().rstrip()
        line = f"{i + 1}. {line}"
        output.append(line)

    return "\n".join(output)


def sort_lines(text, order="asc"):
    lines = text.splitlines()
    if order == "asc":
        lines = sorted(lines, key=str.lower)
    else:
        lines = sorted(lines, reverse=True, key=str.lower)
    return "\n".join(lines)


def remove_empty_lines(text):
    return "\n".join(line for line in text.splitlines() if line.strip())


def move_first_word_to_end(text):
    result = []
    lines = text.splitlines()
    for line in lines:
        words = line.split(maxsplit=1)  # Split into first word and the rest
        line = f"{words[1]} {words[0]}" if len(words) > 1 else text
        result.append(line)
    return "\n".join(result)


def remove_non_ascii(text):
    # Normalize text to decompose accents
    normalized = unicodedata.normalize('NFKD', text)

    # Manually replace ł with l and Ł with L
    fixed = normalized.replace('ł', 'l').replace('Ł', 'L')

    # Remove remaining non-ASCII characters
    return ''.join(c for c in fixed if c.encode('ascii', 'ignore'))


def move_last_word_to_beginning(text):
    result = []
    lines = text.splitlines()
    for line in lines:
        words = line.rsplit(maxsplit=1)  # Split into first word and the rest
        line = f"{words[1]} {words[0]}" if len(words) > 1 else text
        result.append(line)
    return "\n".join(result)
