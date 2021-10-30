import random
from typing import List

from src.interpreter.expression import Expression


def random_func(block: List, codebase):
    return random.uniform(Expression(block[1], codebase), Expression(block[2], codebase))
