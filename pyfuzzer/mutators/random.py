import inspect


FUNCS = None


def lookup_function(module, value):
    global FUNCS

    if FUNCS is None:
        FUNCS = [
            m[1] for m in inspect.getmembers(module, inspect.isbuiltin)
        ]

        if len(FUNCS) == 0:
            sys.exit(1)

    return FUNCS[value % len(FUNCS)]


def test_one_input(module, data):
    if len(data) == 0:
        return

    # C extension functions can not have type annotations. Can be part
    # of function documentation though.
    #
    # print(inspect.signature(func))
    #
    # print(func.__doc__)
    lookup_function(module, data[0])(data[1:])
