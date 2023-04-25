import Config.b_star_interpreter.globals as globals
from Config.b_star_interpreter.expression import Expression


# TODO: Inspect types further
def map_func(function: any, listToEdit: any):
    parsedListToEdit = Expression(listToEdit, globals.codebase)

    resultArray = []
    for item in parsedListToEdit:
        globals.codebase.variables["map.iterator"] = item
        globals.codebase.variables["map.i"] = item
        res = Expression(function, globals.codebase)
        if res is not None:
            resultArray.append(res)

    return resultArray or None
