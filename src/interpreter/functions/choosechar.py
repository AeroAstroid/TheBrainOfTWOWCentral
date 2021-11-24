import random
from typing import List

from src.interpreter.expression import Expression


def choosechar(block: List, codebase):
    choices = Expression(str(block[1]), codebase)
    rand = random.randint(0, len(choices) - 1)

    return Expression(choices[rand], codebase)
