import random


def choose(arr):
    rand = random.randint(0, len(arr) - 1)
    return arr[rand]
