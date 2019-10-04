#include <stdint.h>
#include <stddef.h>
#include <string.h>
#include <Python.h>

static void init(PyObject **test_one_input_pp)
{
    PyObject *bridge_p;

    Py_Initialize();

    bridge_p = PyImport_ImportModule("bridge");

    if (bridge_p == NULL) {
        PyErr_Print();
        exit(1);
    }

    *test_one_input_pp = PyObject_GetAttrString(bridge_p, "test_one_input");

    if (*test_one_input_pp == NULL) {
        PyErr_Print();
        exit(1);
    }
}

int LLVMFuzzerTestOneInput(const uint8_t *data_p, size_t size)
{
    static PyObject *test_one_input_p = NULL;
    PyObject *func_p;
    PyObject *res_p;
    PyObject *args_p;
    PyObject *data_obj_p;
    const char *name_p;

    if (test_one_input_p == NULL) {
        init(&test_one_input_p);
    }

    args_p = PyTuple_New(1);
    PyTuple_SET_ITEM(args_p,
                     0,
                     PyBytes_FromStringAndSize((const char *)data_p,
                                               size));
    PyErr_Clear();
    res_p = PyObject_CallObject(test_one_input_p, args_p);
    Py_DECREF(args_p);

    if (res_p != NULL) {
        Py_DECREF(res_p);
        printf("res: %s\n", PyUnicode_AsUTF8(PyObject_Str(res_p)));
    } else if (!PyErr_Occurred()) {
        exit(2);
    } else {
        PyErr_Print();
    }

    return (0);
}
