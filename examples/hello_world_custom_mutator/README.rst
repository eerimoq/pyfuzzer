About
=====

Fuzzy-test the ``hello_world`` module using the custom mutator
``hello_world_mutator.py``.

.. code-block:: text

   $ pyfuzzer run -m hello_world_mutator.py hello_world hello_world.c
   clang -fprofile-instr-generate -fcoverage-mapping -g -fsanitize=fuzzer -fsanitize=signed-integer-overflow -fno-sanitize-recover=all -I/usr/include/python3.7m hello_world.c module.c /home/erik/workspace/pyfuzzer/pyfuzzer/pyfuzzer.c -Wl,-Bsymbolic-functions -Wl,-z,relro -lpython3.7m -o pyfuzzer
   clang -I/usr/include/python3.7m hello_world.c module.c /home/erik/workspace/pyfuzzer/pyfuzzer/pyfuzzer_print_corpus.c -Wl,-Bsymbolic-functions -Wl,-z,relro -lpython3.7m -o pyfuzzer_print_corpus
   rm -f pyfuzzer.profraw
   ./pyfuzzer corpus -max_total_time=1 -max_len=4096
   INFO: Seed: 4068588707
   INFO: Loaded 1 modules   (23 inline 8-bit counters): 23 [0x47444d, 0x474464),
   INFO: Loaded 1 PC tables (23 PCs): 23 [0x461770,0x4618e0),
   INFO:        0 files found in corpus
   Importing module under test... done.
   Importing custom mutator... done.
   Finding function 'test_one_input' in mutator... done.
   INFO: A corpus is not provided, starting from an empty corpus
   #2	INITED cov: 7 ft: 8 corp: 1/1b lim: 4 exec/s: 0 rss: 33Mb
   #5	NEW    cov: 9 ft: 10 corp: 2/3b lim: 4 exec/s: 0 rss: 33Mb L: 2/2 MS: 3 ShuffleBytes-ShuffleBytes-InsertByte-
   #6	NEW    cov: 10 ft: 11 corp: 3/6b lim: 4 exec/s: 0 rss: 33Mb L: 3/3 MS: 1 CopyPart-
   #13	NEW    cov: 11 ft: 12 corp: 4/10b lim: 4 exec/s: 0 rss: 33Mb L: 4/4 MS: 2 EraseBytes-CopyPart-
   #53	NEW    cov: 13 ft: 14 corp: 5/14b lim: 4 exec/s: 0 rss: 33Mb L: 4/4 MS: 5 CopyPart-ChangeBit-CopyPart-ChangeBinInt-ChangeBinInt-
   #55	REDUCE cov: 13 ft: 14 corp: 5/12b lim: 4 exec/s: 0 rss: 33Mb L: 2/4 MS: 2 ChangeBit-CrossOver-
   #252	REDUCE cov: 13 ft: 14 corp: 5/11b lim: 4 exec/s: 0 rss: 33Mb L: 1/4 MS: 2 ChangeByte-EraseBytes-
   #1221577	DONE   cov: 13 ft: 14 corp: 5/11b lim: 4096 exec/s: 610788 rss: 33Mb
   Done 1221577 runs in 2 second(s)
   llvm-profdata merge -sparse pyfuzzer.profraw -o pyfuzzer.profdata
   llvm-cov show pyfuzzer -instr-profile=pyfuzzer.profdata -ignore-filename-regex=/usr/|pyfuzzer.c|module.c
       1|       |#include <Python.h>
       2|       |
       3|       |PyDoc_STRVAR(
       4|       |    tell_doc,
       5|       |    "tell(message)\n"
       6|       |    "--\n"
       7|       |    "Arguments: (message:bytes)\n");
       8|       |
       9|       |static PyObject *m_tell(PyObject *module_p, PyObject *message_p)
      10|  1.22M|{
      11|  1.22M|    Py_ssize_t size;
      12|  1.22M|    char* buf_p;
      13|  1.22M|    int res;
      14|  1.22M|    PyObject *res_p;
      15|  1.22M|
      16|  1.22M|    res = PyBytes_AsStringAndSize(message_p, &buf_p, &size);
      17|  1.22M|
      18|  1.22M|    if (res != -1) {
      19|  1.01M|        switch (size) {
      20|  1.01M|
      21|  1.01M|        case 0:
      22|   100k|            res_p = PyLong_FromLong(5);
      23|   100k|            break;
      24|  1.01M|
      25|  1.01M|        case 1:
      26|   128k|            res_p = PyBool_FromLong(1);
      27|   128k|            break;
      28|  1.01M|
      29|  1.01M|        case 2:
      30|   106k|            res_p = PyBytes_FromString("Hello!");
      31|   106k|            break;
      32|  1.01M|
      33|  1.01M|        default:
      34|   684k|            res_p = PyLong_FromLong(0);
      35|   684k|            break;
      36|   201k|        }
      37|   201k|    } else {
      38|   201k|        res_p = NULL;
      39|   201k|    }
      40|  1.22M|
      41|  1.22M|    return (res_p);
      42|  1.22M|}
      43|       |
      44|       |static struct PyMethodDef methods[] = {
      45|       |    { "tell", m_tell, METH_O, tell_doc},
      46|       |    { NULL }
      47|       |};
      48|       |
      49|       |static PyModuleDef module = {
      50|       |    PyModuleDef_HEAD_INIT,
      51|       |    .m_name = "hello_world",
      52|       |    .m_size = -1,
      53|       |    .m_methods = methods
      54|       |};
      55|       |
      56|       |PyMODINIT_FUNC PyInit_hello_world(void)
      57|      1|{
      58|      1|    return (PyModule_Create(&module));
      59|      1|}

Print the function calls that found new code paths. This information
is usually good input when writing unit tests.

.. code-block:: text

   $ pyfuzzer print_corpus
   tell(b'1\n1') = 0
   tell(b'1') = True
   tell(None) raises:
   Traceback (most recent call last):
     File "/home/erik/workspace/pyfuzzer/pyfuzzer/mutators/utils.py", line 23, in print_function
       res = func(*args)
   TypeError: expected bytes, NoneType found
   tell(b'1\n') = b'Hello!'
