import os.path
import libpry
import libpry.coverage

class ufileSet(libpry.TestTree):
    def test_build(self):
        s = libpry.coverage.fileSet("testmodule", [])
        assert os.path.abspath("testmodule/two/test_two.py") in s
        s = libpry.coverage.fileSet(
                "testmodule",
                [
                    os.path.abspath("testmodule/two")
                ]
            )
        assert not os.path.abspath("testmodule/two/test_two.py") in s


tests = [
    ufileSet()
]
