import fnmatch, cStringIO, os, shutil
import libpry.test
import libpry.helpers

zero = libpry.test._Output(libpry.test._RootNode(False, None), 0)

class TSetupCheckRoot(libpry.test.AutoTree):
    def __init__(self, *args, **kwargs):
        libpry.test.AutoTree.__init__(self, *args, **kwargs)
        self.log = []


class TSetupCheck(libpry.test.AutoTree):
    def __init__(self, *args, **kwargs):
        libpry.test.AutoTree.__init__(self, *args, **kwargs)

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


class _SetupAllCheck(libpry.test.AutoTree):
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
        self.getTopNode().log.append("setUpAll")


class TSetupAllError(_SetupAllCheck):
    def setUpAll(self):
        raise ValueError, "test"


class TTearDownAllError(_SetupAllCheck):
    def tearDownAll(self):
        raise ValueError, "test"


class TTeardownAllCheck(_SetupAllCheck):
    def tearDownAll(self):
        self.getTopNode().log.append("tearDownAll")


class TSubTree(libpry.test.AutoTree):
    name = "sub"
    def test_fail(self): assert False
    def test_error (self): raise ValueError


class TTree(libpry.test.AutoTree):
    def __init__(self, *args, **kwargs):
        libpry.test.AutoTree.__init__(self, *args, **kwargs)
        self.addChild(TSubTree())
        self["item"] = "data"

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_pass(self): pass


def errFunc(): assert None


class TSetupFailure(libpry.test.AutoTree):
    def setUp(self): raise ValueError
    def test_pass(self): pass
    def test_pass2(self): pass


class TTeardownFailure(libpry.test.AutoTree):
    def tearDown(self): raise ValueError
    def test_pass(self): pass


class uError(libpry.test.AutoTree):
    def test_exc(self):
        try:
            raise ValueError
        except:
            pass
        Error(None, None)


class uSetupCheck(libpry.test.AutoTree):
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
        # Needed to make test succeed with -b N, for N > 1
        self.t.log = []
        self.t.run(zero, 1, None)
        v = ['setup_one', 'setup_two', 'test_a', 'teardown_two', 'setup_two',
        'test_b', 'teardown_two', 'teardown_one', 'setup_one', 'setup_three',
        'test_a', 'teardown_three', 'setup_three', 'test_b', 'teardown_three',
        'teardown_one']
        assert self.t.log == v

    def test_bench(self):
        self.t.log = []
        self.t.mark("two.test_a")
        self.t.prune()
        self.t.run(zero, 10, None)
        assert self.t.log.count("test_a") == 10

    def test_mark_multi(self):
        # Needed to make test succeed with -b N, for N > 1
        self.t.log = []
        self.t.mark("test_a")
        self.t.prune()
        self.t.run(zero, 1, None)
        v = ['setup_one', 'setup_two', 'test_a', 'teardown_two',
        'teardown_one', 'setup_one', 'setup_three', 'test_a', 'teardown_three',
        'teardown_one']
        assert self.t.log == v

    def test_mark_single(self):
        # Needed to make test succeed with -b N, for N > 1
        self.t.log = []
        self.t.mark("two.test_a")
        self.t.prune()
        self.t.run(zero, 1, None)
        v = ['setup_one', 'setup_two', 'test_a', 'teardown_two', 'teardown_one']
        assert self.t.log == v


