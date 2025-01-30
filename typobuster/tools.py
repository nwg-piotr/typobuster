import json
import os
import re
import sys


def config_dir():
    xdg_config_home = os.getenv('XDG_CONFIG_HOME')
    config_home = xdg_config_home if xdg_config_home else os.path.join(os.getenv("HOME"), ".config")

    return os.path.join(config_home, "typobuster")


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
        "sanitize-spaces": True,
        "sanitize-punctuation-marks": True,
        "sanitize-hyphens": True,
        "sanitize-quotes": True,
        "sanitize-eol": True,
        "view-line-numbers": True,
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


def load_text_file(path):
    try:
        with open(path, 'r') as file:
            data = file.read()
            return data
    except Exception as e:
        eprint(e)
        return None


def save_text_file(text, path):
    try:
        with open(path, 'w') as file:
            file.write(text)
            return "ok"
    except Exception as e:
        eprint(e)
        return e


def sanitize_hyphens(text, start_idx, end_idx):
    selection = text[start_idx:end_idx]
    selection = selection.replace("–", "-")  # Replace en-dashes with hyphens
    selection = selection.replace(" -", " - ")  # Add spaces around hyphens
    selection = selection.replace("- ", " - ")  # Add spaces around hyphens
    return text[:start_idx] + selection + text[end_idx:]


def sanitize_quotes(text, start_idx, end_idx):
    selection = text[start_idx:end_idx]
    selection = selection.replace(',,', '"')  # Replace double comma with English-style quotes
    selection = re.sub(r"[„”]", '"', selection) # Replace German-style quotes with English-style quotes
    return text[:start_idx] + selection + text[end_idx:]


def sanitize_punctuation_marks(text, start_idx, end_idx):
    selection = text[start_idx:end_idx]
    selection = re.sub(r'\s+([.,!?;:])', r'\1', selection)  # Remove spaces before punctuation marks
    selection = re.sub(r'([.,!?;:])([A-Za-z0-9])', r'\1 \2', selection)
    selection = selection.replace('. ,', '.,')
    selection = selection.replace('. . .', '...')
    return text[:start_idx] + selection + text[end_idx:]


def sanitize_spaces(text, start_idx, end_idx):
    selection = text[start_idx:end_idx]
    selection = re.sub(r" {2,}", " ", selection)  # Replace two or more spaces with a single space
    selection = selection.replace("\n ", "\n")  # Remove spaces right after end-of-line characters
    return text[:start_idx] + selection + text[end_idx:]


def sanitize_eol(text, start_idx, end_idx):
    selection = text[start_idx:end_idx]
    selection = re.sub(r"\n{2,}", "\n", selection)  # Replace two or more end-of-line characters with a single one
    selection = selection.replace("\n", "\n\n")  # Double all end-of-line characters
    selection = selection.replace(" \n", "\n")  # Remove spaces before end-of-line characters
    return text[:start_idx] + selection + text[end_idx:]
