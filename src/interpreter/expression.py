import types
from enum import Enum
from re import fullmatch
from typing import Union, List

from lark import Tree

import src.interpreter.globals as globals
import src.interpreter.tempFunctionsFile


# Deprecated, lark does this now
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


"""
        diagram of a block
        block {
            children: [
                0: block,
                1: args
            ],
            data: "function" (usually)
        }
"""


def Expression(block: Tree, codebase):
    # print(block, block.pretty())
    match block.data:
        case "function":
            alias = block.children[0].children[0]

            # this gets the argument values from the block
            # arguments = list(map(lambda x: Expression(x, codebase), block.children[1].children))
            arguments = list(map(lambda x: x, block.children[1].children))
            # arguments = list(map(lambda x: x.children[0], arguments))
            functionWanted = findFunction(alias, codebase)
            if functionWanted is not None:
                if hasattr(functionWanted, "block"):  # check if it's a user-made function
                    return functionWanted.run(arguments)
                else:
                    return functionWanted.run(codebase, arguments, alias)
            else:
                raise NotImplementedError(f"Function not found: {alias}")
        case "unescaped_string":
            return str(block.children[0])
        case "number":
            # TODO: check if it's an int or float
            return float(block.children[0])
        case "array":
            return block.children
        case _:
            return block.children[0]
    # elif blockType == Type.ARRAY:
    #     arguments = block[1:]
    #     return list(map(lambda item: Expression(item, codebase), arguments))
    # elif blockType == Type.INTEGER:
    #     return int(block)
    # elif blockType == Type.FLOAT:
    #     return float(block)
    # elif blockType == Type.EXPONENT:
    #     return int(float(block))


def findFunction(name: str, codebase):  # -> Union[Callable[[List, Codebase], None], List[str]]:
    # This tries to find a user-made function first, then tries the built-in ones.
    functionWanted = globals.codebase.functions[name]
    if functionWanted is None:
        functionWanted = src.interpreter.tempFunctionsFile.functions.get(name)

    return functionWanted
