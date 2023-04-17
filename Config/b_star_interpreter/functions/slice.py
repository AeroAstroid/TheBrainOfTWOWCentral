

def slice_func(array, index_start, index_end, index_step):


    if index_step is None:
        index_step = 1
    else:
        index_step = int(index_step)
    
    if index_end is None or index_end is "":
        index_end = ""
    else:
        index_end = int(index_end)

    if index_start is None or index_start is "":
        index_start = ""
    else:
        index_start = int(index_start)

    return array[index_start:index_end:index_step]
