import random
from typing import List

from src.interpreter.expression import Expression


def choose(block: List, codebase):
    choices = block[1:]
    rand = random.randint(0, len(choices) - 1)

    return Expression(choices[rand], codebase)
