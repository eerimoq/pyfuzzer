#include <Python.h>

extern PyMODINIT_FUNC PyInit_hello_world(void);

PyMODINIT_FUNC pyfuzzer_module_init(void)
{
    return (PyInit_hello_world());
}
