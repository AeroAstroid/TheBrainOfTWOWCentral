from enum import Enum

import bstarparser
# from lark import Tree, Token
import Config.b_star_interpreter.globals as globals
import Config.b_star_interpreter.tempFunctionsFile
from Config.b_star_interpreter.newpasta import Node, Token


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


def Expression(node: Node, codebase):
    if globals.codebase.ret is not None:
        return

    # if type(block) is Token:
        # the worse if statement you've ever seen.
        # TODO: maybe make this a function?
        # if (block[0] == "'" or block[0] == "\"") and (block[-1] == "'" or block[-1] == "\""):
        #     return block[1:-1]
        # return block

    # print(block, block.pretty())

    if node.type is None: # function
        alias = Expression(node.children[0], globals.codebase)

        # this gets the argument values from the block
        # arguments = list(map(lambda x: Expression(x, codebase), block.children[1].children))
        # arguments = list(map(lambda x: x, block.children[1:]))
        arguments = node.children[1:]
        # arguments = list(map(lambda x: x.children[0], arguments))
        functionWanted = findFunction(alias, codebase)
        if functionWanted is not None:
            if hasattr(functionWanted, "block"):  # check if it's a user-made function
                return functionWanted.run(arguments)
            else:
                return functionWanted.run(codebase, node, arguments, alias)
        else:
            raise NotImplementedError(f"Function not found: {alias}")

    match node.type.__class__:
        case Token.INTEGER:
            return int(node.type.value)
        case Token.FLOAT:
            return float(node.type.value)
        case Token.SYMBOL:
            return node.type.value.strip()
        case _:
            raise NotImplementedError(f"Type not found: {node.type.__class__.__name__}")
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

