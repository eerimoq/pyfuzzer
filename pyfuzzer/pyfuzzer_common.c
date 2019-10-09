/**
 * The MIT License (MIT)
 *
 * Copyright (c) 2019 Erik Moqvist
 *
 * Permission is hereby granted, free of charge, to any person
 * obtaining a copy of this software and associated documentation
 * files (the "Software"), to deal in the Software without
 * restriction, including without limitation the rights to use, copy,
 * modify, merge, publish, distribute, sublicense, and/or sell copies
 * of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be
 * included in all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
 * EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
 * MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
 * NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
 * BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
 * ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
 * CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

#include "pyfuzzer_common.h"

extern PyObject *pyfuzzer_module_init(void);

static PyObject *import_module_under_test(void)
{
    PyObject *module_p;

    printf("Importing module under test... ");
    module_p = pyfuzzer_module_init();

    if (module_p != NULL) {
        printf("done.\n");
    } else {
        printf("failed.\n");
        PyErr_Print();
        exit(1);
    }

    return (module_p);
}

static PyObject *import_mutator_module(void)
{
    PyObject *module_p;

    printf("Importing custom mutator... ");
    module_p = PyImport_ImportModule("mutator");

    if (module_p != NULL) {
        printf("done.\n");
    } else {
        printf("failed.\n");
        PyErr_Print();

        printf("Importing mutator 'pyfuzzer.mutators.generic'... ");
        module_p = PyImport_ImportModule("pyfuzzer.mutators.generic");

        if (module_p != NULL) {
            printf("done.\n");
        } else {
            printf("failed.\n");
            PyErr_Print();
            printf("sys.path: %s\n",
                   PyUnicode_AsUTF8(PyObject_Str(PySys_GetObject("path"))));
            exit(1);
        }
    }

    return (module_p);
}

static PyObject *find_setup_function(PyObject *module_p)
{
    PyObject *setup_p;

    printf("Finding function 'setup' in mutator module... ");
    setup_p = PyObject_GetAttrString(module_p, "setup");

    if (setup_p != NULL) {
        printf("done.\n");
    } else {
        printf("failed.\n");
        PyErr_Print();
        exit(1);
    }

    return (setup_p);
}

static PyObject *call_setup_function(PyObject *setup_p,
                                     PyObject *module_under_test_p)
{
    PyObject *mutator_p;
    PyObject *args_p;

    args_p = PyTuple_Pack(1, module_under_test_p);

    if (args_p == NULL) {
        printf("Failed to create arguments.\n");
        exit(1);
    }

    PyErr_Clear();
    mutator_p = PyObject_CallObject(setup_p, args_p);

    if (PyErr_Occurred()) {
        PyErr_Print();
        exit(1);
    }

    return (mutator_p);
}

static PyObject *find_test_one_input_method(PyObject *mutator_p)
{
    PyObject *test_one_input_p;

    printf("Finding function 'test_one_input' in mutator... ");
    test_one_input_p = PyObject_GetAttrString(mutator_p, "test_one_input");

    if (test_one_input_p != NULL) {
        printf("done.\n");
    } else {
        printf("failed.\n");
        PyErr_Print();
        exit(1);
    }

    return (test_one_input_p);
}

static PyObject *find_test_one_input_print_method(PyObject *mutator_p)
{
    PyObject *test_one_input_print_p;

    printf("Finding function 'test_one_input_print' in mutator... ");
    test_one_input_print_p = PyObject_GetAttrString(mutator_p,
                                                    "test_one_input_print");

    if (test_one_input_print_p != NULL) {
        printf("done.\n");
    } else {
        printf("failed.\n");
        PyErr_Print();
        exit(1);
    }

    return (test_one_input_print_p);
}

static PyObject *create_test_one_input_args(void)
{
    PyObject *args_p;

    args_p = PyTuple_New(1);

    if (args_p == NULL) {
        PyErr_Print();
        exit(1);
    }

    return (args_p);
}

void pyfuzzer_init(PyObject **test_one_input_pp,
                   PyObject **args_pp,
                   PyObject **test_one_input_print_pp)
{
    PyObject *module_under_test_p;
    PyObject *mutator_module_p;
    PyObject *setup_p;
    PyObject *mutator_p;

    Py_Initialize();

    module_under_test_p = import_module_under_test();
    mutator_module_p = import_mutator_module();
    setup_p = find_setup_function(mutator_module_p);
    mutator_p = call_setup_function(setup_p, module_under_test_p);

    if (test_one_input_pp != NULL) {
        *test_one_input_pp = find_test_one_input_method(mutator_p);
    }

    if (args_pp != NULL) {
        *args_pp = create_test_one_input_args();
    }

    if (test_one_input_print_pp != NULL) {
        *test_one_input_print_pp = find_test_one_input_print_method(mutator_p);
    }
}
