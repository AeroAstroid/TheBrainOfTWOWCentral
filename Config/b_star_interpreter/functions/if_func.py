import Config.b_star_interpreter.globals as globals
from Config.b_star_interpreter.expression import Expression


# TODO: Inspect types further
def if_func(compare: any, true: any, false: any):
    # TODO: Get a better name
    false_arg = false is not False

    if Expression(compare, globals.codebase):
        return Expression(true, globals.codebase)
    else:
        if false_arg:
            return Expression(false, globals.codebase)
