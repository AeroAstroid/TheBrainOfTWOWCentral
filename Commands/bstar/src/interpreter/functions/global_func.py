import Commands.bstar.src.interpreter.globals as globals
from Commands.bstar.src.database.s3 import getGlobal, globalExists, isOwnerGlobal, editGlobal, createGlobal
from Commands.bstar.src.interpreter.expression import Expression
from Commands.bstar.src.interpreter.parse import parseCode


def global_func(use, name, value):
    if globals.codebase.global_limit < 50:
        if use == "DEFINE":
            if globalExists(name):
                if isOwnerGlobal(name, globals.codebase.user.id):
                    editGlobal(globals.codebase.user, name, check_filesize(value))
                    globals.codebase.global_limit += 1

                else:
                    raise PermissionError(f"You cannot edit global '**{name}**' as you are not the owner!")
            else:
                createGlobal(globals.codebase.user, name, check_filesize(value))
                globals.codebase.global_limit += 1

        elif use == "VAR":
            possible_global = getGlobal(name)
            globals.codebase.global_limit += 1

            if possible_global is None:
                raise ValueError(f"Global '{name}' does not exist!")
            else:
                # TODO: Create an easier & faster way to find the type of a string
                val = parseCode("[BLOCK " + possible_global["value"] + "]").children[0].children[1]
                return Expression(val, globals.codebase)
    else:
        raise ValueError("You have reached the __temporary__ global read/write limit of 50! Please make sure you're only using GLOBAL blocks when absolutely necessary.")

def check_filesize(value):
    if len(str(value)) > 150_000:
        raise ValueError("Global Input is too large! (150KB MAX)")
    else:
        return value
