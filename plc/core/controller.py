from .settings import conf

from .integration import *

class Controller:
    def __init__(self,settings=conf):
        self.settings = settings
        self.universes = []
        for i in settings["universes"]:
            self.universes.append(Universe(
                i["output"], i["dimmers"], i["interval"],
                INTEGRATION_MODES[i["mode"]], i["input"]))

    def launch(self):
        ola_thread.start()
        while True: pass
