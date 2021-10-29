from typing import List

from src.interpreter.expression import Expression


def concat(block: List, codebase):
    buffer = ""
    for i in block[1:]:
        print("CONCAT_i", i)
        buffer += Expression(i, codebase)
    return buffer
