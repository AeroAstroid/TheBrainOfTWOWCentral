from typing import List

from src.interpreter.expression import Expression


def math(number, operator, by):
    if operator == "+":
        return Expression(["ADD", number, by], codebase)
    elif operator == "-":
        return Expression(["SUB", number, by], codebase)
    elif operator == "/":
        return Expression(["DIV", number, by], codebase)
    elif operator == "*":
        return Expression(["MUL", number, by], codebase)
    elif operator == "^":
        return Expression(["POW", number, by], codebase)
    elif operator == "%":
        return Expression(["MOD", number, by], codebase)

