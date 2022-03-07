import types
from enum import Enum
from re import fullmatch
from typing import Union, List, Callable

import src.interpreter.tempFunctionsFile


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
    # EXPONENT = 5


def Expression(block: Union[List[str], str], codebase):
    # TODO(?): try/except needed
    arguments = block[1:]

    blockType = isType(block)

    if blockType == Type.FUNCTION:
        alias = block[0]
        functionWanted = findFunction(alias, codebase)
        if functionWanted is not None:
            # if functionWanted is Function:
            #     built-in functions (python)
                return functionWanted.run(codebase, arguments, alias)
            # else:
                # user functions (b*)
                # return Expression(functionWanted.run(block[1:]), codebase)
        else:
            raise NotImplementedError(f"Function not found: {alias}")
    elif blockType == Type.STRING:
        return block
    elif blockType == Type.ARRAY:
        return list(map(lambda item: Expression(item, codebase), arguments))
    elif blockType == Type.INTEGER:
        return int(block)
    elif blockType == Type.FLOAT:
        return float(block)
    # elif blockType == Type.EXPONENT:
    #     return int(float(block))


def findFunction(name: str, codebase):  # -> Union[Callable[[List, Codebase], None], List[str]]:
    # This tries to find a built-in function first, then tries the user-made ones.
    functionWanted = src.interpreter.tempFunctionsFile.functions.get(name)

    return functionWanted


def isType(block):
    if type(block) == list:
        if block[0] == "ARRAY":
            return Type.ARRAY
        else:
            return Type.FUNCTION
    else:
        if fullmatch(r"^[+-]?\d+$", block):
            return Type.INTEGER
        elif fullmatch(r"^[+-]?\d+(.|([eE][+-]?)|)\d+$", block):
            return Type.FLOAT
        # elif fullmatch(r"^[+-]?\d+[eE][+-]?\d+$", block):
        #     return Type.EXPONENT
        else:
            return Type.STRING
