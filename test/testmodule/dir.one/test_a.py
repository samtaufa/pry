import os
import libpry

class uOne(libpry.AutoTree):
    def test_one(self):
        assert os.path.exists("mod_one.py")

    def test_two(self):
        pass


tests = [
    uOne()
]
