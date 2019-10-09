import traceback
import struct
import inspect
from io import BytesIO


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


def generate_list(data):
    return generate_args(None, data)


def generate_dict(data):
    return {value: value for value in generate_args(None, data)}


def get_signature(callable):
    """Get the signature for given callable.

    """

    try:
        return inspect.signature(callable)
    except Exception as e:
        return None


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


class Mutator:

    def __init__(self, module):
        self._module = module
        self._functions = None
        self._classes = None
        self._attribute_kind = {
            0: self.test_one_function,
            1: self.test_one_class
        }
        self._attribute_kind_print = {
            0: self.test_one_function_print,
            1: self.test_one_class_print
        }

    def lookup_function(self, value):
        if self._functions is None:
            self._functions = lookup_functions(self._module)

            if len(self._functions) > 256:
                print('More than 256 functions.')
                sys.exit(1)

        return self._functions[value % len(self._functions)]

    def lookup_class(self, value):
        if self._classes is None:
            self._classes = lookup_classes(self._module)

            if len(self._classes) > 256:
                print('More than 256 classes.')
                sys.exit(1)

        return self._classes[value % len(self._classes)]

    def test_one_function(self, data):
        func, signature = self.lookup_function(data.read(1)[0])
        args = generate_args(signature, data)

        return func(*args)

    def test_one_class(self, data):
        cls, signature, methods = self.lookup_class(data.read(1)[0])
        args = generate_args(signature, data)
        obj = cls(*args)

        for _ in range(data.read(1)[0]):
            method, signature = methods[data.read(1)[0] % len(methods)]
            method(obj, *generate_args(signature, data))

        return obj

    def test_one_function_print(self, data):
        func, signature = self.lookup_function(data.read(1)[0])
        args = generate_args(signature, data)
        print_callable(func, args, 4 * ' ')


    def test_one_class_print(self, data):
        cls, signature, methods = self.lookup_class(data.read(1)[0])
        args = generate_args(signature, data)
        obj = print_callable(cls, args, 4 * ' ')

        if obj is None:
            return

        for _ in range(data.read(1)[0]):
            method, signature = methods[data.read(1)[0] % len(methods)]
            print_callable(method,
                           [obj, *generate_args(signature, data)],
                           8 * ' ')

    def test_one_input(self, data):
        kind = data.read(1)[0]

        return self._attribute_kind[kind % len(self._attribute_kind)](data)

    def test_one_input_print(self, data):
        kind = data.read(1)[0]
        self._attribute_kind_print[kind % len(self._attribute_kind_print)](data)


MUTATOR = None


def test_one_input(module, data):
    global MUTATOR

    if MUTATOR is None:
        MUTATOR = Mutator(module)

    return MUTATOR.test_one_input(BytesIO(data))


def test_one_input_print(module, data):
    global MUTATOR

    if MUTATOR is None:
        MUTATOR = Mutator(module)

    MUTATOR.test_one_input_print(BytesIO(data))
