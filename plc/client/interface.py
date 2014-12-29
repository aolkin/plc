import curses

from ..core.errors import *
from ..core.logging import *
from ..core.data import *
from ..core.settings import conf

from ..network.receiver import Receiver

from .colors import init_colors, get_color

import time, sys, os

MAX_ENTITIES = 999

MAX_TIME = 9999

DIMMER_MAX = 255

def percent(l):
    return int(l / DIMMER_MAX * 100)

class _ObjectDict(dict):
    def __getattr__(self, k):
        return self[k]

    def __setattr__(self, k, v):
        self[k] = v

class Pad:
    def __init__(self, xfrac, yfrac, linefrac, colfrac, zindex=100):
        self.xfrac = xfrac
        self.yfrac = yfrac
        self.linefrac = linefrac
        self.colfrac = colfrac
        self.z = zindex
        self.enabled = True

    def __lt__(self, other):
        return self.z < other.z

    def resize(self, w, h):
        self.x = int(self.xfrac * w)
        self.y = int(self.yfrac * h)
        self.rows = int(self.linefrac * h)
        self.cols = int(self.colfrac * w)
        self.pad = curses.newpad(self.rows, self.cols)
        if hasattr(self, "post_resize"):
            self.post_resize(w, h)

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
        return [i + (self.y if n % 2 == 0 else self.x)
                for n, i in enumerate(args)]

    def handle_mouse(self, e):
        log(self.__class__, e)

class StatusPad(Pad):
    def __init__(self, screen):
        self.screen = screen
        super().__init__(0, 0, 0.0625, 1, 0)
        self.screen.loop.call_soon(self.timed_update)

    def post_resize(self, w, h):
        self.pad.addstr(0, 0, " Python Lighting Controls ", curses.A_REVERSE)

    def timed_update(self):
        self.screen.loop.call_later(1, self.timed_update)
        self.pad.addstr(0, self.cols-10, time.strftime(" %I:%M %p "),
                        curses.A_REVERSE) # width: 10

