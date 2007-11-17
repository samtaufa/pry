import parser, token, symbol, copy, getopt, types
import time, os.path, sys, tokenize, re
import utils

beginNocover = re.compile("\s*#\s*(begin|end)\s+nocover", re.I)


def summariseList(lst):
    """
        Takes a list of numbers, and returns a summary.
        Eg. [1, 2, 3, 4, 9] -> [(1, 4), 9]
            [1, 2, 3, 7, 8, 9] -> [(1, 3), (7, 9)]
    """
    if len(lst) < 2:
        return lst
    ranges = []
    start = 0
    for i in range(1, len(lst)):
        if (lst[i] - lst[i-1]) > 1:
            if (i-1) == start:
                start = i
                ranges.append(lst[i-1])
            else:
                ranges.append((lst[start], lst[i-1]))
                start = i
    if lst[start] == lst[i]:
        ranges.append(lst[i])
    else:
        ranges.append((lst[start], lst[i]))
    return ranges


def find_lines(code):
    linenos = set()
    line_increments = [ord(c) for c in code.co_lnotab[1::2]]
    lineno = code.co_firstlineno
    for li in line_increments:
        lineno += li
        linenos.add(lineno)
    for c in code.co_consts:
        if isinstance(c, types.CodeType):
            linenos.update(find_lines(c))
    return linenos


def find_exclusions(filename):
    f = open(filename, "r")
    s = set()
    nocover = 0
    for i, l in enumerate(f):
        m = beginNocover.match(l)
        if m:
            if m.group(1) == "begin" and nocover == 0:
                nocover = 1
            elif m.group(1) == "end" and nocover == 1:
                nocover = 0
            else:
                s = "Unbalanced nocover directive at line %s of %s"%(i, filename)
                raise ValueError, s
        if nocover:
            s.add(i+1)
    return s


def find_executable_linenos(filename):
    exclusions = find_exclusions(filename)
    prog = open(filename, "rU").read()
    code = compile(prog, filename, "exec")
    lines = find_lines(code) - exclusions
    return lines


def fileSet(path, excludeList):
    """
        Recursively finds all .py files that not included in the excludelist.
        Returns a set of absolute paths.
    """
    s = set()
    for root, dirs, files in os.walk(path):
        for f in files:
            if f.endswith(".py"):
                ap = os.path.abspath(os.path.join(root, f))
                if not utils.isPathContainedAny(excludeList, ap):
                    s.add(ap)
    return s


class Coverage:
    def __init__(self, coveragePath, excludeList=[]):
        """
            coveragePath    - Path to the file tree that will be analysed.
            excludeList     - List of exceptions to coverage analysis.
        """
        self.excludeList = [os.path.abspath(x) for x in excludeList]
        self.coveragePath = os.path.abspath(coveragePath)
        self.coverageFileset = fileSet(self.coveragePath, self.excludeList)
        # Keys are filenames, values are dictionaries of line numbers.
        self.linesRun = {}
        self.statementsRun = {}
        self.allStatements = {}
        # Keys are filenames, values are lists of lines for statements not covered.
        self.statementsNotRun = {}
        # Data gathered by the _trace method
        self._traceData = set()

    def _globalTrace(self, frame, event, arg):
        """

            This method is extremely delicate, because the Python trace stuff
            is buggy. For example

                for i in []: pass

            At the top of the function, and watch your coverage stats go to hell.

            We really should call abspath on the filename below, since the
            co_filename attribute for non-module imports is a relative path.
            This means that we can only run coverage on modules at the moment.
        """
        # FIXME: Lodge a Python bug over this
        try:
            for i in []: pass
        except Exception, e:
            print repr(e)

