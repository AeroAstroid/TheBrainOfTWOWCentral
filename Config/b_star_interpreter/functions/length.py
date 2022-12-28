def length(arr):
    try:
        return len(arr)
    except TypeError:  # for numbers (int and float)
        return len(str(arr))
