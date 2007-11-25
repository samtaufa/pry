
import libpry


class _Test(libpry.test.AutoTree):
    def test_one(self):
        pass

    def test_two(self):
        pass


class uSetupAll(_Test):
    def setUpAll(self):
        raise ValueError, "This is an intentional error."


class uTearDownAll(_Test):
    def tearDownAll(self):
        raise ValueError, "This is an intentional error."


class uSetup(_Test):
    def setUp(self):
        raise ValueError, "This is an intentional error."


class uTearDown(_Test):
    def tearDown(self):
        raise ValueError, "This is an intentional error."

class uTearDownOnly(libpry.test.AutoTree):
    def tearDown(self):
        raise ValueError, "This is an intentional error."

    def test_one(self):
        pass


tests = [
    uSetup(),
    uTearDown(),
    uTearDownOnly(),
    uSetupAll(),
    uTearDownAll(),
]



