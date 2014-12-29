from curses import *

COLOR_PAIRS = {
    "yellow": (1, COLOR_YELLOW, -1),
    "green": (2, COLOR_GREEN, -1),
}

def init_colors():
    use_default_colors()
    for i, f, g in COLOR_PAIRS.values():
        init_pair(i, f, g)

def get_color(name):
    return color_pair(COLOR_PAIRS[name.lower()][0])
