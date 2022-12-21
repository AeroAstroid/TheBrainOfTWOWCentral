import Commands.bstar.interpreter.globals as globals
from Commands.bstar.interpreter.expression import Expression


def map_func(function, listToEdit):
    parsedListToEdit = Expression(listToEdit, globals.codebase)

    resultArray = []
    for item in parsedListToEdit:
        globals.codebase.variables[0]["map.iterator"] = item
        resultArray.append(Expression(function, globals.codebase))

    return resultArray
