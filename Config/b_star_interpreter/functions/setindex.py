import copy

def setindex(arr, index, val):
  arr = copy.copy(arr)
  arr[index] = val
  return arr
