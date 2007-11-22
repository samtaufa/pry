
import libpry


class _Test(libpry.test.TestTree):
    def test_one(self):
        pass

    def test_two(self):
        pass


class uSetupAll(_Test):
    def setUpAll(self):
        raise ValueError


class uTearDownAll(_Test):
    def tearDownAll(self):
        raise ValueError


class uSetup(_Test):
    def setUp(self):
        raise ValueError


class uTearDown(_Test):
    def tearDown(self):
        raise ValueError

class uTearDownOnly(libpry.test.TestTree):
    def tearDown(self):
        raise ValueError

    def test_one(self):
        pass


tests = [
    uSetup(),
    uTearDown(),
    uTearDownOnly(),
    uSetupAll(),
    uTearDownAll(),
]



