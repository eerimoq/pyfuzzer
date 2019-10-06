#include <Python.h>

extern PyObject *pyfuzzer_module_init(void);

static void init(PyObject **module_pp,
                 PyObject **test_one_input_print_pp)
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
        mutator_p = PyImport_ImportModule("pyfuzzer.mutators.random");

        if (mutator_p == NULL) {
            PyErr_Print();
            exit(1);
        }
    }

    *test_one_input_print_pp = PyObject_GetAttrString(mutator_p,
                                                      "test_one_input_print");

    if (*test_one_input_print_pp == NULL) {
        PyErr_Print();
        exit(1);
    }
}

static void *read_corpus(const char *corpus_path_p, Py_ssize_t *size_p)
{
    void *buf_p;
    FILE *fin_p;
    ssize_t res;

    fin_p = fopen(corpus_path_p, "rb");

    if (fin_p == NULL) {
        fprintf(stderr, "Failed to open '%s'.\n", corpus_path_p);
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

    return (buf_p);
}

int main(int argc, const char *argv[])
{
    PyObject *module_p;
    PyObject *test_one_input_print_p;
    PyObject *args_p;
    PyObject *data_p;
    Py_ssize_t size;
    void *buf_p;

    if (argc != 2) {
        fprintf(stderr, "Wrong number of arguments %d.\n", argc);
        exit(1);
    }

    buf_p = read_corpus(argv[1], &size);
    init(&module_p, &test_one_input_print_p);
    args_p = PyTuple_Pack(2,
                          module_p,
                          PyBytes_FromStringAndSize((const char *)buf_p, size));

    if (args_p == NULL) {
        printf("Failed to create arguments.\n");
        exit(1);
    }

    PyObject_CallObject(test_one_input_print_p, args_p);

    return (0);
}
