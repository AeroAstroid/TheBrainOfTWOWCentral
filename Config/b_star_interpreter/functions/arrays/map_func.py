import Config.b_star_interpreter.globals as globals
from Config.b_star_interpreter.expression import Expression


def map_func(function, listToEdit):
    parsedListToEdit = Expression(listToEdit, globals.codebase)

    resultArray = []
    for item in parsedListToEdit:
        globals.codebase.variables[0]["map.iterator"] = item
        globals.codebase.variables[0]["map.i"] = item
        res = Expression(function, globals.codebase)
        if res is not None:
            resultArray.append(res)

    return resultArray or None
