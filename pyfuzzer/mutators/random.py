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


DATA_KINDS = {
    0: generate_integer,
    1: generate_bool,
    2: generate_string,
    3: generate_bytes,
    4: generate_none
}


def lookup_function(module, value):
    global FUNCS
    global NUMBER_OF_FUNCS

    if FUNCS is None:
        FUNCS = [
            m[1] for m in inspect.getmembers(module, inspect.isbuiltin)
        ]
        NUMBER_OF_FUNCS = len(FUNCS)

        if NUMBER_OF_FUNCS > 256:
            print('More than 256 functions.')
            sys.exit(1)

    return FUNCS[value % NUMBER_OF_FUNCS]


def lookup_class(module, value):
    global CLASSES
    global NUMBER_OF_CLASSES

    if CLASSES is None:
        CLASSES = [
            m[1] for m in inspect.getmembers(module, inspect.isclass)
        ]
        NUMBER_OF_CLASSES = len(CLASSES)

        if NUMBER_OF_CLASSES > 256:
            print('More than 256 classes.')
            sys.exit(1)

    return CLASSES[value % NUMBER_OF_CLASSES]


def generate_args(data):
    args = []
    number_of_args = data.read(1)[0]

    for _ in range(number_of_args):
        args.append(DATA_KINDS[data.read(1)[0]](data))

    return args


def test_one_function(module, data):
    func = lookup_function(module, data.read(1)[0])
    args = generate_args(data)
    func(*args)


def test_one_class(module, data):
    cls = lookup_class(module, data.read(1)[0])
    args = generate_args(data)
    cls(*args)


ATTRIBUTE_KIND = {
    0: test_one_function,
    1: test_one_class
}


def test_one_function_print(module, data):
    func = lookup_function(module, data.read(1)[0])
    args = generate_args(data)
    print_callable(func, args)


def test_one_class_print(module, data):
    cls = lookup_class(module, data.read(1)[0])
    args = generate_args(data)
    print_callable(cls, args)


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
    ATTRIBUTE_KIND[kind](module, data)


def test_one_input_print(module, data):
    data = BytesIO(data)
    kind = data.read(1)[0]
    ATTRIBUTE_KIND_PRINT[kind](module, data)
