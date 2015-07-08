from plc.core.errors import *
from plc.core.logging import *

class Message:
    def __init__(self, *args, **kwargs):
        self.id = hash(self)
        self.__dict__.update(**kwargs)
        self._list = args
        self._dict = kwargs

    def __getitem__(self, i):
        return self._list[i]

    def __len__(self):
        return len(self._list)

    def action(self, protocol):
        action = self.__class__.__name__[:-7].lower()
        getattr(protocol.receiver, action)(*self._list, **self._dict)

class ResultMessage(Message):
    def action(self, protocol):
        debug("Result:", self._list)

class AuthMessage(Message):
    """Constructor arguments: username, hashed password"""
    def action(self, protocol):
        if protocol.user.login(self[0], self[1]):
            protocol.controller.register_client(protocol)
            protocol.send_message(ResultMessage(
                True, "Authenticated successfully", self))
        else:
            protocol.send_message(ResultMessage(
                False, "Invalid username or password", self))
            protocol.transport.close()

class DimmerMessage(Message):
    pass

class RequestMessage(Message):
    def action(self, protocol):
        obj = protocol.controller.get_list(self[0]+"s")[self[1]]
        if self[0] == "group":
            protocol.send_message(GroupMessage(obj, action="update"))
        elif self[0] == "cue":
            protocol.send_message(CueMessage(obj, action="update"))

class GroupMessage(Message):
    """Args: (action, group, [level])

    'group' should be the id of the group unless updating."""

    def action(self, protocol):
        groups = protocol.receiver.get_list("groups")
        if self[0] == "update":
            group = groups[self[1].id] = self[1]
            group._groups = groups
        else:
            group = groups[self[1]]
        if self[0] == "level" or (self[0] == "update" and len(self) > 2):
            group.level = self[2]
        protocol.receiver.group(self[0], group)

class CueMessage(GroupMessage):
    """Args: (action, cue)

    'group' should be the id of the group unless updating.
    'fader' should be supplied to select the fader to run in when
    sending a 'go' command."""

    def action(self, protocol):
        groups = protocol.receiver.get_list("cues")
        if self[0] == "update":
            group = groups[self[1].id] = self[1]
            group._groups = protocol.receiver.get_list("groups")
        else:
            group = groups[self[1]]
        protocol.receiver.cue(self[0], group)

class RegistryMessage(Message):
    pass
