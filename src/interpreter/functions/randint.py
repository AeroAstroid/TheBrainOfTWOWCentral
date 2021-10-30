import random

from typing import List

from src.interpreter.expression import Expression


def randint(block: List, codebase):
    # TODO: add seeds to these, maybe?
    return random.randint(Expression(block[1], codebase), Expression(block[2], codebase))
