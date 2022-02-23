from typing import List
from src.interpreter.expression import Expression


def split(block: List, codebase):
    string = block[1]
    if len(block) < 3:  # Seperator argument or not
        string = [*string.split(" ")]
    else:
        string = [*string.split(block[2])]

    return Expression(["ARRAY", *string], codebase)
