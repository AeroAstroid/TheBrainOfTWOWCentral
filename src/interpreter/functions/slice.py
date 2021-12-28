from typing import List
from src.interpreter.expression import Expression


def slice_func(block: List, codebase):
    return block[1][int(block[2]):int(block[3])]
