import Commands.bstar.src.interpreter.globals as globals
from Commands.bstar.src.interpreter.expression import Expression


def loop(amount, func):
    results = []
    for _ in range(Expression(amount, globals.codebase)):
        result = Expression(func, globals.codebase)
        if result is not None:  # VOID Function
            results.append(result)

    if len(results) > 0:
        return results
