
import sys, json, os

default_fn = sys.argv[1] if len(sys.argv) > 1 else "settings.json"

class Configuration(dict):
    def save(self, fn=default_fn):
        fd = open(fn,"w")
        json.dump(self,fd)
        fd.close()

    def load(self, fn=default_fn):
        fd = open(fn,"r")
        self.update(json.load(fd))
        fd.close()

conf = Configuration()
if os.path.exists(default_fn):
    conf.load()
else:
    print("Warning: configuration not found!", file=sys.stderr)
