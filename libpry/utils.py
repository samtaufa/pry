import os.path, fnmatch, struct, os

def summariseList(lst):
    """
        Takes a sorted list of numbers, and returns a summary.
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


def isPathContained(outer, inner):
    """
       Does inner lie "within" outer?
       Outer has to be an absolute path!
    """
    inner = os.path.abspath(inner)
    outer = os.path.abspath(outer)
    if inner[:len(outer)] != outer:
        return False
    elif len(inner) == len(outer):
        return True
    elif inner[len(outer)] in [os.path.sep, os.path.altsep]:
        return True
    return False


def isPathContainedAny(outerList, inner):
    """
        Like isPathContained, but with a list of outer directories.
    """
    for i in outerList:
        if isPathContained(i, inner):
            return True
    return False


def isStringLike(anobj):
    try:
        # Avoid succeeding expensively if anobj is large.
        anobj[:0]+''
    except:
        return 0
    else:
        return 1


def isNumeric(obj):
    try:
        obj + 0
    except:
        return 0
    else:
        return 1


def _splitSpec(spec):
    """ 
        Takes an input specification, and returns a (path, pattern) tuple.

        The splitting works as follows:
            - First, the spec is split on ".".
            - We then try to maximally match as much as possible of the
              start of the spec to an existing file or directory.
            - The remainder is considered the mark pattern.

        If no path is found, the first element of the return tuple is the empty
        string.
    """
    parts = spec.split(".")
    dirOffset = 0
    fileOffset = 0
    for i in range(1, len(parts) + 1):
        if os.path.isdir(".".join(parts[:i])):
            dirOffset = i
        elif os.path.isfile(".".join(parts[:i]) + ".py"):
            fileOffset = i
    if dirOffset > fileOffset:
        target = ".".join(parts[:dirOffset])
        pattern = ".".join(parts[dirOffset:])
    elif fileOffset:
        target = ".".join(parts[:fileOffset]) + ".py"
        pattern = ".".join(parts[fileOffset:])
    else:
        target = ""
        pattern = ".".join(parts)
    if target and pattern == "py":
        pattern = ""
    return target, pattern



# begin nocover
def terminalWidth():
    width = None
    try:
        import fcntl, termios
        cr = struct.unpack('hh', fcntl.ioctl(0, termios.TIOCGWINSZ, '1234'))
        width = int(cr[1])
    except (IOError, ImportError):
        pass
    return width or 80
