import Config.b_star_interpreter.globals as globals
from Config.b_star_interpreter.expression import Expression


def block(*functions):
    ret = None
    for fn in functions:
        if ret is not None:  # print everything that isn't returned
            globals.codebase.output += str(ret)

        ret = Expression(fn, globals.codebase)
        if globals.codebase.ret is not None:
            break
    return ret
