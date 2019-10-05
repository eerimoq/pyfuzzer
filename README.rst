|buildstatus|_

About
=====

!!! UNDER CONSTRUCTION - DO NOT USE !!!

Use `libFuzzer`_ to fuzz test Python C extension modules.

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
   $ pyfuzzer hello_world.c
   clang -fprofile-instr-generate -fcoverage-mapping -I/usr/include/python3.7m -g -fsanitize=fuzzer -fsanitize=signed-integer-overflow -fno-sanitize-recover=all hello_world.c module.c ../../pyfuzzer/pyfuzzer.c -lpython3.7m -o hello_world
   rm -f hello_world.profraw
   ./hello_world -max_total_time=5 -max_len=4096
   INFO: Seed: 2099947845
   INFO: Loaded 1 modules   (22 inline 8-bit counters): 22 [0x47444d, 0x474463),
   INFO: Loaded 1 PC tables (22 PCs): 22 [0x4616c0,0x461820),
   ModuleNotFoundError: No module named 'mutator'
   INFO: A corpus is not provided, starting from an empty corpus
   #2	INITED cov: 7 ft: 8 corp: 1/1b lim: 4 exec/s: 0 rss: 43Mb
   #8	NEW    cov: 8 ft: 9 corp: 2/3b lim: 4 exec/s: 0 rss: 43Mb L: 2/2 MS: 1 InsertByte-
   #10	NEW    cov: 9 ft: 10 corp: 3/6b lim: 4 exec/s: 0 rss: 43Mb L: 3/3 MS: 2 CopyPart-InsertByte-
   #11	NEW    cov: 10 ft: 11 corp: 4/10b lim: 4 exec/s: 0 rss: 43Mb L: 4/4 MS: 1 InsertByte-
   #1048576	pulse  cov: 10 ft: 11 corp: 4/10b lim: 4096 exec/s: 524288 rss: 43Mb
   #2097152	pulse  cov: 10 ft: 11 corp: 4/10b lim: 4096 exec/s: 699050 rss: 43Mb
   #3189296	DONE   cov: 10 ft: 11 corp: 4/10b lim: 4096 exec/s: 531549 rss: 43Mb
   Done 3189296 runs in 6 second(s)
   llvm-profdata merge -sparse hello_world.profraw -o hello_world.profdata
   llvm-cov show hello_world -instr-profile=hello_world.profdata
   /home/erik/workspace/pyfuzzer/examples/hello_world/hello_world.c:
       1|       |#include <Python.h>
       2|       |
       3|       |PyDoc_STRVAR(
       4|       |    tell_doc,
       5|       |    "tell(message)\n"
       6|       |    "--\n"
       7|       |    "Arguments: (message:bytes)\n");
       8|       |
       9|       |static PyObject *m_tell(PyObject *module_p, PyObject *message_p)
      10|  3.18M|{
      11|  3.18M|    Py_ssize_t size;
      12|  3.18M|    char* buf_p;
      13|  3.18M|    int res;
      14|  3.18M|    PyObject *res_p;
      15|  3.18M|
      16|  3.18M|    res = PyBytes_AsStringAndSize(message_p, &buf_p, &size);
      17|  3.18M|
      18|  3.18M|    if (res != -1) {
      19|  3.18M|        switch (size) {
      20|  3.18M|
      21|  3.18M|        case 0:
      22|   144k|            res_p = PyLong_FromLong(5);
      23|   144k|            break;
      24|  3.18M|
      25|  3.18M|        case 1:
      26|   328k|            res_p = PyBool_FromLong(1);
      27|   328k|            break;
      28|  3.18M|
      29|  3.18M|        case 2:
      30|   348k|            res_p = PyBytes_FromString("Hello!");
      31|   348k|            break;
      32|  3.18M|
      33|  3.18M|        default:
      34|  2.36M|            res_p = PyLong_FromLong(0);
      35|  2.36M|            break;
      36|      0|        }
      37|      0|    } else {
      38|      0|        Py_INCREF(Py_None);
      39|      0|        res_p = Py_None;
      40|      0|    }
      41|  3.18M|
      42|  3.18M|    return (res_p);
      43|  3.18M|}
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
   ...

Use a custom mutator when testing the module hello_world.

Testing with a custom mutator is often more efficient then using a
generic.

.. code-block:: text

   $ cd examples/hello_world
   $ pyfuzzer -m mutator.py hello_world.c
   ...

.. |buildstatus| image:: https://travis-ci.org/eerimoq/pyfuzzer.svg
.. _buildstatus: https://travis-ci.org/eerimoq/pyfuzzer

.. _libFuzzer: https://llvm.org/docs/LibFuzzer.html
