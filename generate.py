import sublime
import sublime_plugin
import json
from pathlib import Path

THEME_FILENAME = "Spacegray Adaptative.sublime-theme"
PACKAGE_DIR = Path(sublime.packages_path()) / "Theme - Spacegray Adaptative"
WIDGETS_DIR = PACKAGE_DIR / 'widgets'
WIDGET_FILE = PACKAGE_DIR / 'Widget - Spacegray Adaptative.hidden-color-scheme'
TEMP_FILE = WIDGET_FILE.with_suffix('.tmp')


class UpdateSpacegrayWidgetCommand(sublime_plugin.ApplicationCommand):

    def is_enabled(self):
        return sublime.ui_info()['theme']['resolved_value'] == THEME_FILENAME

    def run(self):
        update_widget(force=True)


def plugin_loaded():
    settings = sublime.load_settings("Preferences.sublime-settings")
    settings.add_on_change(
        "color_scheme",
        lambda: sublime.set_timeout(on_color_change, 1)
    )


def on_color_change():
    scheme_filename = sublime.ui_info()['theme']['resolved_value']
    if scheme_filename == THEME_FILENAME:
        update_widget()


def update_widget(force=False):
    current_widget_path = WIDGETS_DIR / get_widget_filename()

    if force or not current_widget_path.exists():
        WIDGETS_DIR.mkdir() if not WIDGETS_DIR.exists() else 0
        with current_widget_path.open("w+") as widget_file:
            widget_file.write(create_widget())

    TEMP_FILE.symlink_to(current_widget_path)
    TEMP_FILE.replace(WIDGET_FILE)


def get_widget_filename():
    scheme_filename = sublime.ui_info()['color_scheme']['resolved_value']
    start = scheme_filename.rfind('/') + 1
    stop = scheme_filename.rfind('.')
    name = scheme_filename[start:stop]
    return "Widget - %s.hidden-color-scheme" % name


def create_widget():
    current_style = sublime.active_window().active_view().style()
    background = hex2rgb(current_style['background'])
    current_style['background'] = rgb2hex(dim(background))
    return json.dumps(
        {
            "author": "Oreilles",
            "name": "Auto generated",
            "globals": current_style
        }, indent=4, separators=(',', ': '))


def dim(rgb):
    v = max(i for i in rgb[:3]) / 255
    k = 0.66 if v < 0.6 else 0.902
    return tuple([int(x * k) for x in rgb])


def hex2rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in range(0, len(h), 2))


def rgb2hex(rgba):
    return ('#' + '%02x' * len(rgba) % rgba).upper()
