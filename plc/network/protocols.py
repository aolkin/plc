from asyncio import Protocol

import pickle

from struct import Struct

from .messages import *
from .authentication import *
from plc.core.errors import *
from plc.core.logging import *

HEADER_STRUCT = Struct("!BH")

class PLCProtocol(Protocol):
    __version__  = 1

    def __init__(self):
        self.header = b''
        self.data = b''

    def connection_made(self, transport):
        self.transport = transport

    def data_received(self, data):
        while len(data):
            while len(data) and len(self.header) < HEADER_STRUCT.size:
                self.header += data[0:1]
                data = data[1:]
            version, self.length = HEADER_STRUCT.unpack(self.header)
            if version != self.__version__:
                raise NetworkError("Protocol version mismatch: need {}, got {}".format(
                    self.__version__, version))
            while len(data) and (len(self.data) < self.length):
                bytes_needed = self.length - len(self.data)
                self.data += data[:bytes_needed]
                data = data[bytes_needed:]
            if len(self.data) == self.length:
                self.on_message(pickle.loads(self.data))
                self.data = b''
                self.header = b''

    def send_message(self, data):
        data = pickle.dumps(data, conf["server"].get("pickle_version", None))
        header = HEADER_STRUCT.pack(self.__version__, len(data))
        self.transport.write(header + data)

    def on_message(self,obj):
        debug("Received:", obj)
        obj.action(self)

class ServerProtocol(PLCProtocol):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller

    def connection_made(self, transport):
        super().connection_made(transport)
        self.user = User()
        debug("Connection from {}".format(transport.get_extra_info("peername")))

    def connection_lost(self, exc):
        if self.user.authenticated:
            try:
                self.controller.unregister_client(self)
            except ValueError: pass
        if exc:
            warn(repr(exc))

    def on_message(self,obj):
        debug("Received:", obj)
        obj.server_action(self)

class ClientProtocol(PLCProtocol):
    def __init__(self, user, pw, client):
        super().__init__()
        self.username = user
        self.pw = pw
        self.client = client

    def connection_made(self, transport):
        super().connection_made(transport)
        debug("Connected to {}".format(transport.get_extra_info("peername")))
        self.send_message(AuthMessage(self.username, self.pw))

    def on_message(self,obj):
        debug("Received:", obj)
        obj.client_action(self)
