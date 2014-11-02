
from .logging import *
from .settings import conf

from ola.DMXConstants import *
from ola.ClientWrapper import ClientWrapper

from threading import Thread, Lock

from array import array

INTEGRATION_MODES = {
    "LTP": 0,
    "HTP": 1
}

ola_lock = Lock()

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

ola_thread = _OlaThread()

class Universe:
    def __init__(self, output, dimmers=DMX_UNIVERSE_SIZE, interval=100,
                 mode=INTEGRATION_MODES["LTP"], input=None):
        self.dimmers = array("B", [0 for i in range(dimmers)])
        self.override = []
        self.last_input = array("B", [0 for i in range(dimmers)])
        self.mode = mode
        self.interval = interval
        self.handlers = []
        self.output = sorted(map(lambda x: (int(x[0]), x[1]),output.items()))
        self.input = input
        ola_thread.universes.append(self)

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
                self.dimmers[i] = d
                changed[i] = d
            elif i in self.override:
                self.dimmers[i] = d
        self.last_input = data
        if len(changed): debug("Changed inputs:", changed)
        for i in self.handlers:
            i(self, changed, data)

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
