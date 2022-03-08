import src.interpreter.globals as globals


def var(item, index):
    if index == "":
        return globals.codebase.variables[item]
    else:
        return globals.codebase.variables[item][index]
