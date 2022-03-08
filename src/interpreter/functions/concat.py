import src.interpreter.globals as globals
from src.interpreter.expression import Expression


# TODO: Refactor CONCAT
def concat(item, *items):
    # determine whether concat is concatenating strings or arrays
    is_array = (type(item) == list)
    buffer = [] if is_array else ""

    for i in items:
        element = Expression(i, globals.codebase)
        if is_array != (type(element) == list):
            raise TypeError("Cannot call CONCAT with a mix of arrays and other types")
        if is_array:
            buffer.extend(element)
        else:
            buffer += str(element)
    
    if is_array:
        buffer = ''.join(map(str, buffer))

    return buffer
