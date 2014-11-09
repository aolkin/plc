from curses import *

class Screen:
    def __init__(self, loop):
        self.loop = loop

    def update(self):
        c = self.scr.getch()
        if c == ord("q"):
            self.loop.stop()
            return False
        self.scr.refresh()
        self.loop.call_later(0.05, self.update)

    def wrapper(self, func):
        self.func = func
        wrapper(self.wrapped)

    def wrapped(self, stdscr):
        self.scr = stdscr
        self.scr.nodelay(True)
        self.win = newwin(64, 160)
        self.func()
