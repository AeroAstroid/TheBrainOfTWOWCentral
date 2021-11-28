from typing import List

from src.database.s3 import getGlobal, globalExists, isOwnerGlobal, editGlobal, createGlobal
from src.interpreter.expression import Expression


def global_func(block: List, codebase):

    name = Expression(block[2], codebase)
    if block[1] == "DEFINE":
        value = Expression(block[3], codebase)

        if globalExists(name):
            if isOwnerGlobal(name, codebase.user.id):
                editGlobal(codebase.id, name, value)
            else:
                raise PermissionError(f"You cannot edit global '{name}' as you are not the owner!")
        else:
            createGlobal(codebase.user, name, value)
    elif block[1] == "VAR":
        possible_global = getGlobal(name)
        if possible_global is None:
            raise ValueError(f"Global '{name}' does not exist!")
        else:
            return possible_global["value"]