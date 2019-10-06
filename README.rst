|buildstatus|_

About
=====

Use `libFuzzer`_ to fuzz test Python 3.6+ C extension modules.

Ideas
=====

- Use type annotations for less type errors in generic mutator.

- Add support to fuzz test pure Python modules by generating C code
  from them using Cython.

Installation
============

`clang 8` or later is required.

.. code-block:: text

   $ apt install clang
   $ pip install pyfuzzer

Example Usage
=============

Use the default mutator ``pyfuzzer.mutators.random`` when testing the
module ``hello_world``.

.. code-block:: text

   $ cd examples/hello_world
   $ pyfuzzer hello_world hello_world.c
   clang -fprofile-instr-generate -fcoverage-mapping -g -fsanitize=fuzzer -fsanitize=signed-integer-overflow -fno-sanitize-recover=all -I/usr/include/python3.7m hello_world.c module.c /home/erik/workspace/pyfuzzer/pyfuzzer/pyfuzzer.c -Wl,-Bsymbolic-functions -Wl,-z,relro -lpython3.7m -o hello_world
   rm -f hello_world.profraw
   ./hello_world corpus -max_total_time=1 -max_len=4096
   INFO: Seed: 747042709
   INFO: Loaded 1 modules   (23 inline 8-bit counters): 23 [0x47446d, 0x474484),
   INFO: Loaded 1 PC tables (23 PCs): 23 [0x461790,0x461900),
   INFO:        4 files found in corpus
   Importing module under test... done.
   Importing custom mutator... failed.
   ModuleNotFoundError: No module named 'mutator'
   Importing mutator 'pyfuzzer.mutators.random'... done.
   Finding function 'test_one_input' in mutator... done.
   INFO: seed corpus: files: 4 min: 1b max: 4b total: 10b rss: 44Mb
   #5	INITED cov: 11 ft: 12 corp: 4/10b lim: 4 exec/s: 0 rss: 44Mb
   #784855	DONE   cov: 11 ft: 12 corp: 4/10b lim: 4096 exec/s: 392427 rss: 44Mb
   Done 784855 runs in 2 second(s)
   llvm-profdata merge -sparse hello_world.profraw -o hello_world.profdata
   llvm-cov show hello_world -instr-profile=hello_world.profdata -ignore-filename-regex=/usr/include|pyfuzzer.c|module.c
       1|       |#include <Python.h>
       2|       |
       3|       |PyDoc_STRVAR(
       4|       |    tell_doc,
       5|       |    "tell(message)\n"
       6|       |    "--\n"
       7|       |    "Arguments: (message:bytes)\n");
       8|       |
       9|       |static PyObject *m_tell(PyObject *module_p, PyObject *message_p)
      10|   784k|{
      11|   784k|    Py_ssize_t size;
      12|   784k|    char* buf_p;
      13|   784k|    int res;
      14|   784k|    PyObject *res_p;
      15|   784k|
      16|   784k|    res = PyBytes_AsStringAndSize(message_p, &buf_p, &size);
      17|   784k|
      18|   784k|    if (res != -1) {
      19|   784k|        switch (size) {
      20|   784k|
      21|   784k|        case 0:
      22|  35.7k|            res_p = PyLong_FromLong(5);
      23|  35.7k|            break;
      24|   784k|
      25|   784k|        case 1:
      26|  81.8k|            res_p = PyBool_FromLong(1);
      27|  81.8k|            break;
      28|   784k|
      29|   784k|        case 2:
      30|  85.5k|            res_p = PyBytes_FromString("Hello!");
      31|  85.5k|            break;
      32|   784k|
      33|   784k|        default:
      34|   581k|            res_p = PyLong_FromLong(0);
      35|   581k|            break;
      36|      0|        }
      37|      0|    } else {
      38|      0|        Py_INCREF(Py_None);
      39|      0|        res_p = Py_None;
      40|      0|    }
      41|   784k|
      42|   784k|    return (res_p);
      43|   784k|}
      44|       |
      45|       |static struct PyMethodDef methods[] = {
      46|       |    { "tell", m_tell, METH_O, tell_doc},
      47|       |    { NULL }
      48|       |};
      49|       |
      50|       |static PyModuleDef module = {
      51|       |    PyModuleDef_HEAD_INIT,
      52|       |    .m_name = "hello_world",
      53|       |    .m_size = -1,
      54|       |    .m_methods = methods
      55|       |};
      56|       |
      57|       |PyMODINIT_FUNC PyInit_hello_world(void)
      58|      1|{
      59|      1|    return (PyModule_Create(&module));
      60|      1|}

Use the custom mutator ``hello_world_mutator`` when testing the module
``hello_world``.

Testing with a custom mutator is often more efficient than using a
generic one.

.. code-block:: text

   $ cd examples/hello_world_custom_mutator
   $ pyfuzzer -m hello_world_mutator.py hello_world hello_world.c
   ...

Mutators
========

A Mutator uses data from `libFuzzer`_ to test a module. A mutator must
implement the function ``test_one_input(module, data)``, where
``module`` is the module under test and ``data`` is the data generated
by `libFuzzer`_ (as a bytes object).

A minimal mutator fuzz testing a CRC-32 algorithm could look like
below. It simply calls ``crc_32()`` with ``data`` as its only
argument.

.. code-block:: python

   def test_one_input(module, data):
       module.crc_32(data)


.. |buildstatus| image:: https://travis-ci.org/eerimoq/pyfuzzer.svg
.. _buildstatus: https://travis-ci.org/eerimoq/pyfuzzer

.. _libFuzzer: https://llvm.org/docs/LibFuzzer.html
