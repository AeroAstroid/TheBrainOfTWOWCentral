import random


def choose(*arr):
    if len(arr) == 1 and type(arr[0]) == list or type(arr[0]) == str:
        rand = random.randint(0, len(arr[0]) - 1)
        return arr[0][rand]
    else:
        rand = random.randint(0, len(arr) - 1)
        return arr[rand]
