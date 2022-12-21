import Commands.bstar.interpreter.globals as globals
from Commands.bstar.interpreter.expression import Expression


def while_func(condition, body):
    result = []
    while Expression(condition, globals.codebase) and globals.codebase.ret is None:
        res = Expression(body, globals.codebase)
        if res is not None:
            result.append(res)
    return result
