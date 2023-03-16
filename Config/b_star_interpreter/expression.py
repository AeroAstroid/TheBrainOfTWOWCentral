import types
from enum import Enum
from typing import Union

import bstarparser
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
        diagram of a block, e.g. [DEFINE foo 5]
        block {
            children: block[],
            start: int
            end: int
            line: int
            raw?: string,
            val_type: Type
        }
"""


def Expression(block: bstarparser.Property, codebase):
    if globals.codebase.ret is not None:
        return

    # if type(block) is Token:
        # the worse if statement you've ever seen.
        # TODO: maybe make this a function?
        # if (block[0] == "'" or block[0] == "\"") and (block[-1] == "'" or block[-1] == "\""):
        #     return block[1:-1]
        # return block

    # print(block, block.pretty())
    match block.val_type:
        case bstarparser.Type.FUNCTION:
            alias = Expression(block.children[0], globals.codebase)

            # this gets the argument values from the block
            # arguments = list(map(lambda x: Expression(x, codebase), block.children[1].children))
            # arguments = list(map(lambda x: x, block.children[1:]))
            arguments = block.children[1:]
            # arguments = list(map(lambda x: x.children[0], arguments))
            functionWanted = findFunction(alias, codebase)
            if functionWanted is not None:
                if hasattr(functionWanted, "block"):  # check if it's a user-made function
                    return functionWanted.run(arguments)
                else:
                    return functionWanted.run(codebase, block, arguments, alias)
            else:
                raise NotImplementedError(f"Function not found: {alias}")
        case bstarparser.Type.INTEGER:
            return int(block.raw)
        case bstarparser.Type.FLOAT:
            return float(block.raw)
        case bstarparser.Type.STRING:
            return block.raw.strip()
        case _:
            raise NotImplementedError(f"Type not found: {block.val_type}")
            # unstring = block.raw
            # try:
            #     return unstring
            # except:


def findFunction(name: str, codebase):  # -> Union[Callable[[List, Codebase], None], List[str]]:
    # This tries to find a user-made function first, then tries the built-in ones.
    functionWanted = globals.codebase.functions[name]
    # if functionWanted is None:
    #     functionWanted = Commands.src.interpreter.tempFunctionsFile.functions.get(name)

    return functionWanted

