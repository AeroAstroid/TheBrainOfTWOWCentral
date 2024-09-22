import Config.b_star_interpreter.globals as globals
from Config.b_star_interpreter.expression import Expression


# TODO: Inspect types further
def while_func(condition: any, body: any):
    result = []
    while Expression(condition, globals.codebase) and globals.codebase.ret is None:
        res = Expression(body, globals.codebase)
        if res is not None:
            result.append(res)
    return result or None
