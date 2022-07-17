import src.interpreter.globals as globals


def args(index):
    if index == "":
        return globals.codebase.arguments
    else:
        arg = globals.codebase.arguments[index]
        if arg is None:
            return ""

        return arg