class DimmerPad(Pad):
    def __init__(self, scr, n):
        self.dimmers = [0 for i in range(n)]
        super().__init__(0, 0.0625, 0.5, 1, 10)

    def resize(self, w, h):
        super().resize(w // 4 * 4, h)

    def post_resize(self, w, h):
        self.dcols = int(w / 4)
        for i in range(len(self.dimmers)):
            self.pad.addstr("{:0>3} ".format(i + 1))
            if (i + 1) % self.dcols == 0:
                y, x = self.pad.getyx()
                y += 2
                if y < self.rows:
                    self.pad.move(y, x)

    def set_dimmers(self, d, source=None):
        attrs = 0
        if source == "input":
            attrs = curses.A_DIM
        if source == "Cue":
            attrs = get_color("GREEN")
        for i, j in d.items():
            try:
                self.dimmers[i] = j
                col = int(i % self.dcols) * 4
                row = int(int(i / self.dcols) * 3 + 1)
                s = "{:>3} ".format(int((j / 255) * 100)) if j != 0 else "    "
                self.pad.addstr(row, col, s, attrs)
            except KeyError:
                pass

HALF_WIDTH = 0.5

class BoxedPad(Pad):
    def __init__(self, *args):
        super().__init__(*args)

    def post_resize(self, w, h):
        self.pad.border()

    def addstr(self, x, y, *args):
        self.pad.addstr(x + 1, y + 1, *args)

class ListPad(BoxedPad):
    def __init__(self, screen):
        self.screen = screen
        super().__init__(0.5, 0.4375, 0.5625, 0.5)

    def post_resize(self, w, h):
        super().post_resize(w, h)
        self.grouppad = curses.newpad(MAX_ENTITIES * 2, self.cols - 4)
        self.cuepad = curses.newpad(MAX_ENTITIES * 2, self.cols - 4)
        self.mode()
        if hasattr(self, "groups"):
            self.refresh(self.screen.mode+"s")

    def mode(self):
        self.currentrow = 0
        if self.screen.mode == "group":
            self.addstr(0, int(self.cols / 2 - 3), "Groups", curses.A_BOLD)
            self.addstr(1, 1, "  # Name" + " "*(self.cols - 13) + "@",
                        curses.A_REVERSE)
        elif self.screen.mode == "cue":
            self.addstr(0, int(self.cols / 2 - 3), " Cues ", curses.A_BOLD)
            self.addstr(1, 1, "  # Name" + " "*(self.cols - 43) +
                        "Up Down UWait DWait Follow:Time",
                        curses.A_REVERSE)

    def post_update(self):
        if not hasattr(self, "rows"):
            return False
        getattr(self, self.screen.mode+"pad").noutrefresh(
            self.currentrow, 0, *self.shift(4, 2, self.rows - 4, self.cols - 2))

    def refresh(self, t):
        if t == "groups":
            self.grouppad.clear()
            for i, j in sorted(self.groups.items()):
                row = "{:>3} {}{{}}{:>3}\n".format(i, getattr(j, "name", ""),
                                                   percent(j.level))
                self.grouppad.addstr(row.format( " " * (self.cols - len(row) - 1) ))
        elif t == "cues":
            self.cuepad.clear()
            for i, j in sorted(self.cues.items()):
                row = ("{:>3} {}{{}}{:>4} {:>4}  {:>4}  {:>4}    {:>3} " +
                       "{:>4}\n").format(i, getattr(j, "name", ""), j.up,
                                         j.down, j.upwait, j.downwait,
                                         j.follow if j.follow else "",
                                         j.followtime if j.followtime else "")
                self.cuepad.addstr(row.format( " " * (self.cols - len(row) - 1) ))

class SelectedPad(BoxedPad):
    def __init__(self, screen):
        self.screen = screen
        super().__init__(0, 0.4375, 0.25, 0.5)

class RunningPad(BoxedPad):
    def __init__(self, screen):
        self.screen = screen
        super().__init__(0, 0.6875, 0.3125, 0.5)

class Screen(Receiver):
    def __init__(self, loop):
        self.loop = loop
        self.pads = _ObjectDict()
        self.mode = "group"

    def fatal(self, msg):
        error(msg)
        self.loop.stop()

    def update(self):
        self.loop.call_later(0.05, self.update)
        c = self.scr.getch()
        if c == ord("q"):
            self.loop.stop()
            return False
        elif c == ord("m"):
            self.mode = ("group" if self.mode == "cue" else "cue")
            self.pads.list.mode()
        elif c == curses.KEY_MOUSE:
            self.handle_mouse()
        elif c == curses.KEY_RESIZE:
            self.resize()
        for i in sorted(self.pads.values()):
            i.update()
        self.scr.refresh()

    def handle_mouse(self):
        e = curses.getmouse()
        for i in self.pads.values():
            if i.pad.enclose(e[2], e[1]):
                i.handle_mouse(e)

    def resize(self):
        self.height, self.width = self.scr.getmaxyx()
        for i in self.pads.values():
            i.resize(self.width, self.height)
            i.update()
        self.scr.refresh()

    def wrapper(self, func, protocol):
        self.func = func
        self.protocol = protocol
        curses.wrapper(self.wrapped)

    def create_pads(self):
        self.pads.status = StatusPad(self)
        self.pads.dimmers = DimmerPad(self, conf["dimmers"])
        self.dimmer = self.pads.dimmers.set_dimmers
        self.pads.selected = SelectedPad(self)
        self.pads.running = RunningPad(self)
        self.pads.list = ListPad(self)

    def wrapped(self, stdscr):
        self.scr = stdscr
        self.scr.nodelay(True)
        self.original_cursor = curses.curs_set(0)

        curses.mousemask(curses.BUTTON1_CLICKED |
                         curses.BUTTON1_DOUBLE_CLICKED)
        init_colors()

        self.create_pads()
        self.resize()
        self.func()
        curses.curs_set(self.original_cursor)

    def get_list(self, name):
        return getattr(self.pads.list, name)

    def group(self, action, group):
        self.pads.list.refresh("groups")

    def cue(self, action, group):
        self.pads.list.refresh("cues")
