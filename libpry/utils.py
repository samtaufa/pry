import os.path, fnmatch

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


def isStringLike(anobj):
    try:
        # Avoid succeeding expensively if anobj is large.
        anobj[:0]+''
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
    return target, pattern
