import sys, time, traceback, os, fnmatch, cProfile, pstats, io, imp
import linecache, shutil, tempfile
from . import _tinytree, explain, coverage, utils, config

_TestGlob = "test_*.py"


def raises(exc, obj, *args, **kwargs):
    """
        Assert that a callable raises a specified exception.

        :exc An exception class or a string. If a class, assert that an
        exception of this type is raised. If a string, assert that the string
        occurs in the string representation of the exception, based on a
        case-insenstivie match.

        :obj A callable object.

        :args Arguments to be passsed to the callable.

        :kwargs Arguments to be passed to the callable.
    """
    try:
        obj(*args, **kwargs)
    except Exception as v:
        if utils.isStringLike(exc):
            if exc.lower() in str(v).lower():
                return
            else:
                raise AssertionError(
                    "Expected %s, but caught %s"%(
                        repr(str(exc)), v
                    )
                )
        else:
            if isinstance(v, exc):
                return
            else:
                raise AssertionError(
                    "Expected %s, but caught %s %s"%(
                        exc.__name__, v.__class__.__name__, str(v)
                    )
                )
    raise AssertionError("No exception raised.")


class TmpDirMixin:
    """
        A utility mixin that creates a temporary directory during setup, and
        removes it during teardown. The directory path is inserted into the
        test namespace as follows:
            
            self["tmpdir"] = path
    """
    def setUp(self):
        self["tmpdir"] = tempfile.mkdtemp()

    def tearDown(self):
        if os.path.isdir(self["tmpdir"]):
            shutil.rmtree(self["tmpdir"])


class _Error:
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


class _OK:
    def __init__(self, node, time):
        self.node, self.time = node, time


class _OutputZero:
    def __init__(self, root):
        self.root = root
        self.maxname = self.root._maxPathLen()

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
        if isinstance(node, Test):
            return "."

    def tearDownAllError(self, node):
        return "[TA]"

    def setUpAllError(self, node):
        return "[SA]"

    def final(self, root):
        lst = ["\n"]
        if isinstance(root.goState, _Error):
            root.goState.msg = None
            s = [
                    "Internal error:",
                    str(root.goState)
                ]
            return "".join(s)

        errs = root.allErrors()
        if errs:
            lst.append("\nERRORS\n======\n")
            for i in errs:
                lst.append(str(i.getError()))
                lst.append("\n")

        if root.goState and not root.getError():
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
                    # We don't want to know about libpry itself or the profile
                    # disable function.
                    if not "/libpry/" in f[0] and not "_lsprof" in f[2]:
                        s.print_line(f)
                lst.append("\n")
                lst.append(s.stream.getvalue())
                lst.append("\n\n")
        return "".join(lst)


class _OutputTwo(_OutputOne):
    def nodePre(self, node):
        if isinstance(node, Test):
            p = node.fullPath()
            padding = "."*(self.maxname - len(p))
            return "%s .%s "%(p, padding)

    def nodePost(self, node):
        if isinstance(node, Test):
            return "\n"

    def nodeError(self, node):
        if isinstance(node, Test):
            return "FAIL"

    def nodePass(self, node):
        if isinstance(node, Test):
            return "OK"

    def setUpError(self, node):
        cnt = len(node._allSkip())
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
        cnt = len(node._allSkip())
        add = ""
        if cnt:
            add = ", skipping %s tests"%cnt
        return "\n\t** tearDown failed%s"%add


