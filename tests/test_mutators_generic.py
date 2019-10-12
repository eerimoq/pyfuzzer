import sys
import unittest
from unittest.mock import patch
import struct
from io import StringIO
import re

from pyfuzzer.mutators.generic import setup

from . import c_extension


class MutatorsGenericTest(unittest.TestCase):

    maxDiff = None
    
    def test_test_one_input(self):
        datas = [
            # add(1, 2) -> 3
            (b'\x00\x00\x01\x02'
             + b'\x00' + struct.pack('>q', 1)
             + b'\x00' + struct.pack('>q', 2), 3),
            # add(1, 2) -> 3 using signature.
            (b'\x00\x00\x00'
             + b'\x00' + struct.pack('>q', 1)
             + b'\x00' + struct.pack('>q', 2), 3),
            # func_0()
            (b'\x00\x01\x00', 'func 0'),
            # func_1()
            (b'\x00\x02\x00', 'func 1'),
            # sub(2, 3) -> -1 using signature and annotations.
            (b'\x00\x04\x00' + struct.pack('>q', 2) + struct.pack('>q', 3), -1)
        ]

        mutator = setup(c_extension)

        for data, res in datas:
            self.assertEqual(mutator.test_one_input(data), res)

    def test_test_one_input_print(self):
        datas = [
            (b'\x00\x00\x01\x02'
             + b'\x00' + struct.pack('>q', 1)
             + b'\x00' + struct.pack('>q', 2)),
            b'\x00\x01\x00',
            b'\x00\x02\x00'
        ]

        stdout = StringIO()
        mutator = setup(c_extension)

        with patch('sys.stdout', stdout):
            for data in datas:
                mutator.test_one_input_print(data, colors=False)

        self.assertEqual(stdout.getvalue(),
                         '    add(1, 2) = 3\n'
                         "    func_0() = 'func 0'\n"
                         "    func_1() = 'func 1'\n")

    def test_test_one_input_counter(self):
        mutator = setup(c_extension)

        # counter = Counter()
        # counter.get() = 0
        # counter.increment(1)
        # counter.decrement(2)
        # counter.get() = -1
        mutator.test_one_input(
            b'\x01\x00\x00\x04'
            b'\x01\x00'
            b'\x02\x00\x00' + b'\x00\x00\x00\x00\x00\x00\x00\x01'
            b'\x03\x00\x00' + b'\x00\x00\x00\x00\x00\x00\x00\x02'
            b'\x01\x00'
        )

    def test_test_one_input_print_counter(self):
        stdout = StringIO()
        mutator = setup(c_extension)

        with patch('sys.stdout', stdout):
            mutator.test_one_input_print(
                b'\x01\x00\x00\x04'
                b'\x01\x00'
                b'\x02\x00\x00' + b'\x00\x00\x00\x00\x00\x00\x00\x01'
                b'\x03\x00\x00' + b'\x00\x00\x00\x00\x00\x00\x00\x02'
                b'\x01\x00',
                colors=False)

        output = re.sub(r'object at 0x[0-9a-f]+',
                        'object at <address>',
                        stdout.getvalue())

        self.assertEqual(
            output,
            "    Counter() = <tests.c_extension.Counter object at <address>>\n"
            "        get(<tests.c_extension.Counter object at <address>>) = 0\n"
            "        increment(<tests.c_extension.Counter object at <address>>, 1) = None\n"
            "        decrement(<tests.c_extension.Counter object at <address>>, 2) = None\n"
            "        get(<tests.c_extension.Counter object at <address>>) = -1\n")

    def test_test_one_input_noop(self):
        datas = [
            # int
            (b'\x00\x03\x01\x01' + b'\x00' + struct.pack('>q', 5), 5),
            # bool
            (b'\x00\x03\x01\x01' + b'\x01\xff', True),
            # str
            (b'\x00\x03\x01\x01' + b'\x02\x03\x31\x32\x33', '123'),
            # bytes
            (b'\x00\x03\x01\x01' + b'\x03\x03\x31\x32\x33', b'123'),
            # None
            (b'\x00\x03\x01\x01' + b'\x04', None),
            # list
            (b'\x00\x03\x01\x01' + b'\x05\x00', []),
            # dict
            (b'\x00\x03\x01\x01' + b'\x06\x00', {}),
            # bytearray
            (b'\x00\x03\x01\x01' + b'\x07\x03', bytearray(b'\x00\x00\x00'))
        ]

        mutator = setup(c_extension)

        for data, res in datas:
            self.assertEqual(mutator.test_one_input(data), res)

    def test_test_one_input_print_noop(self):
        datas = [
            # int
            b'\x00\x03\x01\x01' + b'\x00' + struct.pack('>q', 5),
            # bool
            b'\x00\x03\x01\x01' + b'\x01\xff',
            # str
            b'\x00\x03\x01\x01' + b'\x02\x03\x31\x32\x33',
            # bytes
            b'\x00\x03\x01\x01' + b'\x03\x03\x31\x32\x33',
            # None
            b'\x00\x03\x01\x01' + b'\x04',
            # list
            b'\x00\x03\x01\x01' + b'\x05\x00',
            # dict
            b'\x00\x03\x01\x01' + b'\x06\x00',
            # bytearray
            b'\x00\x03\x01\x01' + b'\x07\x03'
        ]

        stdout = StringIO()
        mutator = setup(c_extension)

        with patch('sys.stdout', stdout):
            for data in datas:
                mutator.test_one_input_print(data, colors=False)

        self.assertEqual(
            stdout.getvalue(),
            "    noop(5) = 5\n"
            "    noop(True) = True\n"
            "    noop('123') = '123'\n"
            "    noop(b'123') = b'123'\n"
            "    noop(None) = None\n"
            "    noop([]) = []\n"
            "    noop({}) = {}\n"
            "    noop(bytearray(b'\\x00\\x00\\x00')) = bytearray(b'\\x00\\x00\\x00')\n")


if __name__ == '__main__':
    unittest.main()
