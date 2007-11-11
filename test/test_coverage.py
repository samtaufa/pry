import os.path, sys, pprint
import token, symbol
import libpry
import libpry.coverage
import testUnit

class uCoverage(libpry.TestTree):
    def setUp(self):
        self.cov = libpry.coverage.Coverage("./testUnit")

    def test_run(self):
        self.cov.start()
        reload(testUnit.mymod)
        testUnit.mymod.run(1, 2)
        self.cov.stop()
        self.cov._integrateTrace()
        linesrun = self.cov.linesRun[os.path.abspath("./testUnit/mymod.py")]
        assert linesrun == set([3, 4, 5, 8, 12])

    def test_docstrings(self):
        self.cov.start()
        import testUnit.docstrings
        testUnit.docstrings.foo()
        self.cov.stop()
        self.cov._makeCoverage()
        self.cov._integrateTrace()
        pth = os.path.abspath("./testUnit/docstrings.py")
        assert not self.cov.statementsNotRun[pth]

    def test_coveragePath(self):
        """
            Make sure that only files in our coveragePath are covered.
        """
        self.cov.start()
        import testUnit.mymod
        testUnit.mymod.coveragePath()
        self.cov.stop()
        self.cov._integrateTrace()
        assert len(self.cov.linesRun) <= 2
        assert self.cov.linesRun.has_key(
                os.path.abspath("./testUnit/mymod.py")
            )

    def test_excludePath(self):
        mycov = libpry.coverage.Coverage("./testUnit", ["./testUnit/mymod2.py"])
        mycov.start()
        import testUnit.mymod, testUnit.mymod2
        testUnit.mymod.coveragePath()
        testUnit.mymod2.coveragePath()
        mycov.stop()
        mycov._makeCoverage()
        assert len(mycov.linesRun) == 1
        assert mycov.linesRun.has_key(os.path.abspath("./testUnit/mymod.py"))
        assert len(mycov.allStatements) == 1
        assert mycov.allStatements.has_key(os.path.abspath("./testUnit/mymod.py"))

    def test_makeCoverage(self):
        self.cov.start()
        import testUnit.makeCoverage
        testUnit.makeCoverage.foo()
        self.cov.stop()
        self.cov._makeCoverage()
        expected = {
            os.path.abspath("./testUnit/makeCoverage.py"): [6, 12, 17, 18, 22],
        }
        assert self.cov.statementsNotRun == expected

    def test_makeCoverageReentry(self):
        import testUnit.makeCoverageReentry2

        self.cov.start()
        import testUnit.makeCoverageReentry
        testUnit.makeCoverageReentry.foo()
        testUnit.makeCoverageReentry.bar()
        self.cov.stop()

        self.cov._makeCoverage()
        expected = {os.path.abspath("./testUnit/makeCoverageReentry.py"): []}
        assert self.cov.statementsNotRun == expected

        self.cov.start()
        import testUnit.makeCoverageReentry2
        testUnit.makeCoverageReentry2.foo()
        self.cov.stop()

        self.cov._makeCoverage()
        expected = {
                        os.path.abspath("./testUnit/makeCoverageReentry.py"): [],
                        os.path.abspath("./testUnit/makeCoverageReentry2.py"): [3, 4]
                        
                    }
        assert self.cov.statementsNotRun == expected

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
        self.cov._makeCoverage()
        assert self.cov.statementsRun == self.cov.allStatements

    def test_getStats(self):
        self.cov.start()
        import testUnit.getStats, testUnit.getRanges
        testUnit.getStats.foo()
        testUnit.getRanges.foo()
        self.cov.stop()
        expected = [
                (os.path.abspath("./testUnit/getStats.py"), {
                                            "allStatements": 4,
                                            "statementsRun": 3,
                                            "coverage": 75.0,
                                            "ranges": [5],
                                        }),
                (os.path.abspath("./testUnit/getRanges.py"), {
                                            "allStatements": 12,
                                            "statementsRun":9,
                                            "coverage": 75.0,
                                            "ranges": [6, 9, 14],
                                        })
        ]
        assert self.cov.getStats() == expected

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
        self.cov.start()
        import testUnit.getGlobalStats
        testUnit.getGlobalStats.foo()
        self.cov.stop()
        expected = {
                        'percentage': 75.0,
                        'statementsRun': 3,
                        'allStatements': 4
                    }
        x = self.cov.getGlobalStats()
        assert x == expected

    def _test_getRanges(self):
        self.cov.start()
        import testUnit.getRanges
        testUnit.getRanges.foo()
        self.cov.stop()
        expected = {
                       "./testUnit/getRanges.py": [(15, 22), 28, (34, 39)]
                    }
        assert self.cov.getRanges() == expected

    def test_getAnnotation(self):
        self.cov.start()
        import testUnit.getAnnotation
        testUnit.getAnnotation.foo()
        self.cov.stop()
        ann = self.cov.getAnnotation()
        annotatedFile = open("./testUnit/getAnnotation.py.annotated").readlines()
        assert len(ann) == 1
        
        x = ann[os.path.abspath("./testUnit/getAnnotation.py")]
        assert x == annotatedFile

tests = [
    uCoverage()
]
