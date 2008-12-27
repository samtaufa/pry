import libpry

class MyContainer(libpry.AutoTree):
    def setUpAll(self):
        print("setUpAll")

    def tearDownAll(self):
        print("tearDownAll")

    def setUp(self):
        print("\tsetUp")

    def tearDown(self):
        print("\ttearDown")

    def test_one(self):
        print("\t\t%s..."%self.name)

    def test_two(self):
        print("\t\t%s..."%self.name)

tests = [
    MyContainer()
]
