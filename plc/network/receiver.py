from plc.core.errors import *
from plc.core.logging import *

class Receiver:
    def dimmer(self, dimmers, source=None):
        """Called when a list of dimmers is received."""
        raise ActionNotImplemented("dimmers")

    def get_list(self, name):
        """Should return the requested list."""

    def group(self, action, group):
        """Called to perform various actions on groups.
        
        Any updates to the group or its current level will already
        have been processed."""
        raise ActionNotImplemented("group")

    def cue(self, action, cue, fader=None):
        """Called to perform various actions on cues."""
        raise ActionNotImplemented("cue")

    def result(self, of, *args, **kwargs):
        """Called with the result of an action."""
        raise ActionNotImplemented("result")
