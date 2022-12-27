import Commands.b_star.interpreter.globals as globals
from Commands.b_star.interpreter.expression import Expression


def while_func(condition, body):
    result = []
    while Expression(condition, globals.codebase) and globals.codebase.ret is None:
        res = Expression(body, globals.codebase)
        if res is not None:
            result.append(res)
    return result
