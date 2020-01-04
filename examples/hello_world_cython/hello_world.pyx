def tell(message):
    if not isinstance(message, str):
        return

    length = len(message)

    if length == 0:
        return 5
    elif length == 1:
        return 1
    elif length == 2:
        return 'Hello!'
    else:
        return 0
