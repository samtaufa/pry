import os.path, sys, pprint
import token, symbol
import libpry
import libpry.coverage
import testUnit

class uCoverage(libpry.AutoTree):
    def setUp(self):
        self.cov = libpry.coverage.Coverage("./testUnit")

    def test_run(self):
        self.cov.start()
        reload(testUnit.mymod)
        testUnit.mymod.run(1, 2)
        self.cov.stop()
        f = self.cov.fileDict[os.path.abspath("./testUnit/mymod.py")]
        assert f.executed == set([3, 4, 5, 8, 12])

    def test_docstrings(self):
        self.cov.start()
        import testUnit.docstrings
        testUnit.docstrings.foo()
        self.cov.stop()
        pth = os.path.abspath("./testUnit/docstrings.py")
        f = self.cov.fileDict[os.path.abspath(pth)]
        assert not f.notExecuted

    def test_longfuncsig(self):
        self.cov.start()
        import testUnit.longfuncsig
        testUnit.longfuncsig.foo(1)
        f = testUnit.longfuncsig.Foo()
        f.foo(1)
        self.cov.stop()
        pth = os.path.abspath("./testUnit/longfuncsig.py")
        f = self.cov.fileDict[os.path.abspath(pth)]
        assert f.executed == f.executable

    def test_longjump(self):
        self.cov.start()
        import testUnit.longjump
        testUnit.longjump.foo()
        self.cov.stop()
        pth = os.path.abspath("./testUnit/longjump.py")
        f = self.cov.fileDict[os.path.abspath(pth)]
        assert not f.notExecuted

    def test_coveragePath(self):
        """
            Make sure that only files in our coveragePath are covered.
        """
        self.cov.start()
        import testUnit.mymod
        testUnit.mymod.coveragePath()
        self.cov.stop()
        f = self.cov.fileDict[os.path.abspath("./testUnit/mymod.py")]
        assert len(f.executed) <= 2

    def test_excludePath(self):
        mycov = libpry.coverage.Coverage("./testUnit", ["./testUnit/mymod2.py"])
        mycov.start()
        import testUnit.mymod, testUnit.mymod2
        testUnit.mymod.coveragePath()
        testUnit.mymod2.coveragePath()
        mycov.stop()

        total = mycov.getGlobalStats()["statementsRun"]
        assert total == 2
        assert mycov.fileDict[os.path.abspath("./testUnit/mymod.py")].executed

    def test_matching(self):
        """
            Tests that the results of the traced running matches up with the
            file parsing.
        """
        self.cov.start()
        import testUnit.matching
        testUnit.matching.foo(1)
        testUnit.matching.foo(0)
        self.cov.stop()
        f = self.cov.fileDict[os.path.abspath("testUnit/matching.py")]
        assert f.executable == f.executed

    def test_getStats(self):
        self.cov.start()
        import testUnit.getStats, testUnit.getRanges
        reload(testUnit.getRanges)
        testUnit.getStats.foo()
        testUnit.getRanges.foo()
        self.cov.stop()

        f = self.cov.fileDict[os.path.abspath("testUnit/getStats.py")]
        assert f.numExecutable == 4
        assert f.numExecuted == 3
        assert f.percentage == 75
        assert f.notExecutedRanges == [5]

        f = self.cov.fileDict[os.path.abspath("testUnit/getRanges.py")]
        assert f.numExecutable == 12
        assert f.notExecutedRanges == [6, 9, 14]
        assert f.numExecuted == 9
        assert f.percentage == 75

    def test_getGlobalStats2(self):
        """
            Try to trigger a zero-division error
        """
        mycov = libpry.coverage.Coverage("./foo/bar")
        mycov.start()
        import testUnit.getGlobalStats2
        testUnit.getGlobalStats2.foo()
        mycov.stop()

    def test_getGlobalStats(self):
        mycov = libpry.coverage.Coverage("testUnit/getGlobalStats.py")
        mycov.start()
        reload(testUnit.getGlobalStats)
        testUnit.getGlobalStats.foo()
        mycov.stop()
        expected = {
                        'percentage': 75.0,
                        'statementsRun': 3,
                        'allStatements': 4
                    }
        x = mycov.getGlobalStats()
        assert x == expected

    def test_getRanges(self):
        self.cov.start()
        import testUnit.getRanges
        testUnit.getRanges.foo()
        self.cov.stop()
        f = self.cov.fileDict[os.path.abspath("testUnit/getRanges.py")]
        expected = [6, 9, 14]
        assert f.notExecutedRanges == expected

    def test_getAnnotation(self):
        self.cov.start()
        import testUnit.getAnnotation
        testUnit.getAnnotation.foo()
        self.cov.stop()

        f = self.cov.fileDict[os.path.abspath("testUnit/getAnnotation.py")]
        annotatedFile = open("./testUnit/getAnnotation.py.annotated").read()
        assert f.getAnnotation() == annotatedFile

    def test_coverageReport(self):
        self.cov.start()
        import testUnit.getGlobalStats
        testUnit.getGlobalStats.foo()
        self.cov.stop()
        self.cov.coverageReport()


tests = [
    uCoverage()
]
