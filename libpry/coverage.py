import parser, token, symbol, copy, getopt, types
import time, os.path, sys, tokenize, re
import utils

_coverRe = re.compile("\s*#\s*(begin|end)\s+nocover", re.I)
class File:
    def __init__(self, path):
        if path:
            self.path = os.path.abspath(path)
            data = open(path, "r").read()
            code = compile(data, path, "exec")
            self.exclusions = self.getExclusions(data, path)
            lines = self.getLines(code)
            self.executable = lines - self.exclusions
            self.executed = set()

    def __cmp__(self, other):
        c = cmp(self.percentage, other.percentage)
        if c == 0:
            return cmp(self.path, other.path)
        return c

    def nicePath(self, base):
        """
            Return a "nice" path, relative to the specified base.
        """
        common = len(os.path.commonprefix([base, self.path]))
        fname = self.path[common:]
        if fname[0] == "/":
            fname = fname[1:]
        return fname

    @property
    def numExecutable(self):
        return len(self.executable)

    @property
    def numExecuted(self):
        return len(self.executed - self.exclusions)

    @property
    def notExecuted(self):
        return self.executable - self.executed

    @property
    def notExecutedRanges(self):
        n = list(self.notExecuted)
        n.sort()
        return utils.summariseList(n)

    @property
    def percentage(self):
        if self.numExecutable:
            return (self.numExecuted/float(self.numExecutable))*100
        else:
            return 100.0

    def getLines(self, code):
        """
            Return a list of executable line numbers in a code object.
        """
        linenos = set()
        line_increments = [ord(c) for c in code.co_lnotab[1::2]]
        lineno = code.co_firstlineno
        for li in line_increments:
            lineno += li
            linenos.add(lineno)
        for c in code.co_consts:
            if isinstance(c, types.CodeType):
                linenos.update(self.getLines(c))
        if linenos:
            linenos.add(code.co_firstlineno)
        return linenos

    def getExclusions(self, data, filename):
        """
            Returns a set of lines covered by exclusion directives, excluding
            the directives themselves..
        """
        lines = data.splitlines()
        s = set()
        nocover = False
        for i, l in enumerate(lines):
            m = _coverRe.match(l)
            if m:
                if m.group(1) == "begin" and nocover == 0:
                    nocover = True
                elif m.group(1) == "end" and nocover == 1:
                    nocover = False
                else:
                    s = "Unbalanced nocover directive at line %s of %s"%(i, filename)
                    raise ValueError, s
            else:
                if nocover:
                    s.add(i+1)
        return s

    def getAnnotation(self):
        """
            Returns a dictionary with a list of snippets of text. Each snippet
            is an annotated list of un-run lines.
        """
        lines = open(self.path, "r").readlines()
        for i in self.notExecuted:
            lines[i-1] = "> " + lines[i-1]
        return "".join(lines)


class Coverage:
    def __init__(self, coveragePath, excludeList=[]):
        """
            coveragePath    - Path to the file tree that will be analysed.
            excludeList     - List of exceptions to coverage analysis.
        """
        if coveragePath:
            self.excludeList = [os.path.abspath(x) for x in excludeList]
            self.coveragePath = os.path.abspath(coveragePath)
            self.fileDict = self.getFileDict(self.coveragePath, self.excludeList)

    def getFileDict(self, path, excludeList):
        """
            Recursively finds all .py files not included in the excludelist.
            Returns a set of File objects.
        """
        d = dict()
        for root, dirs, files in os.walk(path):
            for f in files:
                if f.endswith(".py"):
                    p = os.path.join(root, f)
                    if not utils.isPathContainedAny(excludeList, p):
                        d[p] = File(p)
        return d

    # begin nocover
    def _globalTrace(self, frame, event, arg):
        """
            This method will produce incorrect coverage results in Python
            versions lower than 2.5.2. See the following commit:

                http://svn.python.org/view?rev=58963&view=rev
        """
        f = self.fileDict.get(os.path.abspath(frame.f_code.co_filename))
        if f:
            def local(frame, event, arg):
                if event == "line":
                    f.executed.add(frame.f_lineno)
                return local
            return local
        else:
            return None

    def start(self):
        sys.settrace(self._globalTrace)

    def stop(self):
        sys.settrace(None)
    # end nocover

    def getGlobalStats(self):
        """
            Returns a dictionary of statistics covering all files.
        """
        statementsRun = 0
        allStatements = 0
        for i in self.fileDict.values():
            statementsRun += i.numExecuted
            allStatements += i.numExecutable
        if allStatements == 0:
            perc = 0 
        else:
            perc = ((float(statementsRun)/float(allStatements))*100)
        return {
                    "statementsRun": statementsRun,
                    "allStatements": allStatements,
                    "percentage": perc
                }

    def statStr(self):
        lst = [
            "[run ] [tot ] [percent]\n"
            "=======================\n"
        ]
        files = self.fileDict.values()
        files.sort()
        files.reverse()
        for f in files:
            lst.append(
                "[%-4s] [%-4s] [%-6.5s%%]     %s  \n" % (
                    f.numExecuted,
                    f.numExecutable,
                    f.percentage,
                    f.nicePath(self.coveragePath),
                )
            )
            if f.notExecuted:
                lst.append("                            ")
                for i in f.notExecutedRanges:
                    try:
                        lst.append("[%s...%s] "%(i[0], i[1]))
                    except:
                        lst.append("%s "%(i))
                lst.append("\n")
        return "".join(lst)
