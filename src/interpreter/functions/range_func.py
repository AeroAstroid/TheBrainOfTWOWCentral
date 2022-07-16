def range_func(index_start, index_end, index_step):

    index_step = 1 if index_step is None else int(index_step)
    index_end = "" if index_end is None or index_end is "" else int(index_end)
    if index_start is None or index_start is "":
        index_start = ""
    else:
        index_start = int(index_start)

    return list(range(index_start, index_end, index_step))
