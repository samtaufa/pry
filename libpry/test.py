"""
    A tree-based unit test system.

    Each test is a node in a tree of tests. Each test can have a setUp and
    tearDown method - these get run before and after each child node is run.
"""
import sys, time, traceback, os, fnmatch, config, cProfile, pstats, cStringIO
import linecache, shutil, tempfile
import _tinytree, explain, coverage

_TestGlob = "test_*.py"

class TmpDirMixin:
    def setUp(self):
        self["tmpdir"] = tempfile.mkdtemp()

    def tearDown(self):
        if os.path.isdir(self["tmpdir"]):
            shutil.rmtree(self["tmpdir"])


class Error:
    """
        Error tests False.
    """
    def __init__(self, node, msg):
        self.node, self.msg = node, msg
        self.exctype, self.excvalue, self.tb = sys.exc_info()
        # Expunge libpry from the traceback
        self.explanation = None 
        if self.exctype == AssertionError:
            r = self.extractLine(self.tb)
            if r[0]:
                self.explanation = str(explain.Explain(*r))
        while "libpry" in self.tb.tb_frame.f_code.co_filename:
            next = self.tb.tb_next
            if next:
                self.tb = next
            # begin nocover
            else:
                break
            # end nocover
        # We lose information if we call format_exception in __str__
        self.s = traceback.format_exception(
                self.exctype, self.excvalue, self.tb
            )

    def extractLine(self, tb):
        r = None
        while tb is not None:
            f = tb.tb_frame
            lineno = tb.tb_lineno
            co = f.f_code
            filename = co.co_filename
            name = co.co_name
            linecache.checkcache(filename)
            line = linecache.getline(filename, lineno, f.f_globals)
            line = line.strip()
            parts = line.split()
            if parts:
                if parts[0] == "assert":
                    line = line[7:]
            line = line.strip()
            r = (line, f.f_globals, f.f_locals)
            tb = tb.tb_next
        return r

    def __str__(self):
        strs = [
                 "%s"%self.node.fullPath(),
               ]
        if self.msg:
            strs.append("    %s:"%self.msg)
        for i in self.s:
            strs.append("    %s"%i.rstrip())
        strs.append("")
        if self.explanation:
            strs.append(self.explanation)
            strs.append("\n")
        return "\n".join(strs)


class OK:
    """
       OK tests True.
    """
    def __init__(self, node, time):
        self.node, self.time = node, time


class _OutputZero:
    def __init__(self, root):
        self.root = root
        self.maxname = self.root.maxPathLen()

    def nodePre(self, node): pass
    def nodePost(self, node): pass
    def nodeError(self, node): pass
    def nodePass(self, node): pass
    def setUpError(self, node): pass
    def tearDownError(self, node): pass
    def final(self, node): pass
    def tearDownAllError(self, node): pass
    def setUpAllError(self, node): pass


