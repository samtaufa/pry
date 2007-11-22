import os
import libpry

def fib(n):
    if n == 0:
        return 
    return fib(n-1)

class uOne(libpry.TestTree):
    def test_one(self):
        assert os.path.exists("mod_one.py")

    def test_two(self):
        # Trigger recursive func to make profile coverage complete.
        fib(3)


tests = [
    uOne()
]
