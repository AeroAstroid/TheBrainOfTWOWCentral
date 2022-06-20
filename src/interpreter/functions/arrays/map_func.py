from typing import List
from src.interpreter.expression import Expression
from src.interpreter.userfunction import UserFunction


def map_func(block: List, codebase):
    # [MAP [ITEMS] [ARGUMENTS] [FUNCTION]}
    # Assume that all of these are Lists
    arr: List = Expression(block[1], codebase)
    args: List = block[2]
    func: List = block[3]
    user = UserFunction("_", {
        0: args[1] or None,
        1: args[2] or None
    }, func, False, codebase)
    buffer = []
    for i, item in enumerate(arr):
        buffer.append(user.run([item, i]))

    # Unpack buffer
    return Expression(["ARRAY", *buffer], codebase)
    # return ["ARRAY", *buffer]
