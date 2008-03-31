import libpry

class MyContainer(libpry.TestContainer):
    def setUpAll(self):
        print "setUpAll"

    def tearDownAll(self):
        print "tearDownAll"

    def setUp(self):
        print "\tsetUp"

    def tearDown(self):
        print "\ttearDown"

class MyTest(libpry.Test):
    def __call__(self):
        print "\t\t%s..."%self.name

tests = [
    MyContainer(), [
        MyTest("test_one"),
        MyTest("test_two"),
    ]
]
