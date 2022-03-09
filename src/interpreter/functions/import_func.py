import src.interpreter.globals as globals
from src.database.s3 import getTag
from src.interpreter.expression import Expression
from src.interpreter.parse import parseCode


def import_func(name):
    tag = getTag(name)
    if tag is None:
        raise Exception(f"Tag **{name}** not found!")
    else:
        # Add it to the codebase functions
        Expression(parseCode(tag["program"])[0], globals.codebase)
