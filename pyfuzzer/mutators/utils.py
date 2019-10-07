import traceback


def format_args(args, limit):
    """Returns a comma separated list of given arguemnts. Each argument is
    at most ``limit`` characters.

    """

    sargs = []

    for arg in args:
        if isinstance(arg, str):
            arg = f"'{arg}'"
        else:
            arg = str(arg)

        sargs.append(arg[:limit])

    return ', '.join(sargs)


def print_callable(obj, args, limit=1024):
    """Print given callable name and its arguments, call it and then print
    the returned value or raised exception.

    """

    fargs = format_args(args, limit)

    # Print and flush callable name and arguments before calling it
    # since it may crash.
    print(f'{obj.__name__}({fargs})', end='', flush=True)

    try:
        res = obj(*args)
        print(f' = {str(res)[:limit]}')
    except Exception:
        print(' raises:')
        traceback.print_exc()
