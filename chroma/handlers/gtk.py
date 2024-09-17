"""
Creates a color theme for GTK 4, and writes that to `~/.config/gtk-4.0/gtk.css`.
"""

import os

def apply(group):
    colors = group.colors
    for k, v in group.items():
        print(k, v)
    return

    theme = [
        f"@define-color accent_color {colors['accent_color']};",
        f"@define-color accent_bg_color {colors['accent_bg_color']};",
        f"@define-color accent_fg_color {colors['accent_fg_color']};",
        f"@define-color window_bg_color {colors['window_bg_color']};",
        f"@define-color window_fg_color {colors['window_fg_color']};",
        f"@define-color view_bg_color {colors['view_bg_color']};",
        f"@define-color view_fg_color {colors['view_fg_color']};",
        f"@define-color headerbar_bg_color {colors['headerbar_bg_color']};",
        f"@define-color headerbar_fg_color {colors['headerbar_fg_color']};",
        f"@define-color card_bg_color {colors['card_bg_color']};",
        f"@define-color card_fg_color {colors['card_fg_color']};",
        f"@define-color dialog_bg_color {colors['dialog_bg_color']};",
        f"@define-color dialog_fg_color {colors['dialog_fg_color']};",
        f"@define-color popover_bg_color {colors['popover_bg_color']};",
        f"@define-color popover_fg_color {colors['popover_fg_color']};",
        f"@define-color sidebar_bg_color {colors['sidebar_bg_color']};",
        f"@define-color sidebar_fg_color {colors['sidebar_fg_color']};",
        f"@define-color blue_1 {colors['blue_1']};",
        f"@define-color green_1 {colors['green_1']};",
        f"@define-color yellow_1 {colors['yellow_1']};",
        f"@define-color orange_1 {colors['orange_1']};",
        f"@define-color red_1 {colors['red_1']};",
        f"@define-color purple_1 {colors['purple_1']};",
        f"@define-color brown_1 {colors['brown_1']};",
        f"@define-color light_1 {colors['light_1']};",
        f"@define-color dark_1 {colors['dark_1']};",
    ]

    # Properly theme the sidebar
    # I don't like how the multiline strings are rendered with indentation or
    # that they have to be hanging off the function, so I'm doing it this way.
    # Bite me.
    sidebar_patch = [
        ".navigation-sidebar, .top-bar {",
        "  color: @sidebar_fg_color;",
        "  background-color: @sidebar_bg_color;",
        "}",
    ]

    with open(os.path.expanduser("~/.cache/chroma/kitty")) as f:
        f.writelines(theme)
        f.writelines(sidebar_patch)

        # If the group has a field for extra GTK CSS, then add that to the
        # output file too.
        if group.extra_css:
            f.write(group.extra_css)
