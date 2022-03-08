import src.interpreter.globals as globals


def var(item, index):
    return globals.codebase.variables[item][index]
