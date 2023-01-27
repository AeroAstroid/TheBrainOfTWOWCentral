import math

from Config.b_star_interpreter.function import Function
from Config.b_star_interpreter.functions.args import args
from Config.b_star_interpreter.functions.array import array
from Config.b_star_interpreter.functions.choose import choose
from Config.b_star_interpreter.functions.comment import comment
from Config.b_star_interpreter.functions.compare import compare
from Config.b_star_interpreter.functions.concat import concat
from Config.b_star_interpreter.functions.define import define
from Config.b_star_interpreter.functions.find import find
from Config.b_star_interpreter.functions.func import func
from Config.b_star_interpreter.functions.global_func import global_func
from Config.b_star_interpreter.functions.if_func import if_func
from Config.b_star_interpreter.functions.import_func import import_func
from Config.b_star_interpreter.functions.index import index
from Config.b_star_interpreter.functions.setindex import setindex
from Config.b_star_interpreter.functions.j import j
from Config.b_star_interpreter.functions.join import join
from Config.b_star_interpreter.functions.joinall import joinall
from Config.b_star_interpreter.functions.length import length
from Config.b_star_interpreter.functions.loop import loop
from Config.b_star_interpreter.functions.randint import randint
from Config.b_star_interpreter.functions.random_func import random_func
from Config.b_star_interpreter.functions.range_func import range_func
from Config.b_star_interpreter.functions.repeat import repeat
from Config.b_star_interpreter.functions.replace import replace_func
from Config.b_star_interpreter.functions.round import round_func
from Config.b_star_interpreter.functions.slice import slice_func
from Config.b_star_interpreter.functions.split import split
from Config.b_star_interpreter.functions.time_func import time_func
from Config.b_star_interpreter.functions.try_func import try_func
from Config.b_star_interpreter.functions.type_func import type_func
from Config.b_star_interpreter.functions.user_func import user_func
from Config.b_star_interpreter.functions.userid import userid
from Config.b_star_interpreter.functions.username import username
from Config.b_star_interpreter.functions.var import var
from Config.b_star_interpreter.functions.while_func import while_func
from Config.b_star_interpreter.functions.block import block
from Config.b_star_interpreter.functions.return_func import return_func
from Config.b_star_interpreter.functions.raise_func import raise_func

from Config.b_star_interpreter.functions.arrays.map_func import map_func
from Config.b_star_interpreter.functions.arrays.max_func import max_func
from Config.b_star_interpreter.functions.arrays.min_func import min_func
from Config.b_star_interpreter.functions.arrays.randomizer import randomizer
from Config.b_star_interpreter.functions.arrays.sort_func import sort_func

from Config.b_star_interpreter.functions.math.abs import abs_func
from Config.b_star_interpreter.functions.math.add import add
from Config.b_star_interpreter.functions.math.ceil import ceil
from Config.b_star_interpreter.functions.math.div import div
from Config.b_star_interpreter.functions.math.factorial import factorial
from Config.b_star_interpreter.functions.math.floor import floor
from Config.b_star_interpreter.functions.math.log import log
from Config.b_star_interpreter.functions.math.math import math_func
from Config.b_star_interpreter.functions.math.mod import mod
from Config.b_star_interpreter.functions.math.mul import mul
from Config.b_star_interpreter.functions.math.pow import pow_func
from Config.b_star_interpreter.functions.math.sub import sub

from Config.b_star_interpreter.functions.math.cos import cos
from Config.b_star_interpreter.functions.math.sin import sin
from Config.b_star_interpreter.functions.math.tan import tan


class ArgumentType:
    Required = None
    Variadic = math.inf


