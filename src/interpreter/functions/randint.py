import random

from typing import List


def randint(block: List, codebase):
    return random.randint(int(block[1]), int(block[2]))  # TODO: add seeds to these, maybe?
