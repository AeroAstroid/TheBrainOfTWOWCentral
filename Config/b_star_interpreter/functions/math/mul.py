# TODO: Inspect types further
def mul(number: any, *bys: tuple[any]):
    # TODO: block isn't used, debug this!
    if type(number) == list and number[0] == "ARRAY":
        block = number

    result = number

    for num in bys:
        result *= num
    return result
