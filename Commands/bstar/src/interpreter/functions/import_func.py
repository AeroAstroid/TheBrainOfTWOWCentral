import Commands.bstar.src.interpreter.globals as globals
from Commands.bstar.src.database.s3 import getTag
from Commands.bstar.src.interpreter.expression import Expression
from Commands.bstar.src.interpreter.parse import parseCode


def import_func(name):
    tag = getTag(name)
    if tag is None:
        raise Exception(f"Tag **{name}** not found!")
    else:
        # Add it to the codebase functions
        # TODO: Remove this hack (by adding a FUNCS row to the tag database)
        # TODO: This is outdated
        code = parseCode(tag["program"])
        funcLines = []
        for line in code:
            if type(line) is list:
                if line[0] == "func" or "FUNC" or "function" or "FUNCTION":
                    funcLines.append(line)

        for func in funcLines:
            Expression(func, globals.codebase)
