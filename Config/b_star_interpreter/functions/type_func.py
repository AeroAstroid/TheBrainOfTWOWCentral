import Config.b_star_interpreter.globals as globals
from Config.b_star_interpreter.expression import Expression


# TODO: Inspect types further
def type_func(thing: any):
    return type(Expression(thing, globals.codebase)).__name__
