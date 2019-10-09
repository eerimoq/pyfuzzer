import sys
import inspect
from io import BytesIO
import struct

from .utils import print_callable
from .utils import generate_integer
from .utils import generate_bool
from .utils import generate_bytes
from .utils import generate_bytearray
from .utils import generate_string
from .utils import generate_none
from .utils import lookup_functions
from .utils import lookup_classes


FUNCS = None
NUMBER_OF_FUNCS = 0

CLASSES = None
NUMBER_OF_CLASSES = 0


def generate_list(data):
    return generate_args(None, data)


def generate_dict(data):
    return {value: value for value in generate_args(None, data)}


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


def lookup_function(module, value):
    global FUNCS
    global NUMBER_OF_FUNCS

    if FUNCS is None:
        FUNCS = lookup_functions(module)
        NUMBER_OF_FUNCS = len(FUNCS)

        if NUMBER_OF_FUNCS > 256:
            print('More than 256 functions.')
            sys.exit(1)

    return FUNCS[value % NUMBER_OF_FUNCS]


def lookup_class(module, value):
    global CLASSES
    global NUMBER_OF_CLASSES

    if CLASSES is None:
        CLASSES = lookup_classes(module)
        NUMBER_OF_CLASSES = len(CLASSES)

        if NUMBER_OF_CLASSES > 256:
            print('More than 256 classes.')
            sys.exit(1)

    return CLASSES[value % NUMBER_OF_CLASSES]


def generate_args(signature, data):
    args = []
    number_of_args = data.read(1)[0]

    try:
        if signature is None:
            for _ in range(number_of_args):
                args.append(DATA_KINDS[data.read(1)[0] % len(DATA_KINDS)](data))
        else:
            if number_of_args == 0:
                for parameter in signature.parameters.values():
                    if parameter.kind == inspect.Parameter.VAR_POSITIONAL:
                        args += generate_args(None, data)
                    else:
                        if parameter.annotation == int:
                            func = generate_integer
                        else:
                            func = DATA_KINDS[data.read(1)[0] % len(DATA_KINDS)]

                        args.append(func(data))
            else:
                number_of_args = data.read(1)[0]

                for _ in range(number_of_args):
                    args.append(DATA_KINDS[data.read(1)[0] % len(DATA_KINDS)](data))
    except (IndexError, TypeError, struct.error):
        pass

    return args


def test_one_function(module, data):
    func, signature = lookup_function(module, data.read(1)[0])
    args = generate_args(signature, data)

    return func(*args)


def test_one_class(module, data):
    cls, signature, methods = lookup_class(module, data.read(1)[0])
    args = generate_args(signature, data)
    obj = cls(*args)

    for _ in range(data.read(1)[0]):
        method, signature = methods[data.read(1)[0] % len(methods)]
        method(obj, *generate_args(signature, data))

    return obj


ATTRIBUTE_KIND = {
    0: test_one_function,
    1: test_one_class
}


def test_one_function_print(module, data):
    func, signature = lookup_function(module, data.read(1)[0])
    args = generate_args(signature, data)
    print_callable(func, args, 4 * ' ')


def test_one_class_print(module, data):
    cls, signature, methods = lookup_class(module, data.read(1)[0])
    args = generate_args(signature, data)
    obj = print_callable(cls, args, 4 * ' ')

    if obj is None:
        return

    for _ in range(data.read(1)[0]):
        method, signature = methods[data.read(1)[0] % len(methods)]
        print_callable(method,
                       [obj, *generate_args(signature, data)],
                       8 * ' ')


ATTRIBUTE_KIND_PRINT = {
    0: test_one_function_print,
    1: test_one_class_print
}


def test_one_input(module, data):
    data = BytesIO(data)
    kind = data.read(1)[0]

    return ATTRIBUTE_KIND[kind % len(ATTRIBUTE_KIND)](module, data)


def test_one_input_print(module, data):
    data = BytesIO(data)
    kind = data.read(1)[0]
    ATTRIBUTE_KIND_PRINT[kind % len(ATTRIBUTE_KIND_PRINT)](module, data)
