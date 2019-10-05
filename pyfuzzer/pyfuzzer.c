#include <Python.h>

extern PyObject *pyfuzzer_module_init(void);

static void init(PyObject **module_pp,
                 PyObject **test_one_input_pp,
                 PyObject **args_pp)
{
    PyObject *mutator_p;

    Py_Initialize();

    *module_pp = pyfuzzer_module_init();

    if (*module_pp == NULL) {
        PyErr_Print();
        exit(1);
    }

    mutator_p = PyImport_ImportModule("mutator");

    if (mutator_p == NULL) {
        PyErr_Print();
        mutator_p = PyImport_ImportModule("pyfuzzer.mutators.random");

        if (mutator_p == NULL) {
            PyErr_Print();
            printf("sys.path: %s\n",
                   PyUnicode_AsUTF8(PyObject_Str(PySys_GetObject("path"))));
            exit(1);
        }
    }

    *test_one_input_pp = PyObject_GetAttrString(mutator_p, "test_one_input");

    if (*test_one_input_pp == NULL) {
        PyErr_Print();
        exit(1);
    }

    *args_pp = PyTuple_New(2);

    if (*args_pp == NULL) {
        PyErr_Print();
        exit(1);
    }

    Py_INCREF(*module_pp);
    PyTuple_SET_ITEM(*args_pp, 0, *module_pp);
}

int LLVMFuzzerTestOneInput(const uint8_t *data_p, size_t size)
{
    static PyObject *module_p = NULL;
    static PyObject *test_one_input_p = NULL;
    static PyObject *args_p;
    PyObject *res_p;
    PyObject *data_obj_p;

    if (module_p == NULL) {
        init(&module_p, &test_one_input_p, &args_p);
    }

    data_obj_p = PyBytes_FromStringAndSize((const char *)data_p, size);

    if (data_obj_p == NULL) {
        PyErr_Print();
        exit(1);
    }

    PyTuple_SET_ITEM(args_p, 1, data_obj_p);
    PyErr_Clear();
    res_p = PyObject_CallObject(test_one_input_p, args_p);
    Py_DECREF(data_obj_p);

    if (res_p != NULL) {
        // printf("res: %s\n", PyUnicode_AsUTF8(PyObject_Str(res_p)));
        Py_DECREF(res_p);
    }

    return (0);
}
