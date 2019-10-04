#include <Python.h>

static PyObject *m_tell(PyObject *module_p, PyObject *message_p)
{
    if (message_p[0] == 'H') {
        if (message_p[1] == 'i') {
            if (message_p[2] == '!') {
                exit(1);
            }
        }
    }

    return (PyBytes_FromString("Hello!"));
}

PyInit_hello_world()
{
}
