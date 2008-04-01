import libpry
import module.two

class Two(libpry.AutoTree):
    def test_a(self):
        assert module.two.method() == 1

tests = [
    Two()
]
