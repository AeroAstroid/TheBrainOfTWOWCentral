import copy


# TODO: Inspect types further
def setindex(arr: list, index: int, val: any):
    arr = copy.copy(arr)
    arr[index] = val
    return arr
