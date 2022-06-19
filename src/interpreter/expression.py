import types
from enum import Enum
from math import floor
from re import fullmatch
from typing import Union, List

from lark import Tree, Token
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


def Expression(block: Union[Tree, Token], codebase):
    if globals.codebase.ret is not None:
        return

    if type(block) is Token:
        # the worse if statement you've ever seen.
        # TODO: maybe make this a function?
        if (block[0] == "'" or block[0] == "\"") and (block[-1] == "'" or block[-1] == "\""):
            return block[1:-1]
        return block

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
        case "integer":
            return int(block.children[0])
        case "float":
            return float(block.children[0])
        case "array":
            return block.children
        case "string":
            return block.children[0][1:-1]
        case "unescaped_string" | _:
            return block.children[0]



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