import Commands.b_star.interpreter.globals as globals


def args(index):
    if index == "":
        return globals.codebase.arguments
    else:
        try:
            return globals.codebase.arguments[index]
        except IndexError:
            return ""
