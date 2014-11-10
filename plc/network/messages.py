from plc.core.errors import *
from plc.core.logging import *

class Message:
    def __init__(self, *args, **kwargs):
        self.id = hash(self)
        self.__dict__.update(**kwargs)
        self._list = args

    def __getitem__(self, i):
        return self._list[i]

    def __len__(self):
        return len(self._list)

    def action(self, protocol):
        debug("Message received.")

    def server_action(self, protocol):
        self.action(protocol)
    
    def client_action(self, protocol):
        self.action(protocol)

class ResultMessage(Message):
    def action(self, protocol):
        debug("Result:", self._list)

### Server messages

class AuthMessage(Message):
    """Constructor arguments: username, hashed password"""
    def action(self, protocol):
        if protocol.user.login(self[0], self[1]):
            protocol.controller.register_client(protocol)
            protocol.send_message(ResultMessage(True, "Authenticated successfully", self))
        else:
            protocol.send_message(ResultMessage(False, "Invalid username or password", self))

class DimmerMessage(Message):
    def server_action(self, protocol):
        protocol.controller.do_update("dimmers", self[0])

    def client_action(self, protocol):
        protocol.client.pads.dimmers.set_dimmers(self[0], self[1] if len(self) > 1 else None)

class RequestMessage(Message):
    def server_action(self, protocol):
        obj = getattr(protocol.controller, self[0]+"s")[self[1]]
        if self[0] == "group":
            protocol.send_message(GroupMessage(obj, action="update"))
        elif self[0] == "cue":
            protocol.send_message(CueMessage(obj, action="update"))

class GroupMessage(Message):
    """Args: (action, group, [level])

    group should be the id of the group unless updating."""
    def server_action(self, protocol):
        if self[0] == "update":
            group = protocol.controller.groups[self[1].id] = self[1]
            group._groups = protocol.controller.groups
        else:
            group = protocol.controller.groups[self[1]]
        if self[0] == "level" or (self[0] == "update" and len(self) > 2):
            group.level = self[2]
        protocol.controller.do_update("group", group)
        for i in protocol.controller.clients:
            i.send_message(self)

class CueMessage(GroupMessage):
    def server_action(self, protocol):
        super().server_action(protocol)
