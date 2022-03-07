# from typing import Dict
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
from src.interpreter.functions.index import index
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
from src.interpreter.functions.userid import userid
from src.interpreter.functions.username import username
from src.interpreter.functions.var import var

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


def setupFunctionsNew():
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

    Function(["args"], {"index": None}, args)
    Function(["array"], {"arr": Infinite}, array)
    Function(["choose"], {"arr": Infinite}, choose)
    Function(["choosechar"], {"string": None}, choosechar)
    Function(["compare"], {"v1": None, "operator": None, "v2": None}, compare)
    Function(["define"], {"name": None, "item": None}, define)

    Function(["find"], {"v1": None, "v2": None, "v3": None, "v4": None}, find)
    Function(["func", "function"], {"name": None, "args": None, "code": Infinite}, func)

    Function(["j"], {"amount": 1}, j)

    Function(["var"], {"item": None}, var)
    Function(["#"], {"comments": Infinite}, comment)
    # Function(["#"], {"*": Infinite}, lambda x: None)


setupFunctionsNew()


def setupFunctions():
    # addFunction("args", args)
    # addFunction("array", array)
    # addFunction("choose", choose)
    # addFunction("choosechar", choosechar)
    # addFunction("compare", compare)
    addFunction("concat", concat)
    # addFunction("define", define)

    # addFunction("find", find)
    addFunction("func", func)
    addFunction("function", func)
    addFunction("global", global_func)
    addFunction("if", if_func)
    addFunction("index", index)
    addFunction("join", join)
    addFunction("joinall", joinall)
    addFunction("length", length)
    addFunction("loop", loop)
    # addFunction("map", map_func)
    # addFunction("math", math_func)

    addFunction("randint", randint)
    addFunction("random", random_func)
    addFunction("repeat", repeat)
    addFunction("round", round_func)
    addFunction("replace", replace_func)

    addFunction("slice", slice_func)
    addFunction("split", split)

    addFunction("time", time_func)
    addFunction("try", try_func)
    addFunction("username", username)
    addFunction("userid", userid)
    # addFunction("var", var)
    # addFunction("#", comment)


def addFunction(name: str, func):
    print(f"{name} > Deprecated: Use Function Class instead")
