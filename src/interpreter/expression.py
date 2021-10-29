# imports -- TODO: split this
from typing import List


# expression defining
import src.interpreter.function_deco


def Expression(block: List, codebase):
    # TODO: try/catch needed
    functionWanted = src.interpreter.function_deco.functions.get(block[0])
    print(functionWanted)
    if functionWanted is not None:
        return functionWanted(block, codebase)
    else:
        return block[0]
