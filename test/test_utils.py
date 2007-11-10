import pylid
from libpry import utils

class uisStringLike(pylid.TestCase):
    def test_all(self):
        self.failUnless(utils.isStringLike("foo"))
        self.failIf(utils.isStringLike([1, 2, 3]))
        self.failIf(utils.isStringLike((1, 2, 3)))
        self.failIf(utils.isStringLike(["1", "2", "3"]))

class u_splitSpec(pylid.TestCase):
    def test_simple(self):
        assert utils._splitSpec("foo") == ('', "foo")
        assert utils._splitSpec("foo.bar") == ('', "foo.bar")
        
    def test_dir(self):
        assert utils._splitSpec("testmodule") == ('testmodule', "")
        assert utils._splitSpec("testmodule.foo") == ('testmodule', "foo")
        assert utils._splitSpec("testmodule/dir.one") == ('testmodule/dir.one', "")
        assert utils._splitSpec("testmodule/dir.one.foo") ==\
                    ('testmodule/dir.one', "foo")

    def test_file(self):
        assert (
                    utils._splitSpec("testmodule/test_a") ==\
                    ('testmodule/test_a.py', "")
                )
        assert (
                    utils._splitSpec("testmodule/dir.one") ==\
                    ('testmodule/dir.one', "")
                )
        assert (
                    utils._splitSpec("testmodule/dir.one/test_a") ==\
                    ('testmodule/dir.one/test_a.py', "")
                )
        assert (
                    utils._splitSpec("testmodule/dir.one/test_a.pattern") ==\
                    ('testmodule/dir.one/test_a.py', "pattern")
                )
