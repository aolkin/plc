
from .settings import conf

import pickle, os

def _get_fn(fn):
    return os.path.join(conf["saving"].get("folder", "."), fn)

class PersistentData:
    def __init__(self, fn):
        self.__fn = fn
        if fn and os.path.exists(_get_fn):
            fd = open(_get_fn(fn), "rb")
            obj = pickle.load(fd)
            fd.close()
            self.__fields = set(obj.keys())
            self.__dict__.update(obj)
            self.__loaded = True
        else:
            self.__fields = set()
            self.__loaded = False

    @property
    def loaded(self):
        return self.__loaded

    def save(self, fn=None):
        if not (fn or self.__fn):
            raise ValueError("Must supply a filename")
        obj = {}
        for i in self.__fields:
            obj[i] = getattr(self, i)
        fd = open(_get_fn(fn or self.__fn), "wb")
        pickle.dump(obj, fd, conf["saving"].get("pickle_version", None))
        fd.close()

    def __setattr__(self, attr, val):
        if attr in ("save", "load", "loaded"):
            raise AttributeError("Cannot save data called 'save', 'load', or 'loaded'.")
        if not ("_PersistentData__" in attr):
            self.__fields.add(attr)
        super().__setattr__(attr, val)
