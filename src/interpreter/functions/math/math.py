from typing import List

from src.interpreter.expression import Expression


def math(block: List, codebase):
    if block[2] == "+":
        return Expression(["ADD", block[1], block[3]], codebase)
    elif block[2] == "-":
        return Expression(["SUB", block[1], block[3]], codebase)
    elif block[2] == "/":
        return Expression(["DIV", block[1], block[3]], codebase)
    elif block[2] == "*":
        return Expression(["MUL", block[1], block[3]], codebase)
    elif block[2] == "^":
        return Expression(["POW", block[1], block[3]], codebase)
    elif block[2] == "%":
        return Expression(["MOD", block[1], block[3]], codebase)

