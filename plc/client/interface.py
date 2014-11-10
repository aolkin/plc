from curses import *

from ..core.errors import *
from ..core.logging import *

DIMMER_MAX = 255

COLS = 160

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
        self.pad = newpad(self.rows, self.cols)

    def update(self):
        self.pad.noutrefresh(0, 0, self.y, self.x,
                             self.y + self.rows, self.x + self.cols)

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

class Screen:
    def __init__(self, loop):
        self.loop = loop
        self.pads = _ObjectDict()

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

    def wrapped(self, stdscr):
        self.scr = stdscr
        self.scr.nodelay(True)

        self.pads.dimmers = DimmerPad(320)

        self.func()
