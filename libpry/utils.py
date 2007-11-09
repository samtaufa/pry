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
