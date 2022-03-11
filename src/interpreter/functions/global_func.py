import src.interpreter.globals as globals
from src.database.s3 import getGlobal, globalExists, isOwnerGlobal, editGlobal, createGlobal


def global_func(use, name, value):
    if use == "DEFINE":
        if globalExists(name):
            if isOwnerGlobal(name, globals.codebase.user.id):
                editGlobal(globals.codebase.user, name, check_filesize(value))
            else:
                raise PermissionError(f"You cannot edit global '**{name}**' as you are not the owner!")
        else:
            createGlobal(globals.codebase.user, name, check_filesize(value))
    elif use == "VAR":
        possible_global = getGlobal(name)
        if possible_global is None:
            raise ValueError(f"Global '{name}' does not exist!")
        else:
            return possible_global["value"]


def check_filesize(value):
    if len(value) > 150_000:
        raise ValueError("Global Input is too large! (150KB MAX)")
    else:
        return value
