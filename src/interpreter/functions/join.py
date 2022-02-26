from typing import List

from src.interpreter.expression import Expression


def join(block: List, codebase):
    delimiter = "" if len(block) < 3 else Expression(block[2], codebase)

    return delimiter.join(Expression(block[1], codebase))