class uAutoTree(libpry.test.AutoTree):
    def setUp(self):
        self.t = TTree()

    def test_autoadd(self):
        assert self.t.count() == 5
        assert len(self.t.tests()) == 3
        assert len(self.t.allNotRun()) == 3

    def test_allSkipped(self):
        assert len(self.t.allSkip()) == len(self.t.tests())
        x = self.t.search("TTree.test_pass")[0]
        assert len(x.allSkip()) == 2
        x = self.t.search("sub")[0]
        assert len(x.allSkip()) == 2
        x = self.t.search("test_error")[0]
        assert len(x.allSkip()) == 1
        x = self.t.search("test_fail")[0]
        assert len(x.allSkip()) == 0

    def test_maxPathLen(self):
        assert self.t.maxPathLen() == 20

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
        self.t.run(zero, 1, None)
        assert not self.t.hasProfStats()
        assert len(self.t.allPassed()) == 1
        assert len(self.t.allNotRun()) == 0
        assert len(self.t.allError()) == 2
        assert isinstance(self.t.children[0].setUpState, libpry.test.OK)
        assert not self.t.children[0].isError()
        assert isinstance(self.t.children[0].tearDownState, libpry.test.OK)

    def test_run_profile(self):
        self.t.run(zero, 1, "calls")
        assert self.t.hasProfStats()
        assert len(self.t.allPassed()) == 1
        assert len(self.t.allNotRun()) == 0
        assert len(self.t.allError()) == 2
        assert isinstance(self.t.children[0].setUpState, libpry.test.OK)
        assert not self.t.children[0].isError()
        assert isinstance(self.t.children[0].tearDownState, libpry.test.OK)

    def test_run_marked(self):
        self.t.mark("sub")
        self.t.prune()
        self.t.run(zero, 1, None)
        assert len(self.t.allPassed()) == 0

    def test_getitem(self):
        n = self.t.search("test_pass")[0]
        assert n["item"] == "data"
        libpry.helpers.raises(KeyError, n.__getitem__, "nonexistent")

    def test_setupFailure(self):
        t = TSetupFailure()
        t.run(zero, 1, None)
        assert isinstance(t.children[0].setUpState, libpry.test.Error)
        assert t.children[0].isError()
        assert len(t.allNotRun()) == 1

    def test_setupFailure2(self):
        t = TTeardownFailure()
        t.run(zero, 1, None)
        assert isinstance(t.children[0].tearDownState, libpry.test.Error)
        assert len(t.allNotRun()) == 0

    def test_getPath(self):
        t = libpry.test.AutoTree(name="one")
        assert t.fullPath() == "one"
        t2 = libpry.test.AutoTree(name="two")
        t.addChild(t2)
        assert t2.fullPath() == "one.two"

        t3 = libpry.test.AutoTree()
        t.addChild(t3)
        t4 = libpry.test.AutoTree(name="four")
        t3.addChild(t4)
        assert t4.fullPath() == "one.AutoTree.four"

    def test_search(self):
        t = libpry.test.AutoTree(
            [
                libpry.test.AutoTree(name="one"), [
                    libpry.test.AutoTree(name="a"),
                    libpry.test.AutoTree(name="b"),
                    libpry.test.AutoTree(name="one"),
                ],
                libpry.test.AutoTree(name="two"), [
                    libpry.test.AutoTree(name="b"),
                ],
                libpry.test.AutoTree(name="three"),
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

    def test_setUpAll(self):
        t = TSetupCheckRoot(
                [
                    TSetupAllCheck()
                ]
            )
        t.run(zero, 1, None)
        expected = [
                     'setUpAll', 'setUp',
                     'test_a', 'tearDown',
                     'setUp', 'test_b',
                     'tearDown'
                   ]
        assert t.log == expected

    def test_isError_setUpAll(self):
        t = TSetupCheckRoot(
                [
                    TSetupAllError()
                ]
            )
        assert not t.children[0].isError()
        t.run(zero, 1, None)
        assert t.children[0].isError()

    def test_isError_tearDownAll(self):
        t = TSetupCheckRoot(
                [
                    TTearDownAllError()
                ]
            )
        x = t.children[0]
        assert not x.isError()
        t.run(zero, 1, None)
        assert x.isError()

    def test_getError(self):
        t = TSetupCheckRoot(
                [
                    TSetupAllError()
                ]
            )
        x = t.children[0]
        libpry.helpers.raises("no error for this node", x.getError)
        t.run(zero, 1, None)
        assert x.getError()

    def test_teardownAll(self):
        t = TSetupCheckRoot(
                [
                    TTeardownAllCheck()
                ]
            )
        t.run(zero, 1, None)
        expected = [
                     'setUp', 'test_a','tearDown',
                     'setUp', 'test_b', 'tearDown',
                     'tearDownAll'
                   ]
        assert t.log == expected


class u_DirNode(libpry.test.AutoTree):
    def setUp(self):
        self.cwd = os.getcwd()
        self.d = libpry.test._DirNode("testmodule", False)

    def tearDown(self):
        os.chdir(self.cwd)
        
    def test_init(self):
        assert len(self.d.search("test_one")) == 2

    def test_init(self):
        d = libpry.test._DirNode("testmodule/test_a.py", False)
        assert len(d.search("test_one")) == 1

    def test_nocover(self):
        d = libpry.test._DirNode("testmodule/nocover", True)
        assert d.coverage == False

    def test_run(self):
        self.d.run(zero, 1, None)

    def test_repr(self):
        repr(self.d)


class u_RootNode(libpry.test.AutoTree):
    def test_init(self):
        r = libpry.test._RootNode(False, None)
        r.addPath("testmodule", True)
        assert r.search("test_one")
        assert r.search("testmodule/test_a.uOne.test_one")
        assert r.search("testmodule/two/test_two")
        assert not r.search("nonexistent")

        r = libpry.test._RootNode(False, None)
        r.addPath("testmodule", False)
        assert not r.search("testmodule/two/test_two")
        assert r.search("test_one")

    def test_errFinal(self):
        try:
            raise ValueError
        except:
            pass
        r = libpry.test._RootNode(False, None)
        o = libpry.test._OutputOne(r)
        r.goState = libpry.test.Error(r, "")
        o.final(r)


class FullTree(libpry.test.AutoTree):
    dirs = [".", "two", "dir.one", "nocover", "assertiondemo"]
    def setUp(self):
        for i in self.dirs:
            shutil.copy(
                os.path.join("testmodule", i, ".pry.inactive"),
                os.path.join("testmodule", i, ".pry"),
            )
        r = libpry.test._RootNode(False, None)
        r.addPath("testmodule", True)
        self["root"] = r
        self["node"] = r.search("test_one")[0]

        c = libpry.test._RootNode(libpry.test.DUMMY, None)
        c.addPath("testmodule", True)
        c.run(zero, 1)
        self["coverageRoot"] = c

        c = libpry.test._RootNode(False, "calls")
        c.addPath("testmodule", True)
        c.run(zero, 1)
        self["profileRoot"] = c

    def tearDown(self):
        for i in self.dirs:
            os.unlink(os.path.join("testmodule", i, ".pry"))


class uOutput(libpry.test.AutoTree):
    def __init__(self, outputClass):
        libpry.test.AutoTree.__init__(self, name=outputClass.__name__)
        self.outputClass = outputClass

    def setUp(self):
        self.output = self.outputClass(self["root"])
        self.coverageOutput = self.outputClass(self["coverageRoot"])
        self.profileOutput = self.outputClass(self["profileRoot"])

    def test_run(self):
        self["root"].run(self.output, 1)
        self["coverageRoot"].run(self.coverageOutput, 1)
        self["profileRoot"].run(self.profileOutput, 1)

    def test_final(self):
        self["root"].run(self.output, 1)
        self["coverageRoot"].run(self.coverageOutput, 1)
        self["profileRoot"].run(self.profileOutput, 1)
        self.output.final(self["root"])
        self.output.final(self["coverageRoot"])
        self.output.final(self["profileRoot"])

    
class uTestNode(libpry.test.AutoTree):
    def test_run_error(self):
        t = TTree()
        x = t.search("test_fail")[0]
        assert x.run(zero, 1, None)

    def test_run_pass(self):
        t = TTree()
        x = t.search("test_pass")[0]
        x.run(zero, 1, None)
        assert isinstance(x.callState, libpry.test.OK)

    def test_call(self):
        t = libpry.test.TestNode("name")
        libpry.helpers.raises(NotImplementedError, t)


class u_Output(libpry.test.AutoTree):
    def test_construct(self):
        r = libpry.test._RootNode(False, None)
        o = libpry.test._Output(r, 0)
        assert isinstance(o.o, libpry.test._OutputZero)

        o = libpry.test._Output(r, 1)
        assert isinstance(o.o, libpry.test._OutputOne)

        o = libpry.test._Output(r, 2)
        assert isinstance(o.o, libpry.test._OutputTwo)

        o = libpry.test._Output(r, 3)
        assert isinstance(o.o, libpry.test._OutputThree)

        o = libpry.test._Output(r, 999)
        assert isinstance(o.o, libpry.test._OutputThree)



class uFileNode(libpry.test.AutoTree):
    def test_repr(self):
        n = self["root"].search("testmodule/test_a")[0]
        repr(n)


class uCallableNode(libpry.test.AutoTree):
    def test_repr(self):
        def x(): pass
        t = libpry.test.CallableNode("foo", x)
        repr(t)


tests = [
    uSetupCheck(),
    FullTree(), [
        uOutput(libpry.test._OutputZero),
        uOutput(libpry.test._OutputOne),
        uOutput(libpry.test._OutputTwo),
        uOutput(libpry.test._OutputThree),
        uFileNode(),
        u_RootNode(),
        u_DirNode(),
    ],
    uTestNode(),
    uAutoTree(),
    u_Output(),
    uCallableNode(),
]