class _OutputOne(_OutputZero):
    def nodeError(self, node):
        return "E"

    def setUpError(self, node):
        return "[S]"

    def tearDownError(self, node):
        return "[T]"

    def nodePass(self, node):
        if isinstance(node, TestNode):
            return "."

    def tearDownAllError(self, node):
        return "[TA]"

    def setUpAllError(self, node):
        return "[SA]"

    def final(self, root):
        lst = ["\n"]
        if isinstance(root.goState, Error):
            root.goState.msg = None
            s = [
                    "Internal error:",
                    str(root.goState)
                ]
            return "".join(s)

        errs = root.allError()
        if errs:
            lst.append("\nERRORS\n======\n")
            for i in errs:
                lst.append(str(i.getError()))
                lst.append("\n")

        if root.goState and not root.isError():
            infostr = [
                "pass: %s"%len(root.allPassed())
            ]
            if errs:
                infostr.append("fail: %s"%len(errs))
            notrun = root.allNotRun()
            if notrun:
                infostr.append("skip: %s"%len(notrun))
            lst.append(
                "%s tests %s- %.3fs\n"%(
                    len(root.tests()),
                    "(%s) "%", ".join(infostr),
                    root.goState.time
                )
            )

        if root.cover:
            for i in root.preOrder():
                if hasattr(i, "coverage") and i.coverage:
                    lst.append("\n")
                    lst.append("> %s\n"%i.dirPath)
                    lst.append(i.coverage.coverageReport())
        
        # Profile printing is a massive kludge, mostly because the pstats
        # module is an awful, awful piece of software, perversely designed to
        # be impossible to sensibly interact with. One day, in our Copious
        # Spare Time we might rewrite it, but for now we kludge.
        if root.profile:
            lst.append("\nPROFILE\n=======\n")
            for i in root.allPassed():
                s = i.profStats
                lst.append("%s\n"%i.fullPath())
                lst.append("   %s function calls"%(s.total_calls))
                if s.total_calls != s.prim_calls:
                    lst.append(" (%d primitive calls)"%s.prim_calls)
                lst.append(" in %.3f CPU seconds"%s.total_tt)
                width, funcs = s.get_print_list([])
                s.print_title()
                for f in funcs:
                    # We don't want to know about libpry itself.
                    if not "/libpry/" in f[0]:
                        s.print_line(f)
                lst.append("\n")
                lst.append(s.stream.getvalue())
                lst.append("\n\n")
        return "".join(lst)


class _OutputTwo(_OutputOne):
    def nodePre(self, node):
        if isinstance(node, TestNode):
            p = node.fullPath()
            padding = "."*(self.maxname - len(p))
            return "%s .%s "%(p, padding)

    def nodePost(self, node):
        if isinstance(node, TestNode):
            return "\n"

    def nodeError(self, node):
        if isinstance(node, TestNode):
            return "FAIL"

    def nodePass(self, node):
        if isinstance(node, TestNode):
            return "OK"

    def setUpError(self, node):
        cnt = len(node.allSkip())
        return "STOP\n\t** setUp failed, skipping %s tests"%cnt

    def setUpAllError(self, node):
        cnt = len(node.tests())
        lst = [
            "%s ...\tSTOP\n"%node.fullPath(),
            "\t** setUpAll failed, skipping %s tests\n"%cnt
        ]
        return "".join(lst)

    def tearDownAllError(self, node):
        lst = [
            "%s ...\tSTOP\n"%node.fullPath(),
            "\t** tearDownAll failed\n"
        ]
        return "".join(lst)

    def tearDownError(self, node):
        cnt = len(node.allSkip())
        add = ""
        if cnt:
            add = ", skipping %s tests"%cnt
        return "\n\t** tearDown failed%s"%add


class _OutputThree(_OutputTwo):
    def nodePass(self, node):
        if isinstance(node, TestNode):
            return "OK (%.3fs)"%node.callState.time


class _Output:
    def __init__(self, root, verbosity, fp=sys.stdout):
        self.fp = fp
        if verbosity == 0:
            self.o = _OutputZero(root)
        elif verbosity == 1:
            self.o = _OutputOne(root)
        elif verbosity == 2:
            self.o = _OutputTwo(root)
        elif verbosity == 3:
            self.o = _OutputThree(root)
        else:
            self.o = _OutputThree(root)

    def __getattr__(self, attr):
        meth = getattr(self.o, attr)
        def printClosure(*args, **kwargs):
            if self.fp:
                s = meth(*args, **kwargs)
                if s:
                    self.fp.write(s)
                    # Defeat buffering
                    self.fp.flush()
        return printClosure


