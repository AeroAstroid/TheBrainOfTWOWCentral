import types
from enum import Enum
from re import fullmatch
from typing import Union, List

import src.interpreter.globals as globals
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

    # [FUNC FACTORIAL [ARRAY "num"]
    #   [DEFINE prev [FACTORIAl [MATH [VAR num] - 1]]]
    #   [RETURN [MATH [VAR prev] * [VAR num]]]
    # ]
    USERFUNCTION = 5


def Expression(block: Union[List[str], str], codebase):
    # TODO(?): try/except needed

    blockType = isType(block)

    if blockType == Type.FUNCTION:
        arguments = block[1:]
        alias = block[0]
        functionWanted = findFunction(alias, codebase)
        if functionWanted is not None:
            if hasattr(functionWanted, "block"):
                return functionWanted.run(arguments)
            else:
                return functionWanted.run(codebase, arguments, alias)
        else:
            raise NotImplementedError(f"Function not found: {alias}")
    elif blockType == Type.STRING:
        return block
    elif blockType == Type.ARRAY:
        arguments = block[1:]
        return list(map(lambda item: Expression(item, codebase), arguments))
    elif blockType == Type.INTEGER:
        return int(block)
    elif blockType == Type.FLOAT:
        return float(block)
    # elif blockType == Type.EXPONENT:
    #     return int(float(block))


def findFunction(name: str, codebase):  # -> Union[Callable[[List, Codebase], None], List[str]]:
    # This tries to find a user-made function first, then tries the built-in ones.
    functionWanted = globals.codebase.functions[name]
    if functionWanted is None:
        functionWanted = src.interpreter.tempFunctionsFile.functions.get(name)

    return functionWanted


def isType(block):
    if type(block) == list:
        if block[0] == "ARRAY":
            return Type.ARRAY
        else:
            return Type.FUNCTION
    else:
        if fullmatch(r"^[+-]?\d+$", str(block)):
            return Type.INTEGER
        elif fullmatch(r"^[+-]?\d+(.|([eE][+-]?)|)\d+$", str(block)):
            return Type.FLOAT
        # elif fullmatch(r"^[+-]?\d+[eE][+-]?\d+$", block):
        #     return Type.EXPONENT
        else:
            return Type.STRING