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

    res = PyBytes_AsStringAndSize(message_p, &buf_p, &size);

    if (res != -1) {
        if ((size > 0) && (buf_p[0] == 'H')) {
            if ((size > 1) && (buf_p[1] == 'i')) {
                if ((size > 2) && (buf_p[2] == '!')) {
                    printf("\"Hi!\" found!\n");
                    abort();
                }
            }
        }
    }
    
    Py_INCREF(Py_None);

    return (Py_None);
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
