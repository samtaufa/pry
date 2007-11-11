"""
    A tree-based unit test system.

    Each test is a node in a tree of tests. Each test can have a setUp and
    tearDown method - these get run before and after each child node is run.
"""
import sys, time, traceback, os, fnmatch
import tinytree
import coverage

_TestGlob = "test_*.py"


class Skip(Exception): pass


class Error:
    """
        Error tests False.
    """
    def __init__(self, node, msg):
        self.node, self.msg = node, msg
        self.exc = sys.exc_info()

    def __str__(self):
        strs = [
                 "Error: %s"%self.msg,
                 self.node.fullPath()
               ]
        for i in traceback.format_exception(*self.exc):
            strs.append("    %s"%i.rstrip())
        strs.append("\n")
        return "\n".join(strs)


class OK:
    """
       OK tests True.
    """
    def __init__(self, node, time):
        self.node, self.time = node, time


class _OutputZero:
    def nodePre(self, node): return ""
    def nodeError(self, node): return ""
    def nodePass(self, node): return ""
    def final(self, node): return ""


class _OutputOne:
    def nodePre(self, node): return ""

    def nodeError(self, node):
        return "E"

    def nodePass(self, node):
        return "."

    def final(self, root):
        lst = ["\n\n"]
        for i in root.preOrder():
            if i.isError():
                lst.append(str(i.getError()))

        print root.runState.time

        return "".join(lst)


class _OutputTwo(_OutputOne):
    def nodePre(self, node):
        return "%s ...\t"%node.fullPath()

    def nodeError(self, node):
        return "FAIL\n"

    def nodePass(self, node):
        return "OK\n"


class _OutputThree(_OutputTwo):
    pass


class _Output:
    def __init__(self, verbosity, fp=sys.stdout):
        self.fp = fp
        if verbosity == 0:
            self.o = _OutputZero()
        elif verbosity == 1:
            self.o = _OutputOne()
        elif verbosity == 2:
            self.o = _OutputTwo()
        elif verbosity == 3:
            self.o = _OutputThree()
        else:
            self.o = _OutputThree()

    def __getattr__(self, attr):
        meth = getattr(self.o, attr)
        def printClosure(*args, **kwargs):
            if self.fp:
                self.fp.write(meth(*args, **kwargs))
        return printClosure


class _TestBase(tinytree.Tree):
    """
        Automatically turns methods or arbitrary callables of the form test_*
        into TestNodes.
    """
    # The name of this node. Names should not contain periods or spaces.
    name = None
    _selected = True
    def __init__(self, children=None, name=None):
        tinytree.Tree.__init__(self, children)
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

    def _run(self, dstObj, meth):
        """
            Utility method that runs a callable, and returns a State object.
            
            dstObj:     The object on which to set the state variable
            meth:       The name of the method to call
        """
        if meth == "run":
            c = self
        else:
            c = getattr(self, meth, None)
        if not c:
            return None
        try:
            start = time.time()
            c()
            stop = time.time()
        except:
            setattr(dstObj, meth + "State", Error(self, meth))
            raise Skip()
        setattr(dstObj, meth + "State", OK(self, stop-start))

    def tests(self):
        """
            All test nodes.
        """
        lst = []
        for i in self.preOrder():
            if isinstance(i, TestNode):
                lst.append(i)
        return lst

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
            All test nodes that errored.
        """
        return [i for i in self.tests() if i.isError()]

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
            True if this node has experienced a test failure.
        """
        for i in self._states():
            if not i is None:
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

class TestTree(_TestBase):
    """
        Automatically turns methods or arbitrary callables of the form test_*
        into TestNodes.
    """
    _testPrefix = "test_"
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
        k = dir(self)
        k.sort()
        for i in k:
            if i.startswith(self._testPrefix):
                self.addChild(TestWrapper(i, getattr(self, i)))

    def _states(self):
        return [
                    self.setUpAllState,
                    self.tearDownAllState,
                    self.setUpState,
                    self.tearDownState,
                ]

    def run(self, output):
        """
            Run the tests contained in this suite.
        """
        self._run(self, "setUpAll")
        for i in self.children:
            self._run(i, "setUp")
            try:
                i.run(output)
            except Skip:
                return
            self._run(i, "tearDown")
        self._run(self, "tearDownAll")


class TestNode(_TestBase):
    # An OK object if run succeeded, an Error object if it failed, and None
    # if the test was not run.
    runState = None
    # An OK object if setUp succeeded, an Error object if it failed, and None
    # if no setUp was run.
    setUpState = None
    # An OK object if setUp succeeded, an Error object if it failed, and None
    # if no tearDown was run.
    tearDownState = None
    def __init__(self, name):
        _TestBase.__init__(self, None, name=name)

    def run(self, output):
        output.nodePre(self)
        try:
            self._run(self, "run")
        except Skip:
            return
        output.nodePass(self)

    def _states(self):
        return [
                    self.setUpState,
                    self.tearDownState,
                    self.runState,
                ]

    def __call__(self):
        raise NotImplementedError


class TestWrapper(TestNode):
    def __init__(self, name, meth):
        TestNode.__init__(self, name)
        self.meth = meth

    def __call__(self):
        self.meth()


class FileNode(TestTree):
    def __init__(self, dirname, filename):
        modname = filename[:-3]
        TestTree.__init__(self, name=os.path.join(dirname, modname))
        self.dirname, self.filename = dirname, filename
        globs, locs = {}, {}
        m = __import__(modname)
        if hasattr(m, "tests"):
            self.addChildrenFromList(m.tests)


class DirNode(TestTree):
    def __init__(self, path):
        TestTree.__init__(self, name=None)
        self.path = path
        self.baseDir = ".."
        self._pre()
        for i in os.listdir("."):
            if fnmatch.fnmatch(i, _TestGlob):
                self.addChild(FileNode(path, i))
        self._post()

    def _pre(self):
        self.oldPath = sys.path
        sys.path = sys.path[:]
        sys.path.insert(0, ".")
        sys.path.insert(0, self.baseDir)
        self.oldcwd = os.getcwd()
        os.chdir(self.path)

    def _post(self):
        sys.path = self.oldPath
        os.chdir(self.oldcwd)

    def setUpAll(self):
        self._pre()

    def tearDownAll(self):
        self._post()


class RootNode(TestTree):
    """
        This node is the parent of all tests.
    """
    def __init__(self, path, recurse):
        TestTree.__init__(self, name=None)
        if recurse:
            dirset = set()
            for root, dirs, files in os.walk(path):
                for i in files:
                    if fnmatch.fnmatch(i, _TestGlob):
                        dirset.add(root)
            for i in dirset:
                self.addChild(DirNode(i))
        else:
            self.addChild(DirNode(path))
