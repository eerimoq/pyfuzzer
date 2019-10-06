import traceback


def print_function(func, args):
    sargs = []

    for arg in args:
        if isinstance(arg, str):
            arg = f"'{arg}'"
        else:
            arg = str(arg)

        sargs.append(arg)

    fargs = ', '.join(sargs)

    try:
        res = func(*args)
        print(f'{func.__name__}({fargs}) = {res}')
    except Exception:
        print(f'{func.__name__}({fargs}) raises:')
        traceback.print_exc()
