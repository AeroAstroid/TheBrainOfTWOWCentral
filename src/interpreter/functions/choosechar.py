import random
from typing import List

from src.interpreter.expression import Expression


def choosechar(block: List, codebase):
    choices = block[1:]
    rand = random.randint(0, len(choices[0]) - 1)

    return Expression(choices[0][rand], codebase)
