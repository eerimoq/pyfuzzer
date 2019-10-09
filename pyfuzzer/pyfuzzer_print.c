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

#include <stdbool.h>
#include "pyfuzzer_common.h"

static void *read_unit(const char *unit_path_p, Py_ssize_t *size_p)
{
    void *buf_p;
    FILE *fin_p;
    ssize_t res;

    fin_p = fopen(unit_path_p, "rb");

    if (fin_p == NULL) {
        fprintf(stderr, "Failed to open '%s'.\n", unit_path_p);
        exit(1);
    }

    res = fseek(fin_p, 0, SEEK_END);

    if (res != 0) {
        fprintf(stderr, "fseek() failed.\n");
        exit(1);
    }

    *size_p = ftell(fin_p);

    if (*size_p < 0) {
        fprintf(stderr, "ftell() failed.\n");
        exit(1);
    }

    res = fseek(fin_p, 0, SEEK_SET);

    if (res != 0) {
        fprintf(stderr, "fseek() failed.\n");
        exit(1);
    }

    buf_p = malloc(*size_p);

    if (buf_p == NULL) {
        fprintf(stderr, "malloc() failed.\n");
        exit(1);
    }

    res = fread(buf_p, 1, *size_p, fin_p);

    if (res != *size_p) {
        fprintf(stderr,
                "fread() failed with %d (size: %d).\n",
                (int)res,
                (int)*size_p);
        exit(1);
    }

    fclose(fin_p);

    return (buf_p);
}

static void print_unit(PyObject *test_one_input_print_p,
                       const char *path_p)
{
    PyObject *args_p;
    PyObject *res_p;
    Py_ssize_t size;
    void *buf_p;

    printf("%s:\n", path_p);

    buf_p = read_unit(path_p, &size);
    args_p = PyTuple_Pack(1, PyBytes_FromStringAndSize((const char *)buf_p, size));

    if (args_p == NULL) {
        printf("Failed to create arguments.\n");
        exit(1);
    }

    res_p = PyObject_CallObject(test_one_input_print_p, args_p);

    if (res_p != NULL) {
        Py_DECREF(res_p);
    }

    if (PyErr_Occurred()) {
        PyErr_Print();
    }

    PyErr_Clear();
    free(buf_p);
}

static bool char_in_string(char c, const char *str_p)
{
    while (*str_p != '\0') {
        if (c == *str_p) {
            return (true);
        }

        str_p++;
    }

    return (false);
}

static char *strip(char *str_p, const char *strip_p)
{
    char *begin_p;
    size_t length;

    /* Strip whitespace characters by default. */
    if (strip_p == NULL) {
        strip_p = "\t\n\x0b\x0c\r ";
    }

    /* String leading characters. */
    while ((*str_p != '\0') && char_in_string(*str_p, strip_p)) {
        str_p++;
    }

    begin_p = str_p;

    /* Strip training characters. */
    length = strlen(str_p);
    str_p += (length - 1);

    while ((str_p >= begin_p) && char_in_string(*str_p, strip_p)) {
        *str_p = '\0';
        str_p--;
    }

    return (begin_p);
}

int main(int argc, const char *argv[])
{
    PyObject *test_one_input_print_p;
    char path[256];
    char *path_p;

    if (argc != 1) {
        fprintf(stderr, "Wrong number of arguments %d.\n", argc);
        exit(1);
    }

    pyfuzzer_init(NULL, NULL, &test_one_input_print_p);

    while (true) {
        path_p = fgets(&path[0], sizeof(path), stdin);

        if (path_p == NULL) {
            break;
        }

        print_unit(test_one_input_print_p, strip(path_p, NULL));
    }

    return (0);
}
