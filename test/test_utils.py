import libpry


class uisPathContained(libpry.TestTree):
    def test_isPathContained(self):
        assert libpry.utils.isPathContained(".", "./foo.py")
        assert libpry.utils.isPathContained("..", ".")
        assert not libpry.utils.isPathContained(".", "../foo.py")
        assert libpry.utils.isPathContained(".", ".")
        assert libpry.utils.isPathContained("../foo.py", "../foo.py")
        assert not libpry.utils.isPathContained("/bar/boo", "/bar/booboo")


#class usummariseList(libpry.TestTree):
#    def test_summariseList(self):
#        lst = [1, 2, 3, 4, 5]
#        expected = [(1, 5)]
#        self.failUnless(summariseList(lst) == expected)
#
#        lst = []
#        expected = []
#        self.failUnless(summariseList(lst) == expected)
#        
#        lst = [1]
#        expected = [1]
#        self.failUnless(summariseList(lst) == expected)
#
#        lst = [1, 2, 3, 8, 11, 12, 13, 15, 16, 17, 23]
#        expected = [(1, 3), 8, (11, 13), (15, 17), 23]
#        self.failUnless(summariseList(lst) == expected)


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
    u_splitSpec(),
    uisPathContained()
]
