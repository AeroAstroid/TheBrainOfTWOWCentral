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

# functions: Dict[str, Function] = {}
Infinite = math.inf


def setupFunctions():
    Function(["abs"], {"number": None}, abs_func)
    Function(["add", "sum"], {"number": None, "bys": Infinite}, add)
    Function(["ceil"], {"number": None}, ceil)
    Function(["div", "divide"], {"dividend": None, "divisors": Infinite}, div)
    Function(["floor"], {"number": None}, floor)
    Function(["math"], {"number": None, "operator": None, "by": None}, math_func)
    Function(["mod"], {"number": None, "bys": Infinite}, mod)
    Function(["mul", "multiply", "product"], {"number": None, "bys": Infinite}, mul)
    Function(["pow"], {"number": None, "bys": Infinite}, pow_func)
    Function(["sub", "subtract", "difference"], {"number": None, "bys": Infinite}, sub)

    Function(["args"], {"index": ""}, args)
    Function(["array"], {"arr": Infinite}, array)
    Function(["choose"], {"arr": Infinite}, choose)
    Function(["choosechar"], {"string": None}, choosechar)
    Function(["compare"], {"v1": None, "operator": None, "v2": None}, compare)
    Function(["concat"], {"items": Infinite}, concat)
    Function(["define"], {"name": None, "item": None}, define)

    Function(["find", "indexof"], {"list": None, "value": None}, find)
    Function(["func", "function"], {"name": None, "args": None, "body": None}, func, parse_args=False)
    Function(["return", "ret"], {"result": None}, return_func)
    Function(["global"], {"use": None, "name": None, "value": 0}, global_func)
    Function(["if"], {"compare": None, "true": None, "false": None}, if_func, parse_args=False)
    Function(["index"], {"arr": None, "index": None}, index)
    Function(["setindex"], {"arr": None, "index": None, "value": None}, setindex)
    Function(["import"], {"name": None}, import_func)

    Function(["length"], {"arr": None}, length)
    Function(["loop"], {"amount": None, "body": None}, loop, parse_args=False)

    Function(["j"], {"amount": 1}, j)
    Function(["join"], {"array": None, "joiner": ""}, join)
    Function(["joinall"], {"array": None}, joinall)

    Function(["randint"], {"minimum": None, "maximum": None}, randint)
    Function(["random"], {"minimum": 0, "maximum": 1}, random_func)
    Function(["repeat"], {"item": None, "amount": None}, repeat)
    Function(["round"], {"number": None}, round_func)
    Function(["replace"], {"string": None, "match": None, "replace": None}, replace_func)
    Function(["slice"], {"array": None, "index_start": None, "index_end": None}, slice_func)
    Function(["split"], {"string": None, "seperator": " "}, split)

    Function(["time"], {}, time_func)
    Function(["try"], {"attempt": None, "on_error": None}, try_func, parse_args=False)
    Function(["user"], {"userItemToGet": None}, user_func)
    Function(["username"], {}, username)
    Function(["userid"], {}, userid)
    Function(["var"], {"item": None, "index": ""}, var)
    Function(["while"], {"condition": None, "body": None}, while_func, parse_args=False)
    Function(["block"], {"body": Infinite}, block, parse_args=False)
    Function(["#"], {"comments": Infinite}, comment)

    Function(["str"], {"item": None}, str)
    Function(["int"], {"item": None}, int)
    Function(["float"], {"item": None}, float)
    # Function(["#"], {"*": Infinite}, lambda x: None)


setupFunctions()
