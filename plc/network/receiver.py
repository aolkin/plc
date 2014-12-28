from plc.core.errors import *
from plc.core.logging import *

class Receiver:
    """Base class for protocol client receivers."""
    def dimmer(self, dimmers, source=None):
        """Called when a list of dimmers is received."""
        raise ActionNotImplemented("dimmers")

    def get_list(self, name):
        """Should return the requested list."""

    def group(self, action, group):
        """Called to perform various actions on groups.
        
        Any updates to the group or its current level will already
        have been processed. 'group' will always be the group object."""
        raise ActionNotImplemented("group")

    def cue(self, action, cue, fader=None):
        """Called to perform various actions on cues.
        
        Any updates to the group will already have been processed.
        'cue' will always be the cue object."""
        raise ActionNotImplemented("cue")

    def result(self, of, *args, **kwargs):
        """Called with the result of an action."""
        raise ActionNotImplemented("result")
