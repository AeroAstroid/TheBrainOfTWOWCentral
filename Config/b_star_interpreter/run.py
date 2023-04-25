from random import choice
from traceback import format_exc

from typing import List, Union

import discord
from func_timeout import func_timeout, FunctionTimedOut
from lark import Tree

from Config.b_star_interpreter.Codebase import Codebase
from Config.b_star_interpreter.error_messages import unfunny_errmsg
from Config.b_star_interpreter.expression import Expression

# the discord user property is used for global ownership checking
import Config.b_star_interpreter.globals as globals
from Config.b_star_interpreter.parse import parseCode
from Config.b_star_interpreter.tempFunctionsFile import functions
from Config.b_star_interpreter.exceptions import BStarProgramRaisedException


def runCode(code: Tree, user: Union[discord.User, None] = None, arguments: List[str] = [], author: int = -1):
    try:
        return func_timeout(30, runCodeSandbox, args=(code, user, arguments, author))
    except FunctionTimedOut:
        return returnError("RUNTIME", "Timed out! (More than 30 seconds)")
    except Exception as error:
        return error


def runCodeSandbox(code: Tree, user: Union[discord.User, None] = None, arguments: List[str] = [], author: int = -1):
    # TODO: Trim up to three backticks from beginning and end of code
    parsed_code = parseCode(code).children
    globals.codebase = Codebase(parsed_code, user, arguments, author)
    globals.codebase.functions = globals.codebase.functions | functions

    for i, statement in enumerate(parsed_code):
        try:
            readLine(statement)
        except BStarProgramRaisedException as error:
            return f"{error}"
        except Exception as error:
            return returnError(statement, error, i)

    # print(codebase.variables)
    # print(codebase.output)
    if len(globals.codebase.output) == 0 or globals.codebase.output.isspace():
        return "⚠️: The code has ran successfully, but returned nothing!"
    if len(globals.codebase.output) > 4000:
        return f"⚠️: Output too long, only showing the first 3800 characters:\n\n```{globals.codebase.output[:3800]}```"
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


def returnError(statement, error, i):
    section = statement.pretty()

    errmsg = f"{choice(unfunny_errmsg)}\n\nError of type {type(error).__name__} at ```scala" \
             f"\n{section}" \
             f"```\n**{error}** (Error occurred at code block {i + 1})"
    if globals.debug.print_error:
        print(f"{errmsg}\n\n{format_exc()}")  # print stack trace too
    return errmsg
