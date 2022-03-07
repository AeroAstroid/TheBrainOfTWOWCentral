import src.interpreter.globals as globals


def var(item):
    return globals.codebase.variables[item]
