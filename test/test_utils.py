import pylid
from libpry.utils import *

class uisStringLike(pylid.TestCase):
    def test_all(self):
        self.failUnless(isStringLike("foo"))
        self.failIf(isStringLike([1, 2, 3]))
        self.failIf(isStringLike((1, 2, 3)))
        self.failIf(isStringLike(["1", "2", "3"]))
