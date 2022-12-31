import types
from enum import Enum
from typing import Union

from lark import Tree, Token
import Config.b_star_interpreter.globals as globals
import Config.b_star_interpreter.tempFunctionsFile


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
            alias = Expression(block.children[0], globals.codebase)

            # this gets the argument values from the block
            # arguments = list(map(lambda x: Expression(x, codebase), block.children[1].children))
            arguments = list(map(lambda x: x, block.children[1:]))
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
            items = list(map(lambda x: Expression(x, globals.codebase), block.children))
            items = [item for item in items if item is not None] # TODO: Some might be None due to a blank arg being parsed, if this is fixed remove this (TODO below)
            return items
        case "string":
            return block.children[0][1:-1].replace("\\n", "\n").replace("\\\"", "\"")
        case "arg":
            return None # TODO: Make empty array not parse blank args, remove TODO above and TODO in function.py
        case "unescaped_string" | _:
            unstring = block.children[0]
            try:
                return unstring.value
            except:
                return unstring


def findFunction(name: str, codebase):  # -> Union[Callable[[List, Codebase], None], List[str]]:
    # This tries to find a user-made function first, then tries the built-in ones.
    functionWanted = globals.codebase.functions[name]
    if functionWanted is None:
        functionWanted = Commands.src.interpreter.tempFunctionsFile.functions.get(name)

    return functionWanted
