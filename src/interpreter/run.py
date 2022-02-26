from random import choice
from traceback import format_exc

from typing import List, Union, Dict

import discord

from src.interpreter.error_messages import unfunny_errmsg
from src.interpreter.expression import Expression


# the discord user property is used for global ownership checking
from src.interpreter.function_deco import functions
from src.interpreter.parse import parseCode
from src.interpreter.userfunction import UserFunction


class Codebase:
    def __init__(self, lines, user, arguments):
        self.lines: List[str] = lines
        self.variables: Dict[str, str] = {}
        self.functions: Dict[str, UserFunction] = {}
        self.user: Union[discord.User, None] = user
        self.arguments: Union[List[str], None] = arguments
        self.output: str = ""


def runCode(code: str, user: Union[discord.User, None] = None, arguments: List[str] = None):
    # TODO: Trim up to three backticks from beginning and end of code
    parsed_code = parseCode(code)
    codebase = Codebase(parsed_code, user, arguments)
    codebase.functions = codebase.functions | functions

    for statement in parsed_code:
        try:
            if type(statement) == str:
                result = statement
            else:
                result = Expression(statement, codebase)

            print(result)
            if result is not None:
                codebase.output += str(result)

        except Exception as e:
            # errmsg = f"ERROR at `{statement}`:\n{e}"
            errmsg = f"{choice(unfunny_errmsg)}\n\nERROR at `{statement}`:\n{e}"
            print(f"{errmsg}\n\n{format_exc()}")  # print stack trace too
            return errmsg

    # print(codebase.variables)
    # print(codebase.output)
    if len(codebase.output) == 0:
        return "NOTICE: The code has successfully ran, but returned nothing!"
    if len(codebase.output) > 2000:
        return "ERROR: Output too long!"
    return codebase.output
