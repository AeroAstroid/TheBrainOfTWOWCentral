from random import choice
from traceback import format_exc

from typing import List, Union, Dict

import discord

from src.interpreter import tempFunctionsFile
from src.interpreter.Codebase import Codebase
from src.interpreter.error_messages import unfunny_errmsg
from src.interpreter.expression import Expression


# the discord user property is used for global ownership checking
import src.interpreter.globals as globals
from src.interpreter.parse import parseCode
from src.interpreter.tempFunctionsFile import functions


def runCode(code: str, user: Union[discord.User, None] = None, arguments: List[str] = None):
    # TODO: Trim up to three backticks from beginning and end of code
    parsed_code = parseCode(code)
    globals.codebase = Codebase(parsed_code, user, arguments)
    globals.codebase.functions = globals.codebase.functions | functions

    for statement in parsed_code:
        try:
            if type(statement) == str:
                result = statement
            else:
                result = Expression(statement, globals.codebase)

            print(result)
            if result is not None:
                globals.codebase.output += str(result)

        except Exception as e:
            # errmsg = f"ERROR at `{statement}`:\n{e}"
            errmsg = f"{choice(unfunny_errmsg)}\n\nERROR at `{statement}`:\n{e}"
            print(f"{errmsg}\n\n{format_exc()}")  # print stack trace too
            return errmsg

    # print(codebase.variables)
    # print(codebase.output)
    if len(globals.codebase.output) == 0:
        return "NOTICE: The code has successfully ran, but returned nothing!"
    if len(globals.codebase.output) > 2000:
        return "ERROR: Output too long!"
    return globals.codebase.output
