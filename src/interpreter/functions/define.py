import src.interpreter.globals as globals


def define(name, item):
    globals.codebase.variables[name] = item
