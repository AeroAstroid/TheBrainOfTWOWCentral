import Config.b_star_interpreter.globals as globals
from Config.b_star_interpreter.expression import Expression


# TODO: Inspect types further
def try_func(attempt: any, on_error: any):
    try:
        return Expression(attempt, globals.codebase)
    except Exception as err:
        globals.codebase.variables[0]["error"] = type(err).__name__
        return Expression(on_error, globals.codebase)
