import Config.b_star_interpreter.globals as globals
from Config.b_star_interpreter.exceptions import BStarUndefinedVariableException


# TODO: Inspect types further
def var(name: any, index: int | None = None):
    variable = globals.codebase.variables[name]
    if variable is None:
        raise BStarUndefinedVariableException(f"variable not found: {name}")

    if index == "":
        return variable
    else:
        return variable[index]
