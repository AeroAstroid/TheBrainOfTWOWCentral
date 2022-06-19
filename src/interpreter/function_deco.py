import math

from src.interpreter.function import Function
from src.interpreter.functions.args import args
from src.interpreter.functions.array import array
from src.interpreter.functions.choose import choose
from src.interpreter.functions.choosechar import choosechar
from src.interpreter.functions.comment import comment
from src.interpreter.functions.compare import compare
from src.interpreter.functions.concat import concat
from src.interpreter.functions.define import define
from src.interpreter.functions.find import find
from src.interpreter.functions.func import func
from src.interpreter.functions.global_func import global_func
from src.interpreter.functions.if_func import if_func
from src.interpreter.functions.import_func import import_func
from src.interpreter.functions.index import index
from src.interpreter.functions.setindex import setindex
from src.interpreter.functions.j import j
from src.interpreter.functions.join import join
from src.interpreter.functions.joinall import joinall
from src.interpreter.functions.length import length
from src.interpreter.functions.loop import loop
from src.interpreter.functions.randint import randint
from src.interpreter.functions.random_func import random_func
from src.interpreter.functions.repeat import repeat
from src.interpreter.functions.replace import replace_func
from src.interpreter.functions.round import round_func
from src.interpreter.functions.slice import slice_func
from src.interpreter.functions.split import split
from src.interpreter.functions.time_func import time_func
from src.interpreter.functions.try_func import try_func
from src.interpreter.functions.user_func import user_func
from src.interpreter.functions.userid import userid
from src.interpreter.functions.username import username
from src.interpreter.functions.var import var
from src.interpreter.functions.while_func import while_func
from src.interpreter.functions.block import block
from src.interpreter.functions.return_func import return_func
from src.interpreter.functions.raise_func import raise_func

from src.interpreter.functions.math.abs import abs_func
from src.interpreter.functions.math.add import add
from src.interpreter.functions.math.ceil import ceil
from src.interpreter.functions.math.div import div
from src.interpreter.functions.math.floor import floor
from src.interpreter.functions.math.math import math_func
from src.interpreter.functions.math.mod import mod
from src.interpreter.functions.math.mul import mul
from src.interpreter.functions.math.pow import pow_func
from src.interpreter.functions.math.sub import sub


class ArgumentType:
    Required = None
    Variadic = math.inf


def setupFunctions():
    Function(["abs"], {"number": ArgumentType.Required}, abs_func)
    Function(["add", "sum"], {"number": ArgumentType.Required, "bys": ArgumentType.Variadic}, add)
    Function(["ceil"], {"number": ArgumentType.Required}, ceil)
    Function(["div", "divide"], {"dividend": ArgumentType.Required, "divisors": ArgumentType.Variadic}, div)
    Function(["floor"], {"number": ArgumentType.Required}, floor)
    Function(["math"], {"number": ArgumentType.Required, "operator": ArgumentType.Required, "by": ArgumentType.Required}, math_func)
    Function(["mod"], {"number": ArgumentType.Required, "bys": ArgumentType.Variadic}, mod)
    Function(["mul", "multiply", "product"], {"number": ArgumentType.Required, "bys": ArgumentType.Variadic}, mul)
    Function(["pow"], {"number": ArgumentType.Required, "bys": ArgumentType.Variadic}, pow_func)
    Function(["sub", "subtract", "difference"], {"number": ArgumentType.Required, "bys": ArgumentType.Variadic}, sub)

    Function(["args"], {"index": ""}, args)
    Function(["array"], {"arr": ArgumentType.Variadic}, array)
    Function(["choose"], {"arr": ArgumentType.Variadic}, choose)
    Function(["choosechar"], {"string": ArgumentType.Required}, choosechar)
    Function(["compare"], {"v1": ArgumentType.Required, "operator": ArgumentType.Required, "v2": ArgumentType.Required}, compare)
    Function(["concat"], {"items": ArgumentType.Variadic}, concat)
    Function(["define"], {"name": ArgumentType.Required, "item": ArgumentType.Required}, define)
    
    Function(["find", "indexof"], {"array": ArgumentType.Required, "element": ArgumentType.Required}, find)
    Function(["func", "function"], {"name": ArgumentType.Required, "args": ArgumentType.Required, "body": ArgumentType.Required}, func, parse_args=False)
    Function(["return", "ret"], {"result": ArgumentType.Required}, return_func)
    Function(["global"], {"use": ArgumentType.Required, "name": ArgumentType.Required, "value": 0}, global_func)
    Function(["if"], {"compare": ArgumentType.Required, "true": ArgumentType.Required, "false": ArgumentType.Required}, if_func, parse_args=False)
    Function(["index"], {"arr": ArgumentType.Required, "number": ArgumentType.Required}, index)
    Function(["import"], {"name": ArgumentType.Required}, import_func)
    Function(["setindex"], {"arr": ArgumentType.Required, "index": ArgumentType.Required, "value": ARgumentType.Required}, setindex)

    Function(["length"], {"arr": ArgumentType.Required}, length)
    Function(["loop"], {"amount": ArgumentType.Required, "body": ArgumentType.Required}, loop, parse_args=False)

    Function(["j"], {"amount": 1}, j)
    Function(["join"], {"array": ArgumentType.Required, "joiner": ""}, join)
    Function(["joinall"], {"array": ArgumentType.Required}, joinall)

    Function(["randint"], {"minimum": ArgumentType.Required, "maximum": ArgumentType.Required}, randint)
    Function(["random"], {"minimum": 0, "maximum": 1}, random_func)

    Function(["repeat"], {"item": ArgumentType.Required, "amount": ArgumentType.Required}, repeat)
    Function(["raise"], {"message": ArgumentType.Required}, raise_func)
    Function(["round"], {"number": ArgumentType.Required}, round_func)
    Function(["replace"], {"string": ArgumentType.Required, "match": ArgumentType.Required, "replace": ArgumentType.Required}, replace_func)
    Function(["slice"], {"array": ArgumentType.Required, "index_start": ArgumentType.Required, "index_end": ArgumentType.Required}, slice_func)
    Function(["split"], {"string": ArgumentType.Required, "seperator": " "}, split)

    Function(["time"], {}, time_func)
    Function(["try"], {"attempt": ArgumentType.Required, "on_error": ArgumentType.Required}, try_func, parse_args=False)
    Function(["user"], {"userItemToGet": ArgumentType.Required}, user_func)
    Function(["username"], {}, username)
    Function(["userid"], {}, userid)
    Function(["var"], {"item": ArgumentType.Required, "index": ""}, var)
    Function(["while"], {"condition": ArgumentType.Required, "body": ArgumentType.Required}, while_func, parse_args=False)
    Function(["block"], {"body": ArgumentType.Variadic}, block, parse_args=False)
    Function(["#"], {"comments": ArgumentType.Variadic}, comment)

    Function(["str"], {"item": ArgumentType.Required}, str)
    Function(["int"], {"item": ArgumentType.Required}, int)
    Function(["float"], {"item": ArgumentType.Required}, float)
    # Function(["#"], {"*": ArgumentType.Variadic}, lambda x: ArgumentType.Required)


setupFunctions()
