import Config.b_star_interpreter.globals as globals


def define(name: str, item: any):
    if name in globals.codebase.variables[0]:
        globals.codebase.variables[0][name] = item
        return

    globals.codebase.variables[-1][name] = item
