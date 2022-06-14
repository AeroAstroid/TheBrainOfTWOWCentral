import src.interpreter.globals as globals


def define(name, item):
    for i, val in reversed(list(enumerate(globals.codebase.variables))):
        if name in val:
            globals.codebase.variables[i][name] = item
            return

    globals.codebase.variables[-1][name] = item