#        if frame.f_code.co_filename in self.coverageFileset:
#            return self._localTrace
#        elif frame.f_code.co_filename == "<string>":
#            return self._localTrace
#        else:
#            return None

    def _localTrace(self, frame, event, arg):
        """
            Called for every code event. We extract and take note of the
            filename and line number.
        """
        if event == "line":
            self._traceData.add((frame.f_code.co_filename, frame.f_lineno))
        return self._localTrace

    def _integrateTrace(self, _traceData, excludeList):
        linesRun = {}
        for path, line in _traceData:
            fname = os.path.abspath(path)
            if fname.startswith(self.coveragePath):
                if linesRun.has_key(fname):
                    linesRun[fname].add(line)
                else:
                    linesRun[fname] = set((line,))
        return linesRun

    def _allStatements(self, files, excludeList):
        for fileName in files:
            lno = find_executable_linenos(fileName)
            self.allStatements[fileName] = lno
            self.allStatements[fileName].update(self.linesRun[fileName])

    def start(self):
        sys.settrace(self._globalTrace)

    def stop(self):
        sys.settrace(None)

    def finalise(self):
        """
            Runs through the list of files, calculates a list of lines that
            weren't covered, and writes the list to self.files["filenames"].
        """
        self.linesRun = self._integrateTrace(self._traceData.copy(), self.excludeList)

        for fileName in self.linesRun.keys():
            lno = find_executable_linenos(fileName)
            self.allStatements[fileName] = lno
            self.allStatements[fileName].update(self.linesRun[fileName])

        # Calculate statementsRun
        sr = {}
        for fileName in self.linesRun:
            sr[fileName] = set()
            for i in self.linesRun[fileName]:
                if i in self.allStatements[fileName]:
                    sr[fileName].add(i)
        self.statementsRun = sr

        # Calculate statementsNotRun
        snr = {}
        for fileName in self.allStatements:
            snr[fileName] = []
            for i in self.allStatements[fileName]:
                if not i in self.statementsRun[fileName]:
                    snr[fileName].append(i)
            snr[fileName].sort()
        self.statementsNotRun = snr

    def getStats(self):
        """
            Returns a list of tuples, containing a dictionary of statistics each. 
            [(name, resultDict)...]
        """
        allStats = []
        for fileName in self.linesRun:
            statDict = {}
            statDict["allStatements"] = len(self.allStatements[fileName])
            statDict["statementsRun"] = len(self.statementsRun[fileName])
            if statDict["allStatements"]:
                srun = float(statDict["statementsRun"])
                sall = float(statDict["allStatements"])
                statDict["coverage"] = (srun/sall)*100
            else:
                # Empty file (e.g. empty __init__.py)
                statDict["coverage"] = 100.0
            statDict["ranges"] = summariseList(self.statementsNotRun[fileName])
            allStats.append((fileName, statDict))

        def compare(a, b):
            return cmp(
                len(self.statementsNotRun[a[0]]),
                len(self.statementsNotRun[b[0]])
            )
        allStats.sort(compare)
        return allStats

    def getGlobalStats(self):
        """
            Returns a dictionary of statistics covering all files.
        """
        # Overall lines
        statementsRun = 0
        allStatements = 0
        for fileName in self.linesRun:
            statementsRun += len(self.statementsRun[fileName])
            allStatements += len(self.allStatements[fileName])
        if allStatements == 0:
            perc = 0 
        else:
            perc = ((float(statementsRun)/float(allStatements))*100)

        return {
                    "statementsRun": statementsRun,
                    "allStatements": allStatements,
                    "percentage": perc
                }

    def getAnnotation(self):
        """
            Returns a dictionary with a list of snippets of text. Each snippet
            is an annotated list of un-run lines.
        """
        annotations = {}
        for fileName in self.statementsNotRun:
            if self.statementsNotRun[fileName]:
                lines = open(fileName).readlines()
                for i in self.statementsNotRun[fileName]:
                    lines[i-1] = "> " + lines[i-1]
                annotations[fileName] = lines
        return annotations

    def statStr(self):
        base = os.path.abspath(self.coveragePath)
        stats = self.getStats()
        lst = [
            "[run ] [tot ] [percent]\n"
            "=======================\n"
        ]
        for i in stats:
            common = len(os.path.commonprefix((base, i[0])))
            fname = i[0][common:]
            if fname[0] == "/":
                fname = fname[1:]
            lst.append(
                "[%-4s] [%-4s] [%-6.5s%%]:     %s  \n" % (
                    i[1]["statementsRun"],
                    i[1]["allStatements"],
                    i[1]["coverage"],
                    fname
                )
            )
            if i[1]["ranges"]:
                lst.append("                            ")
                for j in i[1]["ranges"]:
                    try:
                        lst.append("[%s...%s] "%(j[0], j[1]))
                    except:
                        lst.append("%s "%(j))
                lst.append("\n")
        return "".join(lst)