class _TestBase(_tinytree.Tree):
    """
        Automatically turns methods or arbitrary callables of the form test_*
        into TestNodes.
    """
    # The name of this node. Names should not contain periods or spaces.
    name = None
    _selected = True
    def __init__(self, children=None, name=None):
        _tinytree.Tree.__init__(self, children)
        if name:
            self.name = name
        self._ns = {}

    def __getitem__(self, key):
        if self._ns.has_key(key):
            return self._ns[key]
        elif self.parent:
            return self.parent.__getitem__(key)
        else:
            raise KeyError, "No such data item: %s"%key

    def __setitem__(self, key, value):
        self._ns[key] = value

    def _run(self, meth, dstObj, name, repeat, profile, *args, **kwargs):
        """
            Utility method that runs a callable, and sets a State object.
            
            srcObj:     The object from which to source the method
            dstObj:     The object on which to set the state variable
            meth:       The name of the method to call
        """
        if profile:
            prof = cProfile.Profile()
        try:
            start = time.time()
            for i in xrange(repeat):
                if profile:
                    r = prof.runcall(meth, *args, **kwargs)
                else:
                    r = meth(*args, **kwargs)
            stop = time.time()
        except Exception, e:
            setattr(
                dstObj, name + "State",
                Error(
                    dstObj,
                    "" if name == "call" else name
                )
            )
            return True
        if r is not NOTRUN:
            if profile:
                pstream = cStringIO.StringIO()
                dstObj.profStats = pstats.Stats(prof, stream=pstream)
                dstObj.profStats.sort_stats(profile)
            setattr(dstObj, name + "State", OK(dstObj, stop-start))
        return False

    def tests(self):
        """
            All test nodes.
        """
        lst = []
        for i in self.preOrder():
            if isinstance(i, TestNode):
                lst.append(i)
        return lst

    def maxPathLen(self):
        return max([len(i.fullPath()) for i in self.preOrder()])

    def hasTests(self):
        """
            Does this node have currently selected child tests?
        """
        for i in self.preOrder():
            if isinstance(i, TestNode) and i._selected:
                 return True
        return False

    def prune(self):
        """
            Remove all internal nodes that have no test children.
        """
        for i in self.postOrder():
            if not i.hasTests() and i.parent:
                i.remove()

    def allError(self):
        """
            All nodes that errored.
        """
        return [i for i in self.preOrder() if i.isError()]

    def allPassed(self):
        """
            All test nodes that passed.
        """
        return [i for i in self.tests() if i.isPassed()]

    def allNotRun(self):
        """
            All test nodes that that have not been run.
        """
        return [i for i in self.tests() if i.isNotRun()]

    def allSkip(self):
        """
            If we skipped from this test onwards, not including this test
            itself, how many tests would we skip?

            This amounts to a) and all our children, and b) all our "right"
            siblings, and all their children. 
        """
        lst = []
        seen = False
        for i in self.siblings():
            if i is self:
                seen = True
            if seen:
                lst.extend(i.tests())
        return [i for i in lst if not i is self]

    def hasProfStats(self):
        """
            Does this node or any of its children have profile statistics?
        """
        for i in self.tests():
            if i.profStats:
                return True
        return False

    def isError(self):
        """
            True if this node has experienced a test failure.
        """
        for i in self._states():
            if isinstance(i, Error):
                return True
        return False

    def getError(self):
        """
            Return the Error object for this node. Raises an exception if there
            is none.
        """
        for i in self._states():
            if isinstance(i, Error):
                return i
        raise ValueError, "No error for this node."

    def isNotRun(self):
        """
            True if this node was not run at all. Note that a node that
            experienced failure during setup will return False.
        """
        for i in self._states():
            if i is not None:
                return False
        return True

    def isPassed(self):
        """
            True if this node has passed.
        """
        if (not self.isError()) and (not self.isNotRun()):
            return True
        return False

    def fullPathParts(self):
        """
            Return the components text path of a node.
        """
        lst = []
        for i in self.pathFromRoot():
            if i.name:
                lst.append(i.name)
        return lst

    def fullPath(self):
        """
            Return the full text path of a node as a string.
        """
        return ".".join(self.fullPathParts())

    def search(self, spec):
        """
            Search for matching child nodes using partial path matching.
        """
        # Sneakily (but inefficiently) use string 'in' operator for subsequence
        # searches. This doesn't matter for now, but we can do better.
        xspec = "." + spec + "."
        lst = []
        for i in self.children:
            p = "." + i.fullPath() + "."
            if xspec in p:
                lst.append(i)
            else:
                lst.extend(i.search(spec))
        return lst

    def mark(self, spec):
        """
            - First, un-select all nodes.
            - Now find all matches for spec. For each match, select all direct
              ancestors and all children as
        """
        for i in self.preOrder():
            i._selected = False
        for i in self.search(spec):
            for j in i.pathToRoot():
                j._selected = True
            for j in i.preOrder():
                j._selected = True

    def printStructure(self, outf=sys.stdout):
        for i in self.preOrder():
            if i.name:
                parts = i.fullPathParts()
                if len(parts) > 1:
                    print >> outf, "    "*(len(parts)-1),
                print >> outf, i.name

