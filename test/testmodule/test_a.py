import os
import libpry

class uOne(libpry.TestTree):
    def test_one(self):
        assert os.path.exists("mod_one.py")

    def test_two(self):
        pass


tests = [
    uOne()
]
