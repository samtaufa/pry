import libpry
import module.one

class One(libpry.AutoTree):
    def test_a(self):
        assert module.one.method() == 1
        

tests = [
    One()
]
