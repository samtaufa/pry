import libpry

class uAssertions(libpry.AutoTree):
    def test_one(self):
        a = 1
        b = 2
        assert a == b, "This is an intentional error."

    def test_two(self):
        a = "wabble\nboo"
        b = 2
        assert a == b, "This is an intentional error."

    def test_three(self):
        x = "wabble"
        assert not x != 1, "This is an intentional error."


    def test_four(self):
        x = "wabble"
        assert not (x != 1), "This is an intentional error."


tests = [
    uAssertions()
]
