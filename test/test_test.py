import fnmatch, cStringIO, os
import pylid
import libpry


zero = libpry.test._Output(0)


class TSetupCheckRoot(libpry.TestTree):
    def __init__(self, *args, **kwargs):
        libpry.TestTree.__init__(self, *args, **kwargs)
        self.log = []


class TSetupCheck(libpry.TestTree):
    def __init__(self, *args, **kwargs):
        libpry.TestTree.__init__(self, *args, **kwargs)

    def setUp(self):
        self.getTopNode().log.append("setup_%s"%self.name)

    def tearDown(self):
        self.getTopNode().log.append("teardown_%s"%self.name)


class TSetupCheckNodes(TSetupCheck):
    def __init__(self, *args, **kwargs):
        TSetupCheck.__init__(self, *args, **kwargs)

    def test_a(self):
        self.getTopNode().log.append("test_a")

    def test_b(self):
        self.getTopNode().log.append("test_b")


class _SetupAllCheck(libpry.TestTree):
    def setUp(self):
        self.getTopNode().log.append("setUp")

    def tearDown(self):
        self.getTopNode().log.append("tearDown")

    def test_a(self):
        self.getTopNode().log.append("test_a")

    def test_b(self):
        self.getTopNode().log.append("test_b")


class TSetupAllCheck(_SetupAllCheck):
    def setUpAll(self):
        self.getTopNode().log.append("setupAll")


class TTeardownAllCheck(_SetupAllCheck):
    def tearDownAll(self):
        self.getTopNode().log.append("tearDownAll")


class TSubTree(libpry.TestTree):
    name = "sub"
    def test_fail(self): assert False
    def test_error (self): raise ValueError


class TTree(libpry.TestTree):
    def __init__(self, *args, **kwargs):
        libpry.TestTree.__init__(self, *args, **kwargs)
        self.addChild(TSubTree())
        self["item"] = "data"

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_pass(self): pass


def errFunc(): assert None


class TSetupFailure(libpry.TestTree):
    def setUp(self): raise ValueError
    def test_pass(self): pass


class TTeardownFailure(libpry.TestTree):
    def tearDown(self): raise ValueError
    def test_pass(self): pass


class uSetupCheck(pylid.TestCase):
    def setUp(self):
        self.t =  TSetupCheckRoot(
            [
                TSetupCheck(name="one"), [
                    TSetupCheckNodes(name="two"),
                    TSetupCheckNodes(name="three"),
                ]
            ]
        )

    def test_all(self):
        self.t.run(zero)
        v = ['setup_one', 'setup_two', 'test_a', 'teardown_two', 'setup_two',
        'test_b', 'teardown_two', 'teardown_one', 'setup_one', 'setup_three',
        'test_a', 'teardown_three', 'setup_three', 'test_b', 'teardown_three',
        'teardown_one']
        assert self.t.log == v

    def test_mark_multi(self):
        self.t.mark("test_a")
        self.t.run(zero)
        v = ['setup_one', 'setup_two', 'test_a', 'teardown_two',
        'teardown_one', 'setup_one', 'setup_three', 'test_a', 'teardown_three',
        'teardown_one']
        assert self.t.log == v

    def test_mark_single(self):
        self.t.mark("two.test_a")
        self.t.run(zero)
        v = ['setup_one', 'setup_two', 'test_a', 'teardown_two', 'teardown_one']
        assert self.t.log == v


class uTestTree(pylid.TestCase):
    def setUp(self):
        self.t = TTree()

    def test_autoadd(self):
        assert self.t.count() == 5
        assert len(self.t.tests()) == 3
        assert len(self.t.notrun()) == 3

    def test_hasTests(self):
        assert self.t.hasTests()
        t  = TSetupCheckRoot()
        assert not t.hasTests()

    def test_hasTests(self):
        assert self.t.hasTests()
        t  = TSetupCheckRoot()
        assert not t.hasTests()

    def test_prune(self):
        t = TSetupCheckRoot(
                [
                    TSetupCheckRoot()
                ]
            )
        t.prune()
        assert t.count() == 1
        c = self.t.count()
        self.t.prune()
        assert self.t.count() == c

    def test_printStructure(self):
        s = cStringIO.StringIO()
        self.t.printStructure(s)
        assert s.getvalue()

    def test_mark(self):
        self.t.mark("test_pass")
        selected = [i for i in self.t.preOrder() if i._selected]
        assert len(selected) == 2

        self.t.mark("test_fail")
        selected = [i for i in self.t.preOrder() if i._selected]
        assert len(selected) == 3

        self.t.mark("sub")
        selected = [i for i in self.t.preOrder() if i._selected]
        assert len(selected) == 4

        self.t.mark("nonexistent")
        selected = [i for i in self.t.preOrder() if i._selected]
        assert len(selected) == 0

    def test_run(self):
        self.t.run(zero)
        assert len(self.t.passed()) == 1
        assert len(self.t.notrun()) == 0
        assert isinstance(self.t.children[0].setupState, libpry.OK)
        assert isinstance(self.t.children[0].teardownState, libpry.OK)

    def test_run_marked(self):
        self.t.mark("sub")
        self.t.run(zero)
        assert len(self.t.passed()) == 0

    def test_getitem(self):
        n = self.t.search("test_pass")[0]
        assert n["item"] == "data"
        self.failUnlessRaises(KeyError, n.__getitem__, "nonexistent")

    def test_setupFailure(self):
        t = TSetupFailure()
        t.run(zero)
        assert isinstance(t.children[0].setupState, libpry.Error)
        assert len(t.notrun()) == 1

    def test_setupFailure(self):
        t = TTeardownFailure()
        t.run(zero)
        assert isinstance(t.children[0].teardownState, libpry.Error)
        assert len(t.notrun()) == 0

    def test_getPath(self):
        t = libpry.TestTree(name="one")
        assert t.fullPath() == "one"
        t2 = libpry.TestTree(name="two")
        t.addChild(t2)
        assert t2.fullPath() == "one.two"

        t3 = libpry.TestTree()
        t.addChild(t3)
        t4 = libpry.TestTree(name="four")
        t3.addChild(t4)
        assert t4.fullPath() == "one.TestTree.four"

    def test_search(self):
        t = libpry.TestTree(
            [
                libpry.TestTree(name="one"), [
                    libpry.TestTree(name="a"),
                    libpry.TestTree(name="b"),
                    libpry.TestTree(name="one"),
                ],
                libpry.TestTree(name="two"), [
                    libpry.TestTree(name="b"),
                ],
                libpry.TestTree(name="three"),
            ]
        )
        r = t.search("one")
        assert len(r) == 1
        assert r[0].name == "one"

        r = t.search("a")
        assert len(r) == 1

        r = t.search("b")
        assert len(r) == 2

        r = t.search("nonexistent")
        assert len(r) == 0

    def test_setupAll(self):
        t = TSetupCheckRoot(
                [
                    TSetupAllCheck()
                ]
            )
        t.run(zero)
        expected = [
                     'setupAll', 'setUp',
                     'test_a', 'tearDown',
                     'setUp', 'test_b',
                     'tearDown'
                   ]
        assert t.log == expected

    def test_teardownAll(self):
        t = TSetupCheckRoot(
                [
                    TTeardownAllCheck()
                ]
            )
        t.run(zero)
        expected = [
                     'setUp', 'test_a','tearDown',
                     'setUp', 'test_b', 'tearDown',
                     'tearDownAll'
                   ]
        assert t.log == expected


