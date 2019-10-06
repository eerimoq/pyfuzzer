import traceback


def format_args(args, limit):
    sargs = []

    for arg in args:
        if isinstance(arg, str):
            arg = f"'{arg}'"
        else:
            arg = str(arg)

        sargs.append(arg[:limit])

    return ', '.join(sargs)


def print_function(func, args, limit=1024):
    fargs = format_args(args, limit)

    # Print and flush function name and arguments before calling the
    # function since it may crash.
    print(f'{func.__name__}({fargs})', end='', flush=True)

    try:
        res = func(*args)
        print(f' = {str(res)[:limit]}')
    except Exception:
        print(' raises:')
        traceback.print_exc()


def print_class(cls, args, limit=1024):
    fargs = format_args(args, limit)

    # Print and flush function name and arguments before calling the
    # function since it may crash.
    print(f'{cls.__name__}({fargs})', end='', flush=True)

    try:
        res = cls(*args)
        print(f' = {str(res)[:limit]}')
    except Exception:
        print(' raises:')
        traceback.print_exc()
