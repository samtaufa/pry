import utils

def raises(exc, callableObj, *args, **kwargs):
    try:
        apply(callableObj, args, kwargs)
    except Exception, v:
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
                    "Expected %s, but caught %s"%(exc.__name__, v)
                )
    raise AssertionError("No exception raised.")

