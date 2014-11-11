
import pickle

from ola.DMXConstants import *

from .settings import conf
from .errors import *

def _verify_level(i):
    if i < 0 or i > 1:
        raise InvalidLevelError()

class Registry(dict):
    def __init__(self,cls):
        self._cls = cls

    def new(self, id):
        self[id] = self._cls(id)
        return self[id]

    def add_binary(self, b):
        obj = pickle.loads(b)
        self[obj.id] = obj
        return obj

    def get_binary(self):
        return pickle.dumps(self, conf["saving"].get("pickle_version", None))

    def load(self, b):
        self.update(pickle.loads(b))

class DimmerGroup:
    """Contains a list of channels and nested groups.
    When outputted, any channels will entirely override groups,
    while groups are combined in a HTP fashion."""

    def __init__(self, id, group_registry=None):
        self.id = id
        self.channels = {}
        self.nested = {}
        self.level = 0
        self.name = ""
        self._groups = group_registry

    def get_dimmers(self):
        return self.get_dimmers_at(self.level)

    def get_dimmers_at_level(self, level):
        return self.get_dimmers_at(level / DMX_MAX_SLOT_VALUE)

    def get_dimmers_at(self, level):
        self.level = round(level * DMX_MAX_SLOT_VALUE)
        dimmers = {}
        for obj, intensity in self.nested.items():
            for d, i in self._groups[obj].get_dimmers_at(intensity):
                if i > dimmers.get(d,0):
                    dimmers[d] = i
        dimmers.update(self.channels)
        for d, i in dimmers.items():
            dimmers[d] = round(dimmers[d] * level * DMX_MAX_SLOT_VALUE)
        return dimmers

    def get_binary(self):
        return pickle.dumps(self, conf["saving"].get("pickle_version", None))

class Group(DimmerGroup):
    """Groups will not persist channels at 0, while cues will."""
    def __init__(self, *args):
        super().__init__(*args)
        self.__discard_zero = True

    @property
    def keep_zeros(self):
        return not self.__discard_zero

    @keep_zeros.setter
    def keep_zeros(self, val):
        self.__discard_zero = not val

    def __getitem__(self, i):
        return self.channels[i]

    def __setitem__(self, i, val):
        if self.__discard_zero and val == 0:
            del self.channels[i]
        else:
            _verify_level(val)
            self.channels[i] = val

    def setzero(self, i):
        self.channels[i] = 0

class Cue(DimmerGroup):
    def __init__(self, *args):
        super().__init__(*args)
        self.meta = {}

    def __getitem__(self, i):
        try:
            return self.meta.get(i, conf["defaults"]["cue"][i])
        except KeyError as err:
            raise MissingDefaultError("cue", i)

    def __setitem__(self, i, val):
        self.meta[i] = val

    def persist_defaults(self):
        for i, val in conf["defaults"]["cue"].items():
            self.meta.setdefault(i, val)

    def add_group(self, g, i):
        """Also use this to change group intensities."""
        _verify_level(i)
        self.nested[g] = i

    def remove_group(self, g):
        del self.nested[g]

    def add_channel(self, c, i):
        _verify_level(i)
        self.channels[c] = i

    def remove_channel(self, c):
        del self.channels[c]
