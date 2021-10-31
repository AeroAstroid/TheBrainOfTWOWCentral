from typing import List
from src.interpreter.expression import Expression


def map_func(block: List, codebase):
    func: List = block[1]
    arr: List = block[2][1:]
    res = []

    for item in arr:
        funcc = []
        funcc.extend(func)
        funcc.insert(1, item)
        res.append(Expression(funcc, codebase))

    return res
