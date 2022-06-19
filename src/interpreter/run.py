from random import choice
from traceback import format_exc

from typing import List, Union

import discord
from func_timeout import func_timeout, FunctionTimedOut

from src.interpreter.Codebase import Codebase
from src.interpreter.error_messages import unfunny_errmsg
from src.interpreter.expression import Expression

# the discord user property is used for global ownership checking
import src.interpreter.globals as globals
from src.interpreter.parse import parseCode
from src.interpreter.tempFunctionsFile import functions


def runCode(code: str, user: Union[discord.User, None] = None, arguments: List[str] = None):
    try:
        return func_timeout(30, runCodeSandbox, args=(code, user, arguments))
    except FunctionTimedOut:
        return returnError("RUNTIME", "Timed out! (More than 30 seconds)")
    except Exception as error:
        return error


def runCodeSandbox(code: str, user: Union[discord.User, None] = None, arguments: List[str] = None):
    # TODO: Trim up to three backticks from beginning and end of code
    parsed_code = parseCode(code)
    globals.codebase = Codebase(parsed_code, user, arguments)
    globals.codebase.functions = globals.codebase.functions | functions

    for statement in parsed_code:
        try:
            readLine(statement)
        except Exception as error:
            return returnError(statement, error)

    # print(codebase.variables)
    # print(codebase.output)
    if len(globals.codebase.output) == 0 or globals.codebase.output.isspace():
        return "⚠️: The code has ran successfully, but returned nothing!"
    if len(globals.codebase.output) > 2000:
        return f"⚠️: Output too long, only showing the first 1000 characters:\n\n```{globals.codebase.output[:1000]}```"
    return globals.codebase.output


def readLine(statement):
    if type(statement) == str:
        result = statement
    else:
        result = Expression(statement, globals.codebase)

    # this prints the result code if you need it
    # print(result)
    if result is not None:
        globals.codebase.output += str(result)


def returnError(statement, error):
    errmsg = f"{choice(unfunny_errmsg)}\n\nError of type {type(error).__name__} at `{statement}`:\n{error}"
    if globals.debug.print_error:
        print(f"{errmsg}\n\n{format_exc()}")  # print stack trace too
    return errmsg