class _OutputThree(_OutputTwo):
    def nodePass(self, node):
        if isinstance(node, Test):
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
        into Tests.
    """
    #grok:include
    # The name of this node. Names should not contain periods or spaces.
    name = None
    _selected = True
    def __init__(self, children=None, name=None):
        """
            :children A nested list of child nodes
            :name The name of this node. Should not contain periods or spaces.
            Can optionally be set as a class variable in subclasses.
        """
        _tinytree.Tree.__init__(self, children)
        if name:
            self.name = name
        self._ns = {}

    def __getitem__(self, key):
        """
            Retrieve an item from the tree namespace. Keys are looked up in
            this node, and on all nodes to the root.
        """
        if key in self._ns:
            return self._ns[key]
        elif self.parent:
            return self.parent.__getitem__(key)
        else:
            raise KeyError("No such data item: %s"%key)

    def __setitem__(self, key, value):
        """
            Set an item in this node's namespace.
        """
        self._ns[key] = value

    def _runCallable(self, meth, dstObj, name, repeat, profile, *args, **kwargs):
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
            for i in range(repeat):
                if profile:
                    r = prof.runcall(meth, *args, **kwargs)
                else:
                    r = meth(*args, **kwargs)
            stop = time.time()
        except Exception as e:
            setattr(
                dstObj, name + "State",
                _Error(
                    dstObj,
                    "" if name == "call" else name
                )
            )
            return True
        if r is not _NOTRUN:
            if profile:
                pstream = io.StringIO()
                dstObj.profStats = pstats.Stats(prof, stream=pstream)
                dstObj.profStats.sort_stats(profile)
            setattr(dstObj, name + "State", _OK(dstObj, stop-start))
        return False

    def tests(self):
        """
            Return a pre-order list of all test nodes in this tree.
        """
        #grok:exclude
        lst = []
        for i in self.preOrder():
            if isinstance(i, Test):
                lst.append(i)
        return lst

    def _maxPathLen(self):
        """
            Return the maximum path length for any node in this tree.
        """
        return max([len(i.fullPath()) for i in self.preOrder()])

    def _hasTests(self):
        """
            Does this node have currently selected child tests?
        """
        for i in self.preOrder():
            if isinstance(i, Test) and i._selected:
                 return True
        return False

    def prune(self):
        """
            Remove all internal nodes that have no test children.
        """
        #grok:exclude
        for i in self.postOrder():
            if not i._hasTests() and i.parent:
                i.remove()

    def allErrors(self):
        """
            A list of sub-nodes that had errors, in pre-order.
        """
        #grok:exclude
        return [i for i in self.preOrder() if i.getError()]

    def allPassed(self):
        """
            A list of sub-nodes that passed, in pre-order.
        """
        #grok:exclude
        return [i for i in self.tests() if i.isPassed()]

    def allNotRun(self):
        """
            A list of sub-nodes that have not been run.
        """
        #grok:exclude
        return [i for i in self.tests() if i.isNotRun()]

    def _allSkip(self):
        """
            If we skipped from this test onwards, not including this test
            itself, how many tests would we skip?

            This amounts to: 
            
                - All our children
                - Plus all our "right" siblings, and all their children. 
        """
        lst = []
        seen = False
        for i in self.siblings():
            if i is self:
                seen = True
            if seen:
                lst.extend(i.tests())
        return [i for i in lst if not i is self]

    def _hasProfStats(self):
        """
            Does this node or any of its children have profile statistics?
        """
        for i in self.tests():
            if i.profStats:
                return True
        return False

    def getError(self):
        """
            Return the _Error object for this node. Returns None if no error
            occurred.
        """
        #grok:exclude
        for i in self._states():
            if isinstance(i, _Error):
                return i
        return None

    def isNotRun(self):
        """
            True if this node was not run at all. Note that a node that this
            method will return False for a test that experienced failure during
            setup.
        """
        #grok:exclude
        for i in self._states():
            if i is not None:
                return False
        return True

    def isPassed(self):
        """
            True if this node has been run and has passed.
        """
        #grok:exclude
        if (not self.getError()) and (not self.isNotRun()):
            return True
        return False

    def fullPathParts(self):
        """
            Return the components of the text path of a node as a list.
        """
        #grok:exclude
        lst = []
        for i in self.pathFromRoot():
            if i.name:
                lst.append(i.name)
        return lst

    def fullPath(self):
        """
            Return the full text path of a node as a string.
        """
        #grok:exclude
        return ".".join(self.fullPathParts())

    def search(self, spec):
        """
            Search for matching child nodes using partial path matching.

            :spec A . delimited string specifying a partial test path.
        """
        #grok:exclude
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
            Mark child-nodes for running according to a specification.

            - First, un-select all nodes.
            - Find all matches for spec. For each match, select all direct
              ancestors and all children for running.
        """
        #grok:exclude
        for i in self.preOrder():
            i._selected = False
        for i in self.search(spec):
            for j in i.pathToRoot():
                j._selected = True
            for j in i.preOrder():
                j._selected = True

    def printStructure(self, outf=sys.stdout):
        """
            Print the high-level structure of the test suite.

            :outf Output file descriptor.
        """
        #grok:exclude
        for i in self.preOrder():
            if i.name:
                parts = i.fullPathParts()
                if len(parts) > 1:
                    print("    "*(len(parts)-1), end=' ', file=outf)
                print(i.name, file=outf)

#Flag object for TestContainer
AUTO = object()
_NOTRUN = object()

class TestContainer(_TestBase):
    """
        A container for tests.
    """
    _base = None
    _exclude = None
    _include = None
    def __init__(self, children=None, name=AUTO):
        """
            :children A nested list of subnodes.

            :name The name of this node. Should not contain spaces or periods.
            If set to the special constant AUTO, the name is computed
            automatically from the class name of this instance.
        """
        if self.name:
            name = self.name
        elif name is AUTO:
            name = self.__class__.__name__
        _TestBase.__init__(self, children, name)
        # An _OK object if setUp succeeded, an _Error object if it failed, and None
        # if no setUp was run.
        self.setUpState = None
        # An _OK object if tearDown succeeded, an _Error object if it failed, and None
        # if no tearDown was run.
        self.tearDownState = None
        # An _OK object if setupAll succeeded, an _Error object if it failed, and None
        # if no tearDown was run.
        self.setUpAllState = None
        # An _OK object if teardownAll succeeded, an _Error object if it failed, and
        # None if no tearDown was run.
        self.tearDownAllState = None

    def setUp(self):
        """
            Run before each child is run.
        """
        return _NOTRUN

    def setUpAll(self):
        """
            Run once before any children are run.
        """
        return _NOTRUN

    def tearDown(self):
        """
            Run after each child is run.
        """
        return _NOTRUN

    def tearDownAll(self):
        """
            Run after all children have run.
        """
        return _NOTRUN

    def _states(self):
        return [
                    self.setUpAllState,
                    self.tearDownAllState,
                    self.setUpState,
                    self.tearDownState,
                ]

    def _run(self, output, repeat, profile):
        """
            Run the tests contained in this suite.
        """
        if self._runCallable(self.setUpAll, self, "setUpAll", 1, None):
            output.setUpAllError(self)
            return
        for i in self.children:
            output.nodePre(i)

            if self._runCallable(self.setUp, i, "setUp", 1, None):
                output.setUpError(i)
                output.nodePost(i)
                return

            if i._run(output, repeat, profile):
                output.nodeError(i)
            else:
                output.nodePass(i)

            if self._runCallable(self.tearDown, i, "tearDown", 1, None):
                output.tearDownError(i)
                output.nodePost(i)
                return

            output.nodePost(i)

        if self._runCallable(self.tearDownAll, self, "tearDownAll", 1, None):
            output.tearDownAllError(self)
            return


