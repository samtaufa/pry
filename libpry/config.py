"""
    A reader for the simple .pry config file format.  The format is as follows:

        base = basedirectory
        coverage = coveragedirectory
        exclude =   newline separated
                    paths excluded
                    from coverage
"""
import ConfigParser, cStringIO, os.path

class Config:
    _valid = set(["base", "coverage", "exclude"])
    def __init__(self, path):
        self.path = path
        if os.path.isfile(path):
            self.c = ConfigParser.SafeConfigParser()
            data = open(path).read()
            # You know, Python is my favourite language and all, but its
            # standard library can be utterly moronic
            io = cStringIO.StringIO()
            io.write("[pry]\n")
            io.write(data)
            io.reset()
            self.c.readfp(io)
            options = set(self.c.options("pry"))
            if not self._valid.issuperset(options):
                bad = options - self._valid
                bad = ",".join(list(bad))
                raise ValueError, "Unknown options in config file: %s"%bad
            items = dict(self.c.items("pry"))
            self.base = items.get("base", "..").strip()
            self.coverage = items.get("coverage", "..").strip()
            ex = items.get("exclude", ".")
            ex = ex.split("\n")
            self.exclude = [i.strip() for i in ex]
        else:
            self.base = ".."
            self.coverage = ".."
            self.exclude = ["."]
