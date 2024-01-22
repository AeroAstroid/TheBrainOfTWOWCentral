def length(arr: list):
    try:
        return len(arr)
    except TypeError:  # for numbers (int and float)
        return len(str(arr))
