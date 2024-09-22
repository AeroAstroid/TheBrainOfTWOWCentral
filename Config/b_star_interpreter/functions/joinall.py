from typing import List

import Config.b_star_interpreter.globals as globals
from Config.b_star_interpreter.expression import Expression


def joinall(array):
    return recursive_join(array)


def recursive_join(array):
    result = ""

    for e in array:
        eval_e = Expression(e, globals.codebase)
        if isinstance(eval_e, List):
            result += recursive_join(Expression(eval_e, globals.codebase))
        else:
            result += str(eval_e)
