from curses import *

from ..core.errors import *
from ..core.logging import *
from ..core.data import *

import time, sys, os

MAX_ENTITIES = 999

DIMMER_MAX = 255

COLS = 160

def percent(l):
    return int(l / DIMMER_MAX * 100)

class _ObjectDict(dict):
    def __getattr__(self, k):
        return self[k]

    def __setattr__(self, k, v):
        self[k] = v

class Pad:
    def __init__(self, x, y, lines, cols):
        self.x = int(x)
        self.y = int(y)
        if (int(lines) != lines) or (int(cols) != cols):
            raise PadSizeError("Dimensions must be whole numbers.")
        self.rows = int(lines)
        self.cols = int(cols)
        self.enabled = True
        self.pad = newpad(self.rows, self.cols)

    def move(self, x, y, add=False):
        self.x = int(self.x + x if add else x)
        self.y = int(self.y + y if add else y)

    def update(self):
        if self.enabled:
            self.pad.noutrefresh(0, 0, self.y, self.x,
                                 self.y + self.rows, self.x + self.cols)
            if hasattr(self, "post_update"):
                self.post_update()

    def shift(self, *args):
        return [i + (self.y if n % 2 == 0 else self.x) for n, i in enumerate(args)]

class StatusPad(Pad):
    def __init__(self, screen):
        self.screen = screen
        super().__init__(0, 0, 4, COLS)
        self.screen.loop.call_soon(self.timed_update)
        self.pad.addstr(0, 0, " Python Lighting Controls ", A_REVERSE)

    def timed_update(self):
        self.screen.loop.call_later(1, self.timed_update)
        self.pad.addstr(0, 150, time.strftime(" %I:%M %p "), A_REVERSE) # width: 10

class DimmerPad(Pad):
    def __init__(self, n):
        cols = COLS
        self.dcols = cols / 4
        super().__init__(0, 4, n / self.dcols * 3, cols)
        self.dimmers = [0 for i in range(n)]
        for i in range(n):
            self.pad.addstr("{:0>3} ".format(i + 1))
            if (i + 1) % self.dcols == 0:
                y, x = self.pad.getyx()
                y += 2
                if y < self.rows:
                    self.pad.move(y, x)

    def set_dimmers(self, d, source=None):
        attrs = 0
        if source == "input":
            attrs = A_DIM
        for i, j in d.items():
            try:
                self.dimmers[i] = j
                col = int(i % self.dcols) * 4
                row = int(int(i / self.dcols) * 3 + 1)
                s = "{:>3} ".format(int((j / 255) * 100)) if j != 0 else "    "
                self.pad.addstr(row, col, s, attrs)
            except KeyError:
                pass

HALF_WIDTH = COLS / 2

class BoxedPad(Pad):
    def __init__(self, *args):
        super().__init__(*args)
        self.pad.border()

    def addstr(self, x, y, *args):
        self.pad.addstr(x + 1, y + 1, *args)

class ListPad(BoxedPad):
    def __init__(self, screen):
        self.screen = screen
        super().__init__(HALF_WIDTH, 28, 36, HALF_WIDTH)
        self.grouppad = newpad(MAX_ENTITIES * 2, 76)

    def mode(self):
        self.currentrow = 0
        if self.screen.mode == "group":
            self.addstr(0, int(self.cols / 2 - 3), "Groups", A_BOLD)
            self.addstr(1, 1, "  # Name" + "    "*16 + "   @", A_REVERSE)
        elif self.screen.mode == "cue":
            pass

    def post_update(self):
        getattr(self, self.screen.mode+"pad").noutrefresh(
            self.currentrow, 0, *self.shift(4, 2, self.rows - 4, self.cols - 2))

    def refresh(self, t):
        if t == "groups":
            self.grouppad.clear()
            for i, j in sorted(self.groups.items()):
                self.grouppad.addstr("{:>3} {:<68} {:>3}\n".format(i, getattr(j, "name", ""),
                                                                   percent(j.level)))

class SelectedPad(BoxedPad):
    def __init__(self, screen):
        self.screen = screen
        super().__init__(0, 28, 16, HALF_WIDTH)

class RunningPad(BoxedPad):
    def __init__(self, screen):
        self.screen = screen
        super().__init__(0, 44, 20, HALF_WIDTH)

class Screen:
    def __init__(self, loop):
        self.loop = loop
        self.pads = _ObjectDict()
        self.mode = "group"

    def fatal(self, msg):
        error(msg)
        self.loop.stop()

    def update(self):
        c = self.scr.getch()
        if c == ord("q"):
            self.loop.stop()
            return False
        for i in self.pads.values():
            i.update()
        self.scr.refresh()
        self.loop.call_later(0.05, self.update)

    def wrapper(self, func, protocol):
        self.func = func
        self.protocol = protocol
        wrapper(self.wrapped)

    def create_pads(self):
        self.pads.status = StatusPad(self)
        self.pads.dimmers = DimmerPad(320)
        self.pads.selected = SelectedPad(self)
        self.pads.running = RunningPad(self)
        self.pads.list = ListPad(self)
        self.pads.list.mode()

    def wrapped(self, stdscr):
        self.scr = stdscr
        self.scr.nodelay(True)
        self.original_cursor = curs_set(0)

        self.create_pads()
        self.func()
        curs_set(self.original_cursor)
