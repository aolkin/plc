
from .logging import *
from .settings import conf
from .errors import *

from ola.DMXConstants import *
from ola.ClientWrapper import ClientWrapper

from threading import Thread, Lock

from array import array

INTEGRATION_MODES = {
    "LTP": 0,
    "HTP": 1 ### Need to actually implement this at some point, I suppose...
}

class _OlaThread(Thread):
    def __init__(self):
        super().__init__()
        self.daemon = True
        self.universes = []

    def run(self):
        self.wrapper = ClientWrapper()
        self.client = self.wrapper.Client()
        for i in self.universes:
            i.register(self)
            log("Starting OLA Wrapper...")
            self.wrapper.Run()
            log("OLA Wrapper stopped...")

ola_lock = Lock()
ola_thread = _OlaThread()

class Universe:
    def __init__(self, output, dimmers=DMX_UNIVERSE_SIZE, interval=100,
                 mode=INTEGRATION_MODES["LTP"], input=None,
                 controller=None, allow_ignore_dmx=False):
        self.dimmers = array("B", [0 for i in range(dimmers)])
        self.override = []
        self.last_input = array("B", [0 for i in range(dimmers)])
        self.mode = mode
        self.interval = interval
        self.controller = controller
        self.__allow_ignore_input = allow_ignore_dmx
        self.__ignore_input = False
        self.output = sorted(map(lambda x: (int(x[0]), x[1]),output.items()))
        self.input = input
        ola_thread.universes.append(self)

    @property
    def ignore_dmx(self):
        return self.__ignore_input

    @ignore_dmx.setter
    def ignore_dmx(self,val):
        if val and (not self.__allow_ignore_input):
            raise DisallowedOperation("Ignoring DMX disabled for this universe.")
        self.__ignore_input = val

    def register(self, thread):
        self.thread = thread
        if self.input != None:
            thread.client.RegisterUniverse(self.input, thread.client.REGISTER,
                                           self._received_dmx)
        thread.wrapper.AddEvent(self.interval, self._send_dmx)
        
    def _received_dmx(self, data):
        changed = {}
        for i, d in enumerate(data[:len(self.dimmers)]):
            if d != self.last_input[i]:
                if not self.__ignore_input:
                    self.dimmers[i] = d
                changed[i] = d
            elif i in self.override:
                if not self.__ignore_input:
                    self.dimmers[i] = d
        self.last_input = data
        if len(changed): debug("Changed inputs:", changed)
        if self.controller and hasattr(self.controller, "on_dmx"):
            self.controller.on_dmx(self, changed, data, self.__ignore_input)

    def _send_dmx(self):
        self.thread.wrapper.AddEvent(self.interval, self._send_dmx)
        index = 0
        for i, u in self.output:
            if u != None:
                self.thread.client.SendDmx(u, self.dimmers[index:i],
                                           (lambda x, u=u: self._sent_dmx(u, x)))
            index = i
        
    def _sent_dmx(self, ola, status):
        if not status.Succeeded():
            error("Failed to send DMX on OLA Universe {}".format(ola))

    def set_dimmers(self,values):
        with ola_lock:
            for i, j in values.items():
                d = max(min(j, DMX_MAX_SLOT_VALUE), DMX_MIN_SLOT_VALUE)
                if d != j:
                    warn("Invalid DMX value {}, normalizing to {}".format(j,d))
                self.dimmers[i] = d
