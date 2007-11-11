import libpry

class uisStringLike(libpry.TestTree):
    def test_all(self):
        assert libpry.utils.isStringLike("foo")
        assert not libpry.utils.isStringLike([1, 2, 3])
        assert not libpry.utils.isStringLike((1, 2, 3))
        assert not libpry.utils.isStringLike(["1", "2", "3"])

class u_splitSpec(libpry.TestTree):
    def test_simple(self):
        assert libpry.utils._splitSpec("foo") == ('', "foo")
        assert libpry.utils._splitSpec("foo.bar") == ('', "foo.bar")
        
    def test_dir(self):
        assert libpry.utils._splitSpec("testmodule") == ('testmodule', "")
        assert libpry.utils._splitSpec("testmodule.foo") == ('testmodule', "foo")
        assert libpry.utils._splitSpec("testmodule/dir.one") ==\
                    ('testmodule/dir.one', "")
        assert libpry.utils._splitSpec("testmodule/dir.one.foo") ==\
                    ('testmodule/dir.one', "foo")

    def test_file(self):
        assert (
                    libpry.utils._splitSpec("testmodule/test_a") ==\
                    ('testmodule/test_a.py', "")
                )
        assert (
                    libpry.utils._splitSpec("testmodule/dir.one") ==\
                    ('testmodule/dir.one', "")
                )
        assert (
                    libpry.utils._splitSpec("testmodule/dir.one/test_a") ==\
                    ('testmodule/dir.one/test_a.py', "")
                )
        assert (
                    libpry.utils._splitSpec("testmodule/dir.one/test_a.pattern") ==\
                    ('testmodule/dir.one/test_a.py', "pattern")
                )
        assert (
                    libpry.utils._splitSpec("testmodule/test_a.py") ==\
                    ('testmodule/test_a.py', "")
                )


tests = [
    uisStringLike(),
    u_splitSpec()
]
