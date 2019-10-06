import traceback


def print_function(func, args, limit=1024):
    sargs = []

    for arg in args:
        if isinstance(arg, str):
            arg = f"'{arg}'"
        else:
            arg = str(arg)

        sargs.append(arg[:limit])

    fargs = ', '.join(sargs)

    try:
        res = func(*args)
        print(f'{func.__name__}({fargs}) = {str(res)[:limit]}')
    except Exception:
        print(f'{func.__name__}({fargs}) raises:')
        traceback.print_exc()
