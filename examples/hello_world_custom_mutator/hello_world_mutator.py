import pyfuzzer.mutators.generic
from pyfuzzer.mutators.generic import print_callable


def mutate(data):
    if data[0] == 0:
        return None
    else:
        return data[1:]


class Mutator(pyfuzzer.mutators.generic.Mutator):

    def test_one_input(self, data):
        return self._module.tell(mutate(data))

    def test_one_input_print(self, data):
        print_callable(self._module.tell, [mutate(data)], 4 * ' ')


def setup(module):
    return Mutator(module)
