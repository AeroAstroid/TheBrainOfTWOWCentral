import Commands.bstar.interpreter.globals as globals


def var(item, index):
    for val in reversed(globals.codebase.variables):
        if item in val:
            if index == "":
                return val[item]
            else:
                return val[item][index]

    raise KeyError(f"variable not found: {item}")
