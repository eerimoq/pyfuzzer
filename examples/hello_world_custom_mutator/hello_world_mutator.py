from pyfuzzer.mutators.generic import print_callable


def mutate(data):
    if data[0] == 0:
        return None
    else:
        return data[1:]


def test_one_input(module, data):
    module.tell(mutate(data))


def test_one_input_print(module, data):
    print_callable(module.tell, [mutate(data)], 4 * ' ')