def setupFunctions():
    Function(["abs"], {"number": ArgumentType.Required}, abs_func)
    Function(["add", "sum", "+"], {"number": ArgumentType.Required, "bys": ArgumentType.Variadic}, add)
    Function(["ceil"], {"number": ArgumentType.Required}, ceil)
    Function(["div", "divide", "/"], {"dividend": ArgumentType.Required, "divisors": ArgumentType.Variadic}, div)
    Function(["factorial"], {"number": ArgumentType.Required}, factorial)
    Function(["floor"], {"number": ArgumentType.Required}, floor)
    Function(["log"], {"number": ArgumentType.Required, "bys": ArgumentType.Variadic}, log)
    Function(["math"], {"number": ArgumentType.Required, "operator": ArgumentType.Required, "by": ArgumentType.Required}, math_func)
    Function(["mod", "%"], {"number": ArgumentType.Required, "bys": ArgumentType.Variadic}, mod)
    Function(["mul", "multiply", "product", "*"], {"number": ArgumentType.Required, "bys": ArgumentType.Variadic}, mul)
    Function(["pow", "^"], {"number": ArgumentType.Required, "bys": ArgumentType.Variadic}, pow_func)
    Function(["sub", "subtract", "difference", "-"], {"number": ArgumentType.Required, "bys": ArgumentType.Variadic}, sub)

    Function(["cos", "cosine"], {"number": ArgumentType.Required}, cos)
    Function(["sin", "sine"], {"number": ArgumentType.Required}, sin)
    Function(["tan", "tangent"], {"number": ArgumentType.Required}, tan)


    Function(["args"], {"index": ""}, args)
    Function(["array"], {"arr": ArgumentType.Variadic}, array)
    Function(["choose", "choosechar"], {"arr": ArgumentType.Variadic}, choose)
    Function(["compare"], {"v1": ArgumentType.Required, "operator": ArgumentType.Required, "v2": ArgumentType.Required}, compare)
    Function(["concat"], {"items": ArgumentType.Variadic}, concat)
    Function(["define", "def"], {"name": ArgumentType.Required, "item": ArgumentType.Required}, define)

    Function(["find", "indexof"], {"array": ArgumentType.Required, "element": ArgumentType.Required}, find)
    Function(["func", "function"], {"name": ArgumentType.Required, "args": ArgumentType.Required, "body": ArgumentType.Required}, func, parse_args=False)
    Function(["return", "ret"], {"result": ArgumentType.Required}, return_func)
    Function(["global"], {"use": ArgumentType.Required, "name": ArgumentType.Required, "value": 0}, global_func)
    Function(["if"], {"compare": ArgumentType.Required, "true": ArgumentType.Required, "false": False}, if_func, parse_args=False)
    Function(["index"], {"arr": ArgumentType.Required, "number": ArgumentType.Required}, index)
    Function(["import"], {"name": ArgumentType.Required}, import_func)
    Function(["setindex"], {"arr": ArgumentType.Required, "index": ArgumentType.Required, "value": ArgumentType.Required}, setindex)

    Function(["length"], {"arr": ArgumentType.Required}, length)
    Function(["loop"], {"amount": ArgumentType.Required, "body": ArgumentType.Required}, loop, parse_args=False)

    Function(["j"], {"amount": 1}, j)
    Function(["join"], {"array": ArgumentType.Required, "joiner": ""}, join)
    Function(["joinall"], {"array": ArgumentType.Required}, joinall)

    Function(["randint"], {"minimum": ArgumentType.Required, "maximum": ArgumentType.Required}, randint)
    Function(["random"], {"minimum": 0, "maximum": 1}, random_func)
    Function(["randomizer", "shuffle"], {"array": ArgumentType.Required}, randomizer)

    Function(["range"], {"index_start": ArgumentType.Required, "index_end": ArgumentType.Required, "index_step": 1}, range_func)
    Function(["repeat"], {"item": ArgumentType.Required, "amount": ArgumentType.Required}, repeat)
    Function(["raise", "throw"], {"message": ArgumentType.Required}, raise_func)
    Function(["round"], {"number": ArgumentType.Required}, round_func)
    Function(["replace"], {"string": ArgumentType.Required, "match": ArgumentType.Required, "replace": ArgumentType.Required}, replace_func)
    Function(["slice"], {"array": ArgumentType.Required, "index_start": ArgumentType.Required, "index_end": ArgumentType.Required, "index_step": 1}, slice_func)
    Function(["split"], {"string": ArgumentType.Required, "seperator": " "}, split)

    Function(["time"], {}, time_func)
    Function(["try"], {"attempt": ArgumentType.Required, "on_error": ArgumentType.Required}, try_func, parse_args=False)
    Function(["type"], {"a": ArgumentType.Required}, type_func, parse_args=False)
    Function(["user"], {"userItemToGet": ""}, user_func)
    Function(["username"], {}, username)
    Function(["userid"], {}, userid)
    Function(["var"], {"item": ArgumentType.Required, "index": ""}, var)
    Function(["while"], {"condition": ArgumentType.Required, "body": ArgumentType.Required}, while_func, parse_args=False)
    Function(["block"], {"body": ArgumentType.Variadic}, block, parse_args=False)
    Function(["#"], {"comments": ArgumentType.Variadic}, comment)

    Function(["min"], {"array": ArgumentType.Required}, min_func)
    Function(["max"], {"array": ArgumentType.Required}, max_func)
    Function(["map"], {"function": ArgumentType.Required, "listToEdit": ArgumentType.Required}, map_func, parse_args=False)
    Function(["sort"], {"array": ArgumentType.Required}, sort_func)

    Function(["str"], {"item": ArgumentType.Required}, str)
    Function(["int"], {"item": ArgumentType.Required}, int)
    Function(["float"], {"item": ArgumentType.Required}, float)
    Function(["#"], {"*": ArgumentType.Variadic}, lambda x: ArgumentType.Required, parse_args=False)


setupFunctions()
