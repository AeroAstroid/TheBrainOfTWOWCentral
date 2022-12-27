def mul(number, *bys):
    # TODO: block isn't used, debug this!
    if type(number) == list and number[0] == "ARRAY":
        block = number
    
    result = number

    for num in bys:
        result *= num
    return result
