def pow_func(number, *bys):
    result = number

    for num in bys:
        result **= num
    return result
