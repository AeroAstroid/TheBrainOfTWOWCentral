import math

def log(number, *bys):
    result = number

    for num in bys:
        math.log(result, num)
    return result
