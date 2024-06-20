import math


def log(number: float, *bys: tuple[float]):
    result = number

    for num in bys:
        math.log(result, num)
    return result
