import traceback
import struct
import inspect


def format_value(value, limit):
    if isinstance(value, str):
        value = f"'{value}'"
    else:
        value = str(value)

    return value[:limit]


def format_args(args, limit):
    """Returns a comma separated list of given arguemnts. Each argument is
    at most ``limit`` characters.

    """

    return ', '.join([format_value(arg, limit) for arg in args])


def print_callable(obj, args, indent, limit=1024):
    """Print given callable name and its arguments, call it and then print
    the returned value or raised exception.

    """

    fargs = format_args(args, limit)

    # Print and flush callable name and arguments before calling it
    # since it may crash.
    print(f'{indent}{obj.__name__}({fargs})', end='', flush=True)

    try:
        res = obj(*args)
        print(f' = {format_value(res, limit)}')
    except Exception:
        res = None
        print(' raises:')

        for line in traceback.format_exc().splitlines():
            print(f'{indent}{line}')

    return res


def generate_integer(data):
    return struct.unpack('>q', data.read(8))[0]


def generate_bool(data):
    return bool(data.read(1)[0])


def generate_string(data):
    return str(data.read(data.read(1)[0]))[2:-1]


def generate_bytes(data):
    return data.read(data.read(1)[0])


def generate_bytearray(data):
    return bytearray(data.read(1)[0])


def generate_none(_data):
    return None


def get_signature(callable):
    """Get the signature for given callable.

    """

    try:
        return inspect.signature(callable)
    except Exception as e:
        return None


def is_function(member):
    return inspect.isbuiltin(member) or inspect.isfunction(member)


def lookup_functions(module):
    return [
        (m[1], get_signature(m[1]))
        for m in inspect.getmembers(module, is_function)
    ]


def lookup_class_methods(cls):
    return [
        (m[1], get_signature(m[1]))
        for m in inspect.getmembers(cls)
        if m[0][0] != '_'
    ]


def lookup_classes(module):
    return [
        (cls, get_signature(cls), lookup_class_methods(cls))
        for _, cls in inspect.getmembers(module, inspect.isclass)
    ]
