# imports -- TODO: split this
from typing import List

from src.interpreter.types.block import Block  # import block structure
import random  # used in random and maybe randint?
import math  # used in math functions
import time  # time


# expression defining
def Expression(block: List, codebase):
    if block[0] == "DEFINE":
        codebase.variables[block[1]] = block[2]
        return None
    elif block[0] == "VAR":
        return codebase.variables[block[1]]
    elif block[0] == "MATH":
        return None
    elif block[0] == "COMPARE":
        return None
    elif block[0] == "IF":
        return None
    elif block[0] == "ARRAY":
        return None
    elif block[0] == "CHOOSE":
        return None
    elif block[0] == "CHOOSECHAR":
        return None
    elif block[0] == "REPEAT":
        return None
    elif block[0] == "CONCAT":
        buffer = ""
        for i in block[1:]:
            print("CONCAT_i", i)
            buffer += Expression(i, codebase)
        return buffer
    elif block[0] == "RANDINT":
        return random.randint(int(block[1]), int(block[2]))  # TODO: add seeds to these, maybe?
    elif block[0] == "RANDOM":
        return random.uniform(float(block[1]), float(block[2]))
    elif block[0] == "FLOOR":
        return math.floor(float(block[1]))
    elif block[0] == "CEIL":
        return math.ceil(float(block[1]))
    elif block[0] == "ROUND":
        return None
    elif block[0] == "INDEX":
        return None
    elif block[0] == "ABS":
        return math.fabs(float(block[1]))
    elif block[0] == "ARGS":
        return None
    elif block[0] == "GLOBAL" and block[1] == "DEFINE":
        return None
    elif block[0] == "GLOBAL" and block[1] == "VAR":
        return None
    elif block[0] == "#":
        return None  # this is comments
    elif block[0] == "MOD":
        return None
    elif block[0] == "TIME":
        return math.round(time.time() + (float(block[1]) * 3600),
                          int(block[2]))  # miniDOCs: arg1 is hour offset, arg2 is decimals to round to
    else:
        return block[0]
