import libpry

class MySuite(libpry.AutoTree):
    def setUpAll(self):
        pass

    def tearDownAll(self):
        pass

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_one(self):
        assert True

    def test_two(self):
        d = dict()
        libpry.raises(KeyError, d.__getitem__, "foo")

    def test_three(self):
        d = dict(foo="one")
        assert d["foo"] == "two"
           
tests = [
    MySuite()
]
