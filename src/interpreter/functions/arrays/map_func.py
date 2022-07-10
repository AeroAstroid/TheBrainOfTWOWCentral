import copy

from lark import Token, Tree

import src.interpreter.globals as globals
from src.interpreter.expression import Expression


def map_func(function, listToEdit):
    # The strategy is rebuild the parser tree to add a argument to the function
    # TODO: no "meta" args in Tree() may be a problem in the future?

    newArray = []
    for item in listToEdit.children:
        # deepcopy might become very slow based on depth? idk
        newItem = [
            # Tree(Token("RULE", "block"), copy.deepcopy(function.children[0].children)),
            copy.deepcopy(function.children[0]), # the function
            *function.children[1:],              # the arguments in the function
            item                                 # the item, to be added as an argument, in the function
        ]

        newItemBuilder = Tree(Token("RULE", "function"), newItem)
        newArray.append(newItemBuilder)

    builder = Tree(Token("RULE", "array"), newArray)
    return Expression(builder, globals.codebase)
