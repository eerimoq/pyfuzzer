import sys
import inspect
from io import BytesIO
import struct

from .utils import print_callable


FUNCS = None
NUMBER_OF_FUNCS = 0

CLASSES = None
NUMBER_OF_CLASSES = 0


def generate_integer(data):
    return struct.unpack('>q', data.read(8))[0]


def generate_bool(data):
    return bool(data.read(1)[0])


def generate_string(data):
    return str(data.read(data.read(1)[0]))[2:-1]


def generate_bytes(data):
    return data.read(data.read(1)[0])


def generate_none(_data):
    return None


def generate_list(data):
    return generate_args(data)


def generate_dict(data):
    return {value: value for value in generate_args(data)}


def generate_bytearray(data):
    return bytearray(data.read(1)[0])


DATA_KINDS = {
    0: generate_integer,
    1: generate_bool,
    2: generate_string,
    3: generate_bytes,
    4: generate_none,
    5: generate_list,
    6: generate_dict,
    7: generate_bytearray
}


def is_function(member):
    return inspect.isbuiltin(member) or inspect.isfunction(member)


def lookup_function(module, value):
    global FUNCS
    global NUMBER_OF_FUNCS

    if FUNCS is None:
        FUNCS = [
            m[1] for m in inspect.getmembers(module, is_function)
        ]
        NUMBER_OF_FUNCS = len(FUNCS)

        if NUMBER_OF_FUNCS > 256:
            print('More than 256 functions.')
            sys.exit(1)

    return FUNCS[value % NUMBER_OF_FUNCS]


def lookup_class_methods(cls):
    return [
        m[1]
        for m in inspect.getmembers(cls)
        if m[0][0] != '_'
    ]


def lookup_class(module, value):
    global CLASSES
    global NUMBER_OF_CLASSES

    if CLASSES is None:
        CLASSES = [
            (cls, lookup_class_methods(cls))
            for _, cls in inspect.getmembers(module, inspect.isclass)
        ]
        NUMBER_OF_CLASSES = len(CLASSES)

        if NUMBER_OF_CLASSES > 256:
            print('More than 256 classes.')
            sys.exit(1)

    return CLASSES[value % NUMBER_OF_CLASSES]


def generate_args(data):
    args = []
    number_of_args = data.read(1)[0]

    try:
        for _ in range(number_of_args):
            args.append(DATA_KINDS[data.read(1)[0] % len(DATA_KINDS)](data))
    except Exception:
        pass

    return args


def test_one_function(module, data):
    func = lookup_function(module, data.read(1)[0])
    args = generate_args(data)

    return func(*args)


def test_one_class(module, data):
    cls, methods = lookup_class(module, data.read(1)[0])
    args = generate_args(data)
    obj = cls(*args)

    for _ in range(data.read(1)[0]):
        method = methods[data.read(1)[0] % len(methods)]
        method(obj, *generate_args(data))

    return obj


ATTRIBUTE_KIND = {
    0: test_one_function,
    1: test_one_class
}


def test_one_function_print(module, data):
    func = lookup_function(module, data.read(1)[0])
    print('test_one_function_print')
    args = generate_args(data)
    print_callable(func, args, 4 * ' ')


def test_one_class_print(module, data):
    cls, methods = lookup_class(module, data.read(1)[0])
    args = generate_args(data)
    obj = print_callable(cls, args, 4 * ' ')

    if obj is None:
        return

    for _ in range(data.read(1)[0]):
        method = methods[data.read(1)[0] % len(methods)]
        print_callable(method,
                       [obj, *generate_args(data)],
                       8 * ' ')


ATTRIBUTE_KIND_PRINT = {
    0: test_one_function_print,
    1: test_one_class_print
}


def test_one_input(module, data):
    # C extension functions can not have type annotations. Can be part
    # of function documentation though.
    #
    # print(inspect.signature(func))
    #
    # print(func.__doc__)

    data = BytesIO(data)
    kind = data.read(1)[0]

    return ATTRIBUTE_KIND[kind % len(ATTRIBUTE_KIND)](module, data)


def test_one_input_print(module, data):
    data = BytesIO(data)
    kind = data.read(1)[0]
    ATTRIBUTE_KIND_PRINT[kind % len(ATTRIBUTE_KIND_PRINT)](module, data)
