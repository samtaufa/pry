import dis
import os.path
import libpry
import libpry.coverage


class uFile(libpry.AutoTree):
    def test_extractLineOffsets(self):
        f = libpry.coverage.File(None)
        offsets = [
            #byte    line
            chr(0), chr(1),
            chr(1), chr(1),
            chr(7), chr(255),
            chr(0), chr(10),
            chr(1), chr(1),
        ]
        offets = "".join(offsets)
        expected = [1, 1, 265, 1]
        assert f._extractLineOffsets(offsets) == expected

        offsets = [
            #byte    line
            chr(0), chr(255),
            chr(0), chr(10),
            chr(1), chr(1),
        ]
        offets = "".join(offsets)
        expected = [265, 1]
        assert f._extractLineOffsets(offsets) == expected

        offsets = [
            #byte    line
            chr(1), chr(1),
            chr(0), chr(255),
        ]
        offets = "".join(offsets)
        expected = [1, 255]
        assert f._extractLineOffsets(offsets) == expected

    def test_getLines(self):
        f = libpry.coverage.File(None)
        fname = "covfiles/linenos.py"
        d = open(fname).read()
        code = compile(d, fname, "exec")
        l = f.getLines(code)
        assert l == set([2, 3, 4, 5, 6, 8])

    def test_getLines_empty(self):
        f = libpry.coverage.File(None)
        fname = "covfiles/empty.py"
        d = open(fname).read()
        code = compile(d, fname, "exec")
        l = f.getLines(code)
        assert l == set([])

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
        f.path = os.path.sep[0] + os.path.join("foo", "bar.py")
        assert f.nicePath(os.path.sep[0] + "foo") == "bar.py"
        assert f.nicePath(f.path) == "bar.py"

    def test_cmp(self):
        f1 = libpry.coverage.File(os.path.join("testmodule", "test_a.py"))
        f2 = libpry.coverage.File(os.path.join("testmodule", "test_a.py"))
        f1.executed.add(f1.executable.pop())
        assert cmp(f1, f2)

    def test_annotated(self):
        f = libpry.coverage.File(os.path.join("testmodule", "test_a.py"))
        assert f.getAnnotation()

    def test_stats(self):
        c = libpry.coverage.File(None)
        c.executable = set([1, 2, 3, 4])
        c.executed = set([1, 2])
        c.exclusions = set([])
        assert c.numExecutable == 4
        assert c.numExecuted == 2
        assert c.notExecuted == set([3, 4])
        assert c.percentage == 50.0
        assert c.notExecutedRanges == [(3, 4)]
        c.executable = set()
        assert c.percentage == 100.0

    def test_prettyRanges(self):
        c = libpry.coverage.File(None)
        out = c.prettyRanges([1, 2, (3, 4)], 1, 5)
        assert out == ' 1 2\n [3...4]'
        
        out = c.prettyRanges([1, 2, 3, 4], 1, 5)
        assert out == ' 1 2\n 3 4'

        out = c.prettyRanges([11111, 22222, 33333], 1, 5)
        assert out == ' 11111\n 22222\n 33333'


class uCoverage(libpry.AutoTree):
    def setUp(self):
        self.c = libpry.coverage.Coverage("testmodule")

    def test_getFileDict(self):
        assert len(self.c.getFileDict("testmodule", ["testmodule/mod_one.py"])) == 7
        r = self.c.getFileDict("testmodule/mod_one.py", [])
        assert len(r) == 1

    def test_coverageReport(self):
        assert self.c.coverageReport()

    def test_getGlobalStats(self):
        assert self.c.getGlobalStats()

    def test_getGlobalStats_empty(self):
        c = libpry.coverage.Coverage("nonexistent")
        assert c.getGlobalStats()


tests = [
    uFile(),
    uCoverage(),
]
