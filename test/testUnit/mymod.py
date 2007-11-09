
# MUST be on lines 3, 4, 5
def run(x, y):
    z = 1
    return z


def coveragePath():
    import os.path
    os.path.isdir("/")

def coveragePath2():        #
    """
        A docstring
    """                     #
    x = 1                   # 
    if 0:                   #
        pass
    else:
        pass                #
    x = [                   #
            1,
            2,
            3
        ]
    try:                    #
        1                   #
    except:
        2
