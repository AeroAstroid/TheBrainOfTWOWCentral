from random import choice
from traceback import format_exc

import discord
from func_timeout import func_timeout, FunctionTimedOut
from lark import Tree

from Config.b_star_interpreter.Codebase import Codebase
from Config.b_star_interpreter.error_messages import unfunny_errmsg
from Config.b_star_interpreter.expression import Expression

# the discord user property is used for global ownership checking
import Config.b_star_interpreter.globals as globals
from Config.b_star_interpreter.newpasta import parser, Node
# from Config.b_star_interpreter.parse import parseCode
from Config.b_star_interpreter.tempFunctionsFile import functions
from Config.b_star_interpreter.functions.raise_func import BStarProgramRaisedException


def runCode(code: Tree, user: discord.User | None = None, arguments: list[str] = [], author = None):
    try:
        # return func_timeout(30, runCodeSandbox, args=(code, user, arguments))
        return runCodeSandbox(code, user, arguments, author)
    except FunctionTimedOut:
        return returnError(code, "RUNTIME", "Timed out! (More than 30 seconds)")
    except Exception as error:
        return error


def runCodeSandbox(code: Tree, user: discord.User | None = None, arguments: list[str] = [], author = None):
    # TODO: Trim up to three backticks from beginning and end of code
    # parsed_code = parseCode(code).children

    # root node
    root = parser(code)
    globals.codebase = Codebase(root, user, arguments, author)
    globals.codebase.functions = globals.codebase.functions | functions

    for i, statement in enumerate(root.children):
        globals.codebase.output += "\n"

        try:
            result = readLine(statement)
            if result is not None:
                if not result:
                    globals.codebase.output += "\n"
        # except BStarProgramDefinedException as error:
        #     return f"{error}"
        except Exception as error:
            return returnError(code, statement, error)

    # print(codebase.variables)
    # print(codebase.output)
    if len(globals.codebase.output) == 0 or globals.codebase.output.isspace():
        return "⚠️: The code has ran successfully, but returned nothing!"
    if len(globals.codebase.output) > 4000:
        return f"⚠️: Output too long, only showing the first 3800 characters:\n\n```{globals.codebase.output[:3800]}```"
    return globals.codebase.output


def readLine(statement: Node):
    # if type(statement) == str:
    #     result = statement
    # else:
    #     result = Expression(statement, globals.codebase)

    # if len(statement.children) == 0:
    #     result = Expression(statement, globals.codebase)
    # else:
    result = Expression(statement, globals.codebase)

    # this prints the result code if you need it
    # print(result)
    if result is not None:
        globals.codebase.output += str(result)
        return str(result)
    else:
        return None


# def parseArguments(args: List[str]):
#     result = []
#     for arg in args:
#         match type(arg):
#             case "int":
#                 result.append(int(arg))
#
#             case "float":
#
#             case _:
#                 result.append(arg)


def returnError(code, block, error):
    # s = f"Line **{block.file_line}**, (**{block.file_start}**:**{block.file_end}**)"
    # section = block.pretty()
    line = code.split("\\n")[block.file_line - 1]
    before = line[block.file_start - 11:block.file_start - 1]
    problem_code = line[block.file_start - 1:block.file_end]
    problem_code_length = max(len(problem_code), 1)
    # problem_code = block.raw
    after = line[block.file_end:block.file_end + 10]

    type_name = type(error).__name__
    # errmsg = f"{choice(unfunny_errmsg)}\n\nError of type {type_name} at ```scala" \
    #          f"```\n**{error}** ({s})"

    before_el = "[2;31m[2;30m...[0m[2;31m[2;37m[0m[2;31m[0m" if len(before) >= 10 else ""
    after_el = "[2;31m[2;30m...[0m[2;31m[2;37m[0m[2;31m[0m" if len(after) >= 10 else ""

    before_el_real = "..." if len(before) >= 10 else ""

    errmsg = f"""
    {choice(unfunny_errmsg)}
    ```ansi
[0;31m[2;31merror[0;31m[0;31m[0;31m[0;31m[0;31m[0;31m[0;31m[0;31m[0;37m[1;37m: {type_name}[0m[0;37m
[0;34m  --> [0;37m[1;37mline {block.file_line}, {block.file_start}:{block.file_end}[0m[0;37m[0m[0;34m
   |
 {block.file_line} |    {before_el}[0;37m{before}[0m[0;34m[0;31m{problem_code}[0m[0;34m[0;37m{after}[0m[0;34m{after_el}[0m[0;37m[0m[0;34m
   |    {" "*len(before_el_real + before)}[0;31m[1;31m{"^"*problem_code_length} {error}[0m[0;31m[0m[0;34m[0m[0;37m
[0m[0;31m[0m[0;31m[0m[0;31m[0m[0;31m[0m[0;31m[0m[0;31m[0m[0;31m[0m[0;31m[0m[2;31m[0m[2;31m[0m
```"""

    if globals.debug.print_error:
        print(f"{errmsg}\n\n{format_exc()}")  # print stack trace too
    return errmsg
