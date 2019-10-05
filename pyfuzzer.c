#include <stdint.h>
#include <stddef.h>
#include <string.h>
#include <Python.h>

extern PyObject *PyInit_hello_world(void);

static void init(PyObject **module_pp, PyObject **test_one_input_pp)
{
    PyObject *mutator_p;

    Py_Initialize();

    //*module_pp = PyInit_hello_world();
    *module_pp = PyImport_ImportModule("hello_world");

    if (*module_pp == NULL) {
        PyErr_Print();
        exit(1);
    }

    mutator_p = PyImport_ImportModule("mutator");

    if (mutator_p == NULL) {
        PyErr_Print();
        exit(1);
    }

    *test_one_input_pp = PyObject_GetAttrString(mutator_p, "test_one_input");

    if (*test_one_input_pp == NULL) {
        PyErr_Print();
        exit(1);
    }
}

int LLVMFuzzerTestOneInput(const uint8_t *data_p, size_t size)
{
    static PyObject *module_p = NULL;
    static PyObject *test_one_input_p = NULL;
    PyObject *func_p;
    PyObject *res_p;
    PyObject *args_p;
    PyObject *data_obj_p;
    const char *name_p;

    if (module_p == NULL) {
        init(&module_p, &test_one_input_p);
    }

    args_p = PyTuple_New(2);
    Py_INCREF(module_p);
    PyTuple_SET_ITEM(args_p, 0, module_p);
    PyTuple_SET_ITEM(args_p,
                     1,
                     PyBytes_FromStringAndSize((const char *)data_p,
                                               size));
    PyErr_Clear();
    res_p = PyObject_CallObject(test_one_input_p, args_p);
    Py_DECREF(args_p);

    if (res_p != NULL) {
        //printf("res: %s\n", PyUnicode_AsUTF8(PyObject_Str(res_p)));
        Py_DECREF(res_p);
    } else if (!PyErr_Occurred()) {
        exit(2);
    } else {
        PyErr_Print();
    }

    return (0);
}
