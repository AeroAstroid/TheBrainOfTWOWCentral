def sub(number: float, *bys: tuple[float]):
    result = number

    for num in bys:
        result -= num
    return result
