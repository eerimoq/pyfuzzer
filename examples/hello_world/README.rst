About
=====

Use the default mutator ``pyfuzzer.mutators.random`` when testing the
module ``hello_world``.

.. code-block:: text

   $ pyfuzzer run hello_world hello_world.c
   clang -fprofile-instr-generate -fcoverage-mapping -g -fsanitize=fuzzer -fsanitize=signed-integer-overflow -fno-sanitize-recover=all -I/usr/local/include/python3.7m hello_world.c module.c /home/erik/workspace/pyfuzzer/pyfuzzer/pyfuzzer.c -Wl,-rpath /usr/local/lib -lpython3.7m -o pyfuzzer
   clang -I/usr/local/include/python3.7m hello_world.c module.c /home/erik/workspace/pyfuzzer/pyfuzzer/pyfuzzer_print_corpus.c -Wl,-rpath /usr/local/lib -lpython3.7m -o pyfuzzer_print_corpus
   rm -f pyfuzzer.profraw
   ./pyfuzzer corpus -max_total_time=1 -max_len=4096
   INFO: Seed: 2903179615
   INFO: Loaded 1 modules   (23 inline 8-bit counters): 23 [0x67945d, 0x679474),
   INFO: Loaded 1 PC tables (23 PCs): 23 [0x465d30,0x465ea0),
   INFO:        0 files found in corpus
   Importing module under test... done.
   Importing custom mutator... failed.
   ModuleNotFoundError: No module named 'mutator'
   Importing mutator 'pyfuzzer.mutators.random'... done.
   Finding function 'test_one_input' in mutator... done.
   INFO: A corpus is not provided, starting from an empty corpus
   #2	INITED cov: 4 ft: 5 corp: 1/1b lim: 4 exec/s: 0 rss: 34Mb
        NEW_FUNC[1/1]: 0x4554e0 in m_tell /home/erik/workspace/pyfuzzer/examples/hello_world/hello_world.c:10
   #51	NEW    cov: 6 ft: 8 corp: 2/5b lim: 4 exec/s: 0 rss: 36Mb L: 4/4 MS: 4 ChangeBinInt-CopyPart-InsertByte-InsertByte-
   #412	NEW    cov: 10 ft: 12 corp: 3/9b lim: 6 exec/s: 0 rss: 36Mb L: 4/4 MS: 1 ChangeBinInt-
   #468	NEW    cov: 11 ft: 13 corp: 4/14b lim: 6 exec/s: 0 rss: 36Mb L: 5/5 MS: 1 InsertByte-
   #502	NEW    cov: 12 ft: 14 corp: 5/20b lim: 6 exec/s: 0 rss: 36Mb L: 6/6 MS: 4 ShuffleBytes-ChangeByte-ChangeBinInt-CopyPart-
   #763	NEW    cov: 13 ft: 15 corp: 6/28b lim: 8 exec/s: 0 rss: 36Mb L: 8/8 MS: 1 CrossOver-
   #1466	REDUCE cov: 13 ft: 15 corp: 6/27b lim: 14 exec/s: 0 rss: 36Mb L: 7/7 MS: 3 ChangeBinInt-CopyPart-EraseBytes-
   #63426	DONE   cov: 13 ft: 15 corp: 6/27b lim: 625 exec/s: 31713 rss: 36Mb
   Done 63426 runs in 2 second(s)
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
      10|  18.4k|{
      11|  18.4k|    Py_ssize_t size;
      12|  18.4k|    char* buf_p;
      13|  18.4k|    int res;
      14|  18.4k|    PyObject *res_p;
      15|  18.4k|
      16|  18.4k|    res = PyBytes_AsStringAndSize(message_p, &buf_p, &size);
      17|  18.4k|
      18|  18.4k|    if (res != -1) {
      19|  15.5k|        switch (size) {
      20|  15.5k|
      21|  15.5k|        case 0:
      22|  1.50k|            res_p = PyLong_FromLong(5);
      23|  1.50k|            break;
      24|  15.5k|
      25|  15.5k|        case 1:
      26|  1.55k|            res_p = PyBool_FromLong(1);
      27|  1.55k|            break;
      28|  15.5k|
      29|  15.5k|        case 2:
      30|  1.65k|            res_p = PyBytes_FromString("Hello!");
      31|  1.65k|            break;
      32|  15.5k|
      33|  15.5k|        default:
      34|  10.8k|            res_p = PyLong_FromLong(0);
      35|  10.8k|            break;
      36|  2.88k|        }
      37|  2.88k|    } else {
      38|  2.88k|        res_p = NULL;
      39|  2.88k|    }
      40|  18.4k|
      41|  18.4k|    return (res_p);
      42|  18.4k|}
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
   tell(b'') = 5
   tell(b'@') = True
   tell(None) raises:
   Traceback (most recent call last):
     File "/home/erik/workspace/pyfuzzer/pyfuzzer/mutators/utils.py", line 18, in print_function
       res = func(*args)
   TypeError: expected bytes, NoneType found
   tell(b'@\x01\x00') = 0
   tell(b'#@') = b'Hello!'
