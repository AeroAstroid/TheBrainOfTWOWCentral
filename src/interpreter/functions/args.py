import src.interpreter.globals as globals


def args(index):
    if index == "":
        return globals.codebase.arguments
    else:
        return globals.codebase.arguments[index]
