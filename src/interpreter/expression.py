# imports -- TODO: split this
from typing import Union
from typing import List


# expression defining
import src.interpreter.function_deco


def Expression(block: Union[List, str], codebase):
    # TODO: try/except needed

    # Literal or Numeral
    if type(block) != list:
        if block.isnumeric():
            # TODO: Better way of doing this (without try/except)
            try:
                return int(block)
            except ValueError:
                return float(block)
        else:
            return block

    functionWanted = src.interpreter.function_deco.functions.get(block[0])
    print(functionWanted)
    if functionWanted is not None:
        return functionWanted(block, codebase)
    else:
        return block[0]
