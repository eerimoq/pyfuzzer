|buildstatus|_

About
=====

!!! UNDER CONSTRUCTION - DO NOT USE !!!

Use `libFuzzer`_ to fuzz test Python 3.6+ C extension modules.

Ideas
=====

- Use type annotations for less type errors in generic mutator.

- Add support to fuzz test pure Python modules by generating C code
  from them using Cython.

Installation
============

.. code-block:: text

   $ apt install clang
   $ pip install pyfuzzer

Example Usage
=============

Use the default generic mutator when testing the module hello_world.

.. code-block:: text

   $ cd examples/hello_world
   $ pyfuzzer hello_world hello_world.c
   clang -fprofile-instr-generate -fcoverage-mapping -g -fsanitize=fuzzer -fsanitize=signed-integer-overflow -fno-sanitize-recover=all -I/usr/include/python3.7m hello_world.c module.c /home/erik/workspace/pyfuzzer/pyfuzzer/pyfuzzer.c -Wl,-Bsymbolic-functions -Wl,-z,relro -lpython3.7m -o hello_world
   rm -f hello_world.profraw
   ./hello_world -max_total_time=1 -max_len=4096
   INFO: Seed: 1479758674
   INFO: Loaded 1 modules   (22 inline 8-bit counters): 22 [0x47446d, 0x474483),
   INFO: Loaded 1 PC tables (22 PCs): 22 [0x4616e0,0x461840),
   ModuleNotFoundError: No module named 'mutator'
   INFO: A corpus is not provided, starting from an empty corpus
   #2	INITED cov: 7 ft: 8 corp: 1/1b lim: 4 exec/s: 0 rss: 44Mb
   #10	NEW    cov: 8 ft: 9 corp: 2/3b lim: 4 exec/s: 0 rss: 44Mb L: 2/2 MS: 3 ChangeByte-ChangeBit-CopyPart-
   #11	NEW    cov: 9 ft: 10 corp: 3/6b lim: 4 exec/s: 0 rss: 44Mb L: 3/3 MS: 1 CopyPart-
   #23	NEW    cov: 10 ft: 11 corp: 4/10b lim: 4 exec/s: 0 rss: 44Mb L: 4/4 MS: 2 CopyPart-CrossOver-
   #1044738	DONE   cov: 10 ft: 11 corp: 4/10b lim: 4096 exec/s: 522369 rss: 44Mb
   Done 1044738 runs in 2 second(s)
   llvm-profdata merge -sparse hello_world.profraw -o hello_world.profdata
   llvm-cov show hello_world -instr-profile=hello_world.profdata -ignore-filename-regex=\.h|pyfuzzer.c|module.c
       1|       |#include <Python.h>
       2|       |
       3|       |PyDoc_STRVAR(
       4|       |    tell_doc,
       5|       |    "tell(message)\n"
       6|       |    "--\n"
       7|       |    "Arguments: (message:bytes)\n");
       8|       |
       9|       |static PyObject *m_tell(PyObject *module_p, PyObject *message_p)
      10|  1.04M|{
      11|  1.04M|    Py_ssize_t size;
      12|  1.04M|    char* buf_p;
      13|  1.04M|    int res;
      14|  1.04M|    PyObject *res_p;
      15|  1.04M|
      16|  1.04M|    res = PyBytes_AsStringAndSize(message_p, &buf_p, &size);
      17|  1.04M|
      18|  1.04M|    if (res != -1) {
      19|  1.04M|        switch (size) {
      20|  1.04M|
      21|  1.04M|        case 0:
      22|  47.6k|            res_p = PyLong_FromLong(5);
      23|  47.6k|            break;
      24|  1.04M|
      25|  1.04M|        case 1:
      26|   107k|            res_p = PyBool_FromLong(1);
      27|   107k|            break;
      28|  1.04M|
      29|  1.04M|        case 2:
      30|   114k|            res_p = PyBytes_FromString("Hello!");
      31|   114k|            break;
      32|  1.04M|
      33|  1.04M|        default:
      34|   774k|            res_p = PyLong_FromLong(0);
      35|   774k|            break;
      36|      0|        }
      37|      0|    } else {
      38|      0|        Py_INCREF(Py_None);
      39|      0|        res_p = Py_None;
      40|      0|    }
      41|  1.04M|
      42|  1.04M|    return (res_p);
      43|  1.04M|}
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

Use a custom mutator when testing the module hello_world.

Testing with a custom mutator is often more efficient then using a
generic.

.. code-block:: text

   $ cd examples/hello_world
   $ pyfuzzer -m mutator.py hello_world hello_world.c
   ...

.. |buildstatus| image:: https://travis-ci.org/eerimoq/pyfuzzer.svg
.. _buildstatus: https://travis-ci.org/eerimoq/pyfuzzer

.. _libFuzzer: https://llvm.org/docs/LibFuzzer.html
