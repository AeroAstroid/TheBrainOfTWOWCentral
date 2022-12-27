import Commands.b_star.interpreter.globals as globals
from Commands.b_star.interpreter.expression import Expression
from Commands.b_star.interpreter.parse import parseCode
from Config._bppnew_functions import safe_cut
from Config._db import Database


def global_func(use, name, value):
    db = Database()

    if globals.codebase.global_limit < 50:
        if use == "DEFINE":
            check_filesize(value)
            if globalExists(db, name):
                if isOwnerGlobal(db, name, str(globals.codebase.user.id)):
                    editGlobal(db, name, value)
                    globals.codebase.global_limit += 1

                else:
                    raise PermissionError(f"You cannot edit global '**{name}**' as you are not the owner!")
            else:
                createGlobal(db, name, value)
                globals.codebase.global_limit += 1

        elif use == "VAR":
            possible_global = getGlobal(db, name)
            globals.codebase.global_limit += 1

            if possible_global is None:
                raise ValueError(f"Global '{name}' does not exist!")
            else:
                # TODO: Create an easier & faster way to find the type of a string
                val = parseCode("[BLOCK " + possible_global + "]").children[0].children[1]
                return Expression(val, globals.codebase)
    else:
        raise ValueError(
            "You have reached the __temporary__ global read/write limit of 50! Please make sure you're only using GLOBAL blocks when absolutely necessary.")


# TODO: Remove this duplicate function
def var_type(v):
    try:
        return [int, float, str, list].index(type(v))
    except IndexError:
        raise TypeError(f"Value {safe_cut(v)} could not be attributed to any valid data type")


def globalExists(db, name):
    var = db.get_entries("bsvariables", columns=["name", "owner"], conditions={"name": name})
    return len(var)


def isOwnerGlobal(db, name, id):
    var = db.get_entries("bsvariables", columns=["name", "owner"], conditions={"name": name})[0]
    return var[1] == id


def createGlobal(db, name, value):
    # db.add_entry("b++2variables", [v_name, str(v_value), var_type(v_value), str(author)])
    db.add_entry("bsvariables", [name, str(value), var_type(value), globals.codebase.user.id])


def editGlobal(db, name, value):
    db.edit_entry("bsvariables", entry={"value": str(value), "type": var_type(value)}, conditions={"name": name})


def getGlobal(db, name):
    var = db.get_entries("bsvariables", columns=["name", "value"], conditions={"name": name})[0]
    return var[1]


def check_filesize(value):
    if len(str(value)) > 150_000:
        raise ValueError("Global Input is too large! (150KB MAX)")
    else:
        return value