class AutoTree(TestContainer):
    """
        TestContainer that Automatically adds methods of the form test_* as child
        Tests.
    """
    _testPrefix = "test_"
    def __init__(self, children=None, name=AUTO):
        """
            :children Optional nested list of subnodes.

            :name The name of this node. Should not contain spaces or periods.
            If set to the special constant AUTO, the name is computed
            automatically from the class name of this instance.

            Automatically adds methods of the form test_* as child Tests.
        """
        TestContainer.__init__(self, children, name=name)
        k = dir(self)
        k.sort()
        for i in k:
            if i.startswith(self._testPrefix):
                self.addChild(CallableNode(i, getattr(self, i)))


class Test(_TestBase):
    """
        A node representing a test.
    """
    def __init__(self, name):
        """
            :name The name of this node. Should not contain spaces or periods.
        """
        _TestBase.__init__(self, None, name=name)
        # An _OK object if run succeeded, an _Error object if it failed, and None
        # if the test was not run.
        self.callState = None
        # An _OK object if setUp succeeded, an _Error object if it failed, and None
        # if no setUp was run.
        self.setUpState = None
        # An _OK object if setUp succeeded, an _Error object if it failed, and None
        # if no tearDown was run.
        self.tearDownState = None
        # A pstats.Stats object if profile was run, else None
        self.profStats = None

    def _run(self, output, repeat, profile):
        return self._runCallable(self.__call__, self, "call", repeat, profile)

    def _states(self):
        return [
                    self.setUpState,
                    self.tearDownState,
                    self.callState,
                ]

    def __call__(self):
        """
            This method contains the actual test.
        """
        raise NotImplementedError


class CallableNode(Test):
    """
        A utility wrapper to create a Test from a callable.
    """
    def __init__(self, name, obj):
        """
            :name Name of this test.
            :obj A callable object.
        """
        Test.__init__(self, name)
        self.obj = obj

    def __call__(self):
        #grok:exclude
        self.obj()

    def __repr__(self):
        #grok:exclude
        return "CallableNode: %s"%self.name


class _FileNode(TestContainer):
    # The special magic flag allows pry to run coverage analysis on its own 
    # test suite
    def __init__(self, dirname, filename, magic):
        modname = filename[:-3]
        TestContainer.__init__(self, name=os.path.join(dirname, modname))
        self.dirname, self.filename = dirname, filename
        m = __import__(modname)
        # When pry starts up, it loads the libpry module. In order for the
        # instantiation stuff in libpry to be counted in coverage, we need to
        # go through and re-execute them. We don't "reload", since this will
        # create a new suite of class instances, and break our code.
        # begin nocover
        if magic:
            for k in list(sys.modules.keys()):
                if "libpry" in k and sys.modules[k]:
                    n = sys.modules[k].__file__
                    if n.endswith("pyc"):
                        exec(open(n[:-1]).read())
                    elif n.endswith("py"):
                        exec(open(n).read())
        # end nocover
        # Force a reload to stop Python caching modules that happen to have 
        # the same name
        imp.reload(m)
        if hasattr(m, "tests"):
            self.addChildrenFromList(m.tests)

    def __repr__(self):
        return "_FileNode: %s"%self.filename


class _DirNode(TestContainer):
    """
        A node representing a directory of tests. 
    """
    CONF = ".pry"
    def __init__(self, path, cover):
        TestContainer.__init__(self, name=None)
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
                True if cover is _DUMMY else False
            )
            self.coverage.start()
        l = os.listdir(".")
        l.sort()
        for i in l:
            if fnmatch.fnmatch(i, glob):
                self.addChild(_FileNode(self.dirPath, i, self.magic))
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
_DUMMY = object()
class _RootNode(TestContainer):
    """
        This node is the parent of all tests.
    """
    goState = None
    def __init__(self, cover, profile):
        TestContainer.__init__(self, name=None)
        self.cover = cover
        self.profile = profile

    def _run(self, output, repeat):
        self._runCallable(
            TestContainer._run,
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
