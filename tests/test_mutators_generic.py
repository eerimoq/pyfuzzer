import sys
import unittest
from unittest.mock import patch
import struct
from io import StringIO

from pyfuzzer.mutators.generic import test_one_input
from pyfuzzer.mutators.generic import test_one_input_print

from . import c_extension


class MutatorsGenericTest(unittest.TestCase):

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
            (b'\x00\x03\x00' + struct.pack('>q', 2) + struct.pack('>q', 3), -1)
        ]

        for data, res in datas:
            self.assertEqual(test_one_input(c_extension, data), res)

    def test_test_one_input_print(self):
        datas = [
            (b'\x00\x00\x01\x02'
             + b'\x00' + struct.pack('>q', 1)
             + b'\x00' + struct.pack('>q', 2)),
            b'\x00\x01\x00',
            b'\x00\x02\x00'
        ]

        stdout = StringIO()

        with patch('sys.stdout', stdout):
            for data in datas:
                test_one_input_print(c_extension, data)

        self.assertEqual(stdout.getvalue(),
                         '    add(1, 2) = 3\n'
                         "    func_0() = 'func 0'\n"
                         "    func_1() = 'func 1'\n")


if __name__ == '__main__':
    unittest.main()