AUTO = object()
NOTRUN = object()

class TestTree(_TestBase):
    """
        A container for tests.
    """
    _base = None
    _exclude = None
    _include = None
    name = None
    # An OK object if setUp succeeded, an Error object if it failed, and None
    # if no setUp was run.
    setUpState = None
    # An OK object if tearDown succeeded, an Error object if it failed, and None
    # if no tearDown was run.
    tearDownState = None
    # An OK object if setupAll succeeded, an Error object if it failed, and None
    # if no tearDown was run.
    setUpAllState = None
    # An OK object if teardownAll succeeded, an Error object if it failed, and
    # None if no tearDown was run.
    tearDownAllState = None
    def __init__(self, children=None, name=AUTO):
        if self.name:
            name = self.name
        elif name is AUTO:
            name = self.__class__.__name__
        _TestBase.__init__(self, children, name)

    def setUp(self): return NOTRUN
    def setUpAll(self): return NOTRUN
    def tearDown(self): return NOTRUN
    def tearDownAll(self): return NOTRUN

    def _states(self):
        return [
                    self.setUpAllState,
                    self.tearDownAllState,
                    self.setUpState,
                    self.tearDownState,
                ]

    def run(self, output, repeat, profile):
        """
            Run the tests contained in this suite.
        """
        if self._run(self.setUpAll, self, "setUpAll", 1, None):
            output.setUpAllError(self)
            return
        for i in self.children:
            output.nodePre(i)

            if self._run(self.setUp, i, "setUp", 1, None):
                output.setUpError(i)
                output.nodePost(i)
                return

            if i.run(output, repeat, profile):
                output.nodeError(i)
            else:
                output.nodePass(i)

            if self._run(self.tearDown, i, "tearDown", 1, None):
                output.tearDownError(i)
                output.nodePost(i)
                return

            output.nodePost(i)

        if self._run(self.tearDownAll, self, "tearDownAll", 1, None):
            output.tearDownAllError(self)
            return


class AutoTree(TestTree):
    """
        Automatically adds methods of the form test_* as child TestNodes.
    """
    _testPrefix = "test_"
    def __init__(self, children=None, name=AUTO):
        TestTree.__init__(self, children, name=name)
        k = dir(self)
        k.sort()
        for i in k:
            if i.startswith(self._testPrefix):
                self.addChild(CallableNode(i, getattr(self, i)))


class TestNode(_TestBase):
    """
        A node representing an actual runnable test.
    """
    # An OK object if run succeeded, an Error object if it failed, and None
    # if the test was not run.
    callState = None
    # An OK object if setUp succeeded, an Error object if it failed, and None
    # if no setUp was run.
    setUpState = None
    # An OK object if setUp succeeded, an Error object if it failed, and None
    # if no tearDown was run.
    tearDownState = None
    # A pstats.Stats object if profile was run, else None
    profStats = None
    def __init__(self, name):
        _TestBase.__init__(self, None, name=name)

    def run(self, output, repeat, profile):
        return self._run(self.__call__, self, "call", repeat, profile)

    def _states(self):
        return [
                    self.setUpState,
                    self.tearDownState,
                    self.callState,
                ]

    def __call__(self):
        raise NotImplementedError