class uDirNode(pylid.TestCase):
    def setUp(self):
        self.cwd = os.getcwd()

    def tearDown(self):
        os.chdir(self.cwd)
        
    def test_init(self):
        self.d = libpry.DirNode("testmodule")
        assert len(self.d.search("test_one")) == 2

    def test_run(self):
        self.d = libpry.DirNode("testmodule")
        self.d.run(zero)


class uRootNode(pylid.TestCase):
    def test_init(self):
        r = libpry.RootNode("testmodule", True)
        assert r.search("test_one")
        assert r.search("testmodule/test_a.uOne.test_one")
        assert r.search("testmodule/two/test_two")
        assert not r.search("nonexistent")

        r = libpry.RootNode("testmodule", False)
        assert not r.search("testmodule/two/test_two")
        assert r.search("test_one")

        

class uTestNode(pylid.TestCase):
    def test_run_error(self):
        t = TTree()
        x = t.search("test_fail")[0]
        x.run(zero)
        assert isinstance(x.runState, libpry.Error)
        str(x.runState)

    def test_run_pass(self):
        t = TTree()
        x = t.search("test_pass")[0]
        x.run(zero)
        assert isinstance(x.runState, libpry.OK)

    def test_call(self):
        t = libpry.TestNode("name")
        self.failUnlessRaises(NotImplementedError, t)


class uOutput(pylid.TestCase):
    def setUp(self):
        self.t = TTree()
        self.node = self.t.search("test_pass")[0]
        self.s = cStringIO.StringIO()

    def test_zero(self):
        o = libpry.test._OutputZero()
        assert not o.nodePre(self.node)
        assert not o.nodeError(self.node)

    def test_one(self):
        o = libpry.test._OutputOne()
        assert o.nodeError(self.node) == "E"

    def test_two(self):
        o = libpry.test._OutputTwo()
        assert "test_pass" in o.nodePre(self.node)
        assert o.nodeError(self.node) == "FAIL\n"

    def test_three(self):
        o = libpry.test._OutputThree()
        assert "test_pass" in o.nodePre(self.node)
        assert o.nodeError(self.node) == "FAIL\n"

#    def test_verbosity0(self):
#        s = cStringIO.StringIO()
#        n = libpry.TestWrapper("myname", lambda: None)
#        n.run(0, s)
#        assert not s.getvalue()
#
#    def test_verbosity1(self):
#        s = cStringIO.StringIO()
#        n = libpry.TestWrapper("myname", errFunc)
#        n.run(1, s)
#        assert "E" in s.getvalue()
#
#        s = cStringIO.StringIO()
#        n = libpry.TestWrapper("myname", lambda: None)
#        n.run(1, s)
#        assert "." in s.getvalue()
#
#    def test_verbosity2(self):
#        s = cStringIO.StringIO()
#        n = libpry.TestWrapper("myname", errFunc)
#        n.run(2, s)
#        assert "FAIL" in s.getvalue()
#
#        s = cStringIO.StringIO()
#        n = libpry.TestWrapper("myname", lambda: None)
#        n.run(2, s)
#        assert "PASS" in s.getvalue()
#
#    def test_verbosity3(self):
#        s = cStringIO.StringIO()
#        n = libpry.TestWrapper("myname", errFunc)
#        n.run(3, s)
#        assert "FAIL" in s.getvalue()
#
#        s = cStringIO.StringIO()
#        n = libpry.TestWrapper("myname", lambda: None)
#        n.run(3, s)
#        assert "PASS" in s.getvalue()
#        assert "s)" in s.getvalue()
