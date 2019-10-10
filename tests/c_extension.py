class Counter:

    def __init__(self):
        self._counter = 0

    def get(self):
        return self._counter

    def increment(self, value):
        self._counter += value

    def decrement(self, value):
        self._counter -= value


def add(a, b):
    return a + b


def func_0():
    return 'func 0'


def func_1():
    return 'func 1'


def noop(v):
    return v


def sub(a: int, b: int):
    return a - b
