from enum import Enum
from typing import Union
from typing import List

# expression defining
import src.interpreter.function_deco


class Type(Enum):
    # [J 100]
    FUNCTION = 0

    # "Hello, World!"
    STRING = 1

    # [ARRAY 1 2 3 4 5]
    ARRAY = 2

    # 101
    INTEGER = 3

    # 3.1415926
    FLOAT = 4

    # Special Type used for the elif spam: Its a combination of float and int.
    # 1e9, 5.3e+10
    EXPONENT = 5


def Expression(block: Union[List, str], codebase):
    # TODO: try/except needed
    #[
    if block[-1] == "":
        block = block[:-1]

    blockType = isType(block)
    if blockType == Type.FUNCTION:
        functionWanted = src.interpreter.function_deco.functions.get(block[0])
        # print(functionWanted)
        if functionWanted is not None:
            return functionWanted(block=block, codebase=codebase)
        else:
            return block[0]
    elif blockType == Type.STRING:
        return block
    elif blockType == Type.ARRAY:
        array = block[1:]  # Get rid of ARRAY string

        return list(map(lambda item: Expression(item, codebase), array))
    elif blockType == Type.INTEGER:
        return int(block)
    elif blockType == Type.FLOAT:
        return float(block)
    elif blockType == Type.EXPONENT:
        return int(float(block))


def isType(block):
    if type(block) == list:
        if block[0] == "ARRAY":
            return Type.ARRAY
        else:
            return Type.FUNCTION
    else:
        # TODO: The bruteforce solution; Extremely inefficient
        isFloat = False
        isExponent = False
        for char in block:
            if char in ["e"]:
                isExponent = True
            if char in ["."]:
                isFloat = True
            if char not in ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "e", "+", "-", "."]:
                return Type.STRING

        if isExponent:
            return Type.EXPONENT

        if isFloat:
            return Type.FLOAT
        else:
            return Type.INTEGER
