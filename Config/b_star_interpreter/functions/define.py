import Config.b_star_interpreter.globals as globals


def define(name: str, item: any):
    globals.codebase.variables[name] = item
