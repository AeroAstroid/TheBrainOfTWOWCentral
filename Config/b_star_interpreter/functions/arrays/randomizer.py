import random


def randomizer(array):
    # random.sample will be removed in Python 3.11
    return random.sample(array, k=len(array))
