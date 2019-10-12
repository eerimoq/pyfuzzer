import traceback
import struct
import inspect
from io import BytesIO

from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatter import Formatter
from pygments.token import Name
from pygments.token import String
from pygments.token import Operator
from pygments.token import Literal
from pygments.token import Punctuation
from pygments.token import Text


def format_value(value, limit):
    if isinstance(value, str):
        value = f"'{value}'"[:limit]

        if value[-1] != "'":
            value += "...'"
    elif isinstance(value, bytes):
        value = str(value)[:limit]

        if value[-1] != "'":
            value += "...'"
    elif isinstance(value, bytearray):
        value = str(value)[:limit]

        if value[-2] != "'":
            value += "...'"

        if value[-1] != ")":
            value += ")"
    else:
        value = str(value)[:limit]

    return value


def format_args(args, limit):
    """Returns a comma separated list of given arguemnts. Each argument is
    at most ``limit`` characters.

    """

    return ', '.join([format_value(arg, limit) for arg in args])


RESET = '\033[0m'
RED_BOLD = '\033[1;31m'
GREEN = '\033[1;32m'
YELLOW = '\033[0;33m'
YELLOW_BOLD = '\033[1;33m'
MAGENTA = '\033[0;35m'
MAGENTA_BOLD = '\033[1;35m'
CYAN = '\033[0;36m'


class DefaultFormatter(Formatter):

    COLOR_MAP = {
        Name: CYAN,
        String: MAGENTA,
        Literal.Number.Integer: GREEN,
        Literal.String.Single: MAGENTA,
        Punctuation: YELLOW,
        Operator: YELLOW_BOLD,
        Literal.String.Affix: CYAN,
        Literal.String.Escape: MAGENTA,
        Name.Builtin: CYAN,
        Name.Builtin.Pseudo: YELLOW
    }

    def format(self, tokens, fout):
        for kind, value in tokens:
            if value == '\n':
                continue

            try:
                color = self.COLOR_MAP[kind]
            except KeyError:
                # print(kind)
                color = RESET

            fout.write(f'{color}{value}{RESET}')


class TracebackFormatter(Formatter):

    COLOR_MAP = {
        Literal.Number.Integer: MAGENTA_BOLD,
        Literal.String.Double: CYAN,
        Text: GREEN,
        Name.Exception: RED_BOLD
    }

    def format(self, tokens, fout):
        tokens = list(tokens)

        if tokens[1][1] == 'File':
            self.format_location(tokens, fout)
        elif tokens[1][0] == Name.Exception:
            self.format_exception(tokens, fout)
        else:
            self.format_none(tokens, fout)

    def format_location(self, tokens, fout):
        for kind, value in tokens[:-2]:
            try:
                color = self.COLOR_MAP[kind]
            except KeyError:
                color = RESET

            fout.write(f'{color}{value}{RESET}')

        fout.write(f'{CYAN}{tokens[-2][1]}{RESET}')

    def format_exception(self, tokens, fout):
        fout.write(tokens[0][1])
        fout.write(f'{RED_BOLD}{tokens[1][1]}{RESET}')
        fout.write(tokens[2][1])

        for kind, value in tokens[3:-1]:
            fout.write(f'{CYAN}{value}{RESET}')

    def format_none(self, tokens, fout):
        for kind, value in tokens[:-1]:
            fout.write(value)


def colorize(code, colors):
    if colors:
        code = highlight(code, PythonLexer(), DefaultFormatter())

    return code


def colorize_traceback(code, colors):
    if colors:
        code = highlight(code, PythonLexer(), TracebackFormatter())

    return code


def print_callable(obj, args, indent='    ', limit=1024, colors=True):
    """Print given callable name and its arguments, call it and then print
    the returned value or raised exception.

    """

    fargs = format_args(args, limit)

    # Print and flush callable name and arguments before calling it
    # since it may crash.
    print(colorize(f'{indent}{obj.__name__}({fargs})', colors), end='', flush=True)

    try:
        res = obj(*args)
        print(colorize(f' = {format_value(res, limit)}', colors))
    except Exception:
        res = None
        print()

        for line in traceback.format_exc().splitlines():
            print(colorize_traceback(f'{indent}{line}', colors))

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
    """Get the signature of given callable.

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


def generate_args(signature, data, is_method=False):
    args = []
    number_of_args = data.read(1)[0]

    try:
        if signature is None:
            for _ in range(number_of_args):
                args.append(DATA_KINDS[data.read(1)[0] % len(DATA_KINDS)](data))
        else:
            if number_of_args == 0:
                for parameter in signature.parameters.values():
                    # Skip first parameter (self) for methods.
                    if is_method:
                        is_method = False
                        continue

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
        self._attribute_kind = {
            0: self.test_one_function,
            1: self.test_one_class
        }
        self._attribute_kind_print = {
            0: self.test_one_function_print,
            1: self.test_one_class_print
        }
        self._functions = lookup_functions(module)
        self._classes = lookup_classes(module)

    def test_one_input(self, data):
        data = BytesIO(data)
        kind = (data.read(1)[0] % len(self._attribute_kind))

        return self._attribute_kind[kind](data)

    def test_one_input_print(self, data, colors=True):
        data = BytesIO(data)
        kind = (data.read(1)[0] % len(self._attribute_kind_print))
        self._attribute_kind_print[kind](data, colors)

    def test_one_function(self, data):
        func, signature = self._functions[data.read(1)[0] % len(self._functions)]
        args = generate_args(signature, data)

        return func(*args)

    def test_one_class(self, data):
        cls, signature, methods = self._classes[data.read(1)[0] % len(self._classes)]
        args = generate_args(signature, data)
        obj = cls(*args)

        for _ in range(data.read(1)[0]):
            method, signature = methods[data.read(1)[0] % len(methods)]
            method(obj, *generate_args(signature, data, True))

        return obj

    def test_one_function_print(self, data, colors=True):
        func, signature = self._functions[data.read(1)[0] % len(self._functions)]
        args = generate_args(signature, data)
        print_callable(func, args, colors=colors)

    def test_one_class_print(self, data, colors=True):
        cls, signature, methods = self._classes[data.read(1)[0] % len(self._classes)]
        args = generate_args(signature, data)
        obj = print_callable(cls, args, colors=colors)

        if obj is None:
            return

        for _ in range(data.read(1)[0]):
            method, signature = methods[data.read(1)[0] % len(methods)]
            print_callable(method,
                           [obj, *generate_args(signature, data, True)],
                           8 * ' ',
                           colors=colors)


def setup(module):
    return Mutator(module)
