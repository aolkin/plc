
from .logging import *
from .errors import *

from threading import Thread
from time import sleep, time

UP = 0
DOWN = 1

GO = 0
PAUSE = 1
JUMP_TO_END = 10
CANCEL = 11
STOP = 12
BACK = 11

class Fader(Thread):
    def __init__(self, controller, cue, direction=UP):
        super().__init__()
        self.controller = controller
        self.cue = cue
        self.direction = direction
        self.command = GO
        self.__done = False

        ctime = time()
        if direction == UP:
            self.completion_time = cue.up + cue.upwait + ctime
            self.start_time = cue.upwait + ctime
            self.ftime = cue.up
        elif direction == DOWN:
            self.completion_time = cue.down + cue.downwait + ctime
            self.start_time = cue.downwait + ctime
            self.ftime = cue.down
        self.start()

    def run(self):
        while self.command < 10:
            ctime = time()
            if self.completion_time <= ctime:
                self.command = JUMP_TO_END
            elif self.start_time <= ctime:
                self.cue.level = max((self.completion_time - ctime)
                            / self.ftime, 0)
                if self.direction == UP:
                    self.cue.level = 1 - self.cue.level
                self.controller.do_update(self.cue)
            sleep(0.05)
        if self.command == STOP:
            log("Stopping fader ({})".format(self.cue))
        elif self.command == JUMP_TO_END:
            self.cue.level = 1 if self.direction == UP else 0
        elif self.command == CANCEL:
            self.cue.level = 1 if self.direction == DOWN else 0
        self.controller.do_update(self.cue)
        self.__done = True

    def stop(self):
        self.command = STOP

    @property
    def done(self):
        return self.__done
