import Config.b_star_interpreter.globals as globals
from Config.b_star_interpreter.expression import Expression
from Config.b_star_interpreter.parse import parseCode
from Config._bpp_functions import safe_cut
from Config._db import Database


def global_func(use, name, value):
    db = Database()

    if globals.codebase.global_limit < 50:
        if use == "DEFINE":
            check_filesize(value)
            if globalExists(db, name):
                if isOwnerGlobal(db, name, str(globals.codebase.author)): # author is an id #
                    editGlobal(db, name, value)
                    globals.codebase.global_limit += 1

                else:
                    raise PermissionError(f"You cannot edit global '**{name}**' as you are not the owner!")
            else:
                createGlobal(db, name, value)
                globals.codebase.global_limit += 1

        elif use == "VAR":
            if globalExists(db, name):
                possible_global = getGlobal(db, name)
                globals.codebase.global_limit += 1

                return to_type(possible_global[0], int(possible_global[1]))
            else:
                raise ValueError(f"Global '{name}' does not exist!")
    else:
        raise ValueError(
            "You have reached the __temporary__ global read/write limit of 50! Please make sure you're only using GLOBAL blocks when absolutely necessary.")


# TODO: Remove this duplicate function
def var_type(v):
    try:
        return [int, float, str, list].index(type(v))
    except IndexError:
        raise TypeError(f"Value {safe_cut(v)} could not be attributed to any valid data type")


def to_type(value, type):
    if type == 0:
        return int(value)
    elif type == 1:
        return float(value)
    elif type == 2:
        return str(value)
    elif type == 3:
        return list(value)
    else:
        raise ValueError("Global has invalid type!")


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
    var = db.get_entries("bsvariables", columns=["name", "value", "type"], conditions={"name": name})[0]
    return (var[1], var[2])


def check_filesize(value):
    if len(str(value)) > 150_000:
        raise ValueError("Global Input is too large! (150KB MAX)")
    else:
        return value
