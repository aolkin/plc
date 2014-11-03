from plc.core.errors import *
from plc.core.logging import *

class Message:
    def __init__(self, *args, **kwargs):
        self.id = hash(self)
        self.__dict__.update(**kwargs)
        self._list = args

    def __getitem__(self, i):
        return self._list[i]

    def action(self, protocol):
        """This function should be implemented by subclasses."""
        debug("Message received.")

class ResultMessage(Message):
    pass

class AuthMessage(Message):
    """Constructor arguments: username, hashed password"""
    def action(self, protocol):
        if protocol.user.login(self[0], self[1]):
            protocol.controller.register_client(protocol)
            protocol.send_message(ResultMessage(True, "Authenticated successfully", self))
        else:
            protocol.send_message(ResultMessage(False, "Invalid username or password", self))
