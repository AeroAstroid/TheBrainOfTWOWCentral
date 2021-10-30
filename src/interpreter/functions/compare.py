from typing import List

from src.interpreter.expression import Expression


def compare(block: List, codebase):
    v1 = block[1]
    op = block[2]
    v2 = block[3]
    if op == ">":
        return Expression(v1, codebase) > Expression(v2, codebase)
    elif op == "<":
        return Expression(v1, codebase) < Expression(v2, codebase)
    elif op == ">=":
        return Expression(v1, codebase) >= Expression(v2, codebase)
    elif op == "<=":
        return Expression(v1, codebase) <= Expression(v2, codebase)
    elif op == "=":
        return Expression(v1, codebase) == Expression(v2, codebase)
    elif op == "!=":
        return Expression(v1, codebase) != Expression(v2, codebase)
