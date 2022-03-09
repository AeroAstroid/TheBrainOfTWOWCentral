import src.interpreter.globals as globals
from src.interpreter.expression import Expression


def loop(amount, *functions):
    results = []
    for i in range(Expression(amount, globals.codebase)):
        for func in functions:
            result = Expression(func, globals.codebase)
            if result is not None:  # VOID Function
                results.append(result)

    if len(results) > 0:
        return results
