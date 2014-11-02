from .settings import conf
import sys, time
import traceback as tb

settings = conf["logging"]

class NullFD:
    def write(*args,**kwargs):
        pass

if conf["daemon"]:
    DESCRIPTORS = [NullFD(), sys.stdout, sys.stderr]
else:
    DESCRIPTORS = [NullFD(), open("output.log", "a"), open("errors.log","a")]

def _log(level, *args):
    print(time.strftime("[%m/%d/%y %H:%M:%S]"), *args, file=DESCRIPTORS[settings[level]])

def log(*args):
    _log("logging", *args)

def debug(*args):
    _log("debug", "Debug:", *args)

def warn(*args):
    _log("warnings", "Warning:", *args)

def error(*args):
    _log("errors", *args)

def last_exception():
    error(tb.format_exc())
