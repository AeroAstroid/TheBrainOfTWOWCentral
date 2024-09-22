import Config.b_star_interpreter.globals as globals
from Config.b_star_interpreter.expression import Expression


def loop(amount, func):
    results = []
    for _ in range(Expression(amount, globals.codebase)):
        result = Expression(func, globals.codebase)
        if result is not None:  # VOID Function
            results.append(result)

    return results or None
