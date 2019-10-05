def test_one_input(module, data):
    if data[0] == 0:
        data = None
    else:
        data = data[1:]

    module.tell(data)
