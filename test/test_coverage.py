import dis
import os.path
import libpry
import libpry.coverage


class uFile(libpry.TestTree):
    def test_getLines(self):
        f = libpry.coverage.File(None)
        fname = "covfiles/linenos.py"
        d = open(fname).read()
        code = compile(d, fname, "exec")
        l = f.getLines(code)
        assert l == set([2, 3, 4, 5, 6, 8])

    def test_getExclusions(self):
        f = libpry.coverage.File(None)
        fname = "covfiles/exclusions.py"
        d = open(fname).read()
        l = f.getExclusions(d, fname)
        assert l == set([4, 5, 11, 12])

    def test_getExclusions(self):
        f = libpry.coverage.File(None)
        fname = "covfiles/exclusions_err.py"
        d = open(fname).read()
        libpry.raises("unbalanced", f.getExclusions, d, fname)

    def test_init(self):
        f = libpry.coverage.File("covfiles/combo.py")
        assert f.executable == set([3, 4, 11])

    def test_nicePath(self):
        f = libpry.coverage.File(None)
        f.path = "/foo/bar.py"
        assert f.nicePath("/foo") == "bar.py"

    def test_stats(self):
        c = libpry.coverage.File(None)
        c.executable = set([1, 2, 3, 4])
        c.executed = set([1, 2])
        assert c.numExecutable == 4
        assert c.numExecuted == 2
        assert c.notExecuted == set([3, 4])
        assert c.percentage == 50.0
        assert c.notExecutedRanges == [(3, 4)]
        c.executable = set()
        assert c.percentage == 100.0


class uCoverage(libpry.TestTree):
    def test_getFileDict(self):
        c = libpry.coverage.Coverage("testmodule")
        assert len(c.getFileDict("testmodule", ["testmodule/mod_one.py"])) == 4




tests = [
    uFile(),
    uCoverage(),
]
