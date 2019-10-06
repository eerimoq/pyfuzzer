from pyfuzzer.mutators.utils import print_function


def test_one_input(module, data):
    if data[0] == 0:
        data = None
    else:
        data = data[1:]

    module.tell(data)


def test_one_input_print(module, data):
    if data[0] == 0:
        data = None
    else:
        data = data[1:]

    print_function(module.tell, [data])