class CallableNode(TestNode):
    """
        A utility wrapper to create a TestNode from an arbitrary callable.
    """
    def __init__(self, name, meth):
        TestNode.__init__(self, name)
        self.meth = meth

    def __call__(self):
        self.meth()

    def __repr__(self):
        return "CallableNode: %s"%self.name


class FileNode(TestTree):
    # The special magic flag allows pry to run coverage analysis on its own 
    # test suite
    def __init__(self, dirname, filename, magic):
        modname = filename[:-3]
        TestTree.__init__(self, name=os.path.join(dirname, modname))
        self.dirname, self.filename = dirname, filename
        m = __import__(modname)
        # When pry starts up, it loads the libpry module. In order for the
        # instantiation stuff in libpry to be counted in coverage, we need to
        # go through and re-execute them. We don't "reload", since this will
        # create a new suite of class instances, and break our code.
        # begin nocover
        if magic:
            for k in sys.modules.keys():
                if "libpry" in k and sys.modules[k]:
                    n = sys.modules[k].__file__
                    if n.endswith("pyc"):
                        execfile(n[:-1])
                    elif n.endswith("py"):
                        execfile(n)
        # end nocover
        # Force a reload to stop Python caching modules that happen to have 
        # the same name
        reload(m)
        if hasattr(m, "tests"):
            self.addChildrenFromList(m.tests)

    def __repr__(self):
        return "FileNode: %s"%self.filename


class _DirNode(TestTree):
    """
        A node representing a directory of tests. 
    """
    CONF = ".pry"
    def __init__(self, path, cover):
        TestTree.__init__(self, name=None)
        if os.path.isdir(path):
            self.dirPath = path
            glob = _TestGlob
        elif os.path.isfile(path):
            self.dirPath = os.path.dirname(path) or "."
            glob = os.path.basename(path)

        c = config.Config(os.path.join(self.dirPath, self.CONF))
        self.baseDir = c.base
        self.coveragePath = c.coverage
        self.excludeList = c.exclude
        self.magic = c._magic

        if self.coveragePath == "None":
            cover = False

        self.coverage = False
        self._pre()
        if cover:
            self.coverage = coverage.Coverage(
                self.coveragePath,
                self.excludeList,
                True if cover is DUMMY else False
            )
            self.coverage.start()
        l = os.listdir(".")
        l.sort()
        for i in l:
            if fnmatch.fnmatch(i, glob):
                self.addChild(FileNode(self.dirPath, i, self.magic))
        self._post()

    def _pre(self):
        self.oldPath = sys.path
        sys.path = sys.path[:]
        sys.path.insert(0, ".")
        sys.path.insert(0, self.baseDir)
        self.oldcwd = os.getcwd()
        os.chdir(self.dirPath)
        if self.coverage:
            self.coverage.start()
    
    def _post(self):
        sys.path = self.oldPath
        os.chdir(self.oldcwd)
        if self.coverage:
            self.coverage.stop()

    def setUpAll(self):
        self._pre()

    def tearDownAll(self):
        self._post()

    def __repr__(self):
        return "_DirNode: %s"%self.dirPath


# Do a dummy coverage run
DUMMY = object()
class _RootNode(TestTree):
    """
        This node is the parent of all tests.
    """
    goState = None
    def __init__(self, cover, profile):
        TestTree.__init__(self, name=None)
        self.cover = cover
        self.profile = profile

    def run(self, output, repeat):
        self._run(
            TestTree.run,
            self,
            "go",
            1,
            False,
            self,
            output,
            repeat,
            self.profile
        )

    def addPath(self, path, recurse):
        if recurse:
            dirset = set()
            for root, dirs, files in os.walk(path):
                if os.path.isfile(os.path.join(root, ".pry")):
                    dirset.add(root)
            l = list(dirset)
            l.sort()
            for i in l:
                self.addChild(_DirNode(i, self.cover))
        else:
            self.addChild(_DirNode(path, self.cover))
