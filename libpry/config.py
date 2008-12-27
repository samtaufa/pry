"""
    A reader for the simple .pry config file format.  The format is as follows:

        base = basedirectory
        coverage = coveragedirectory
        exclude =   newline separated
                    paths excluded
                    from coverage

    The special _magic flag is needed to allow pry to run coverage analysis on
    itsef.
"""
import configparser, io, os.path

class Config:
    _valid = set(["base", "coverage", "exclude", "_magic"])
    def __init__(self, path):
        self.path = path
        if os.path.isfile(path):
            self.c = configparser.SafeConfigParser()
            data = open(path).read()
            # You know, Python is my favourite language and all, but its
            # standard library can be utterly moronic
            sio = io.StringIO()
            sio.write("[pry]\n")
            sio.write(data)
            sio.seek(0, 0)
            self.c.readfp(sio)
            options = set(self.c.options("pry"))
            if not self._valid.issuperset(options):
                bad = options - self._valid
                bad = ",".join(list(bad))
                raise ValueError("Unknown options in config file: %s"%bad)
            items = dict(self.c.items("pry"))
            self.base = items.get("base", "..").strip()
            self.coverage = items.get("coverage", "..").strip()
            if "_magic" in items:
                self._magic = True
            else:
                self._magic = False
            ex = items.get("exclude", ".")
            ex = ex.split("\n")
            self.exclude = [i.strip() for i in ex]
        else:
            self.base = ".."
            self.coverage = ".."
            self.exclude = ["."]
            self._magic = False
