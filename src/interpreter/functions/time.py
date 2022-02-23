from typing import List
import time

from src.interpreter.expression import Expression

def time_func(block: List, codebase):
    return Expression(time.time(), codebase)