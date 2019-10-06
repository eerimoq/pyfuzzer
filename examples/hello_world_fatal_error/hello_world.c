#include <Python.h>

PyDoc_STRVAR(
    tell_doc,
    "tell(message)\n"
    "--\n"
    "Arguments: (message:bytes)\n");

static PyObject *m_tell(PyObject *module_p, PyObject *message_p)
{
    Py_ssize_t size;
    char* buf_p;
    int res;
    PyObject *res_p;

    res = PyBytes_AsStringAndSize(message_p, &buf_p, &size);

    if (res != -1) {
        switch (size) {

        case 0:
            res_p = PyLong_FromLong(5);
            break;

        case 1:
            res_p = PyBool_FromLong(1);
            break;

        case 2:
            res_p = PyBytes_FromString("Hello!");
            break;

        default:
            /* Not incremeting the reference count will result in
               "Fatal Python error: deallocating None". */
            res_p = Py_None;
            break;
        }
    } else {
        res_p = NULL;
    }

    return (res_p);
}

static struct PyMethodDef methods[] = {
    { "tell", m_tell, METH_O, tell_doc},
    { NULL }
};

static PyModuleDef module = {
    PyModuleDef_HEAD_INIT,
    .m_name = "hello_world",
    .m_size = -1,
    .m_methods = methods
};

PyMODINIT_FUNC PyInit_hello_world(void)
{
    return (PyModule_Create(&module));
}
