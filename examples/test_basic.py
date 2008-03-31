import libpry

class MySuite(libpry.AutoTree):
    def setUpAll(self):
        self.all_fixture = True

    def tearDownAll(self):
        self.all_fixture = False

    def setUp(self):
        self.fixture = True

    def tearDown(self):
        self.fixture = False

    def test_one(self):
        assert self.fixture
        assert self.all_fixture

    def test_two(self):
        d = dict()
        libpry.raises(KeyError, d.__getitem__, "foo")

    def test_three(self):
        d = dict(foo="one")
        # This will fail:
        assert d["foo"] == "two"

tests = [
    MySuite()
]
