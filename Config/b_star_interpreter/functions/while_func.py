import Config.b_star_interpreter.globals as globals
from Config.b_star_interpreter.expression import Expression


def while_func(condition, body):
    result = []
    while Expression(condition, globals.codebase) and globals.codebase.ret is None:
        res = Expression(body, globals.codebase)
        if res is not None:
            result.append(res)
    return result or None
