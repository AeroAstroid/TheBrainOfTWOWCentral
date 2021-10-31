from enum import Enum
from typing import Union
from typing import List

# expression defining
import src.interpreter.function_deco


class Type(Enum):
    FUNCTION = 0
    STRING = 1
    ARRAY = 2
    INTEGER = 3
    FLOAT = 4


def Expression(block: Union[List, str], codebase):
    # TODO: try/except needed

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


def isType(block):
    if type(block) == list:
        if block[0] == "ARRAY":
            return Type.ARRAY
        else:
            return Type.FUNCTION
    else:
        # TODO: Breaks float
        if block.isnumeric():
            try:
                return Type.INTEGER
            except ValueError:
                return Type.FLOAT
        else:
            return Type.STRING
