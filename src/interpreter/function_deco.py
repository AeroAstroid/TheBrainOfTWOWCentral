# from src.interpreter.functions.func import func
from src.interpreter.functions.args import args
from src.interpreter.functions.array import array
from src.interpreter.functions.choose import choose
from src.interpreter.functions.choosechar import choosechar
from src.interpreter.functions.comment import comment
from src.interpreter.functions.compare import compare
from src.interpreter.functions.concat import concat
from src.interpreter.functions.define import define
from src.interpreter.functions.global_define import global_define
from src.interpreter.functions.global_var import global_var
from src.interpreter.functions.if_func import if_func
from src.interpreter.functions.index import index
from src.interpreter.functions.j import j
from src.interpreter.functions.join import join
from src.interpreter.functions.loop import loop
from src.interpreter.functions.map import map_func
from src.interpreter.functions.randint import randint
from src.interpreter.functions.random_func import random_func
from src.interpreter.functions.repeat import repeat
from src.interpreter.functions.round import round_func
from src.interpreter.functions.time import time
from src.interpreter.functions.var import var

from src.interpreter.functions.math.abs import abs_func
from src.interpreter.functions.math.add import add
from src.interpreter.functions.math.ceil import ceil
from src.interpreter.functions.math.div import div
from src.interpreter.functions.math.floor import floor
from src.interpreter.functions.math.math import math
from src.interpreter.functions.math.mod import mod
from src.interpreter.functions.math.mul import mul
from src.interpreter.functions.math.pow import pow_func
from src.interpreter.functions.math.sub import sub

functions = {}


def setupFunctions():
    addFunction("abs", abs_func)
    addFunction("add", add)
    addFunction("args", args)
    addFunction("array", array)
    addFunction("ceil", ceil)
    addFunction("choose", choose)
    addFunction("choosechar", choosechar)
    addFunction("compare", compare)
    addFunction("concat", concat)
    addFunction("define", define)
    addFunction("div", div)
    addFunction("floor", floor)
    addFunction("global define", global_define)
    addFunction("global var", global_var)
    addFunction("if", if_func)
    addFunction("index", index)
    addFunction("j", j)
    addFunction("join", join)
    addFunction("loop", loop)
    addFunction("map", map_func)
    addFunction("math", math)
    addFunction("mod", mod)
    addFunction("mul", mul)
    addFunction("pow", pow_func)
    addFunction("randint", randint)
    addFunction("random", random_func)
    addFunction("repeat", repeat)
    addFunction("round", round_func)
    addFunction("sub", sub)
    addFunction("time", time)
    addFunction("var", var)
    addFunction("#", comment)


def addFunction(name: str, func):
    print(name.upper(), func)
    functions[name.upper()] = func
