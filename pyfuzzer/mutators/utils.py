import traceback


def print_function(func, args):
    fargs = ', '.join([str(arg) for arg in args])

    try:
        res = func(*args)
        print(f'{func.__name__}({fargs}) = {res}')
    except Exception:
        print(f'{func.__name__}({fargs}) raises:')
        traceback.print_exc()
