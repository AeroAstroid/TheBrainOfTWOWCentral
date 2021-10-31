import math
from typing import List

from src.interpreter.expression import Expression


def round_func(block: List, codebase):
    # 0.5 gives 0 for some reason, but since B++ was the same we'll keep it
    # in function_deco.py its returning a special formatting for "round", maybe that's the source of the issue?
    return round(Expression(block[1], codebase))