from src.interpreter.functions.abs import abs_func
from src.interpreter.functions.args import args
from src.interpreter.functions.array import array
from src.interpreter.functions.ceil import ceil
from src.interpreter.functions.choose import choose
from src.interpreter.functions.choosechar import choosechar
from src.interpreter.functions.comment import comment
from src.interpreter.functions.compare import compare
from src.interpreter.functions.concat import concat
from src.interpreter.functions.define import define
from src.interpreter.functions.floor import floor
from src.interpreter.functions.global_define import global_define
from src.interpreter.functions.global_var import global_var
from src.interpreter.functions.if_func import if_func
from src.interpreter.functions.index import index
from src.interpreter.functions.j import j
from src.interpreter.functions.math import math
from src.interpreter.functions.mod import mod
from src.interpreter.functions.randint import randint
from src.interpreter.functions.random_func import random_func
from src.interpreter.functions.repeat import repeat
from src.interpreter.functions.round import round_func
from src.interpreter.functions.time import time
from src.interpreter.functions.var import var

functions = {}


def setupFunctions():
    addFunction("abs", abs_func)
    addFunction("args", args)
    addFunction("array", array)
    addFunction("ceil", ceil)
    addFunction("choose", choose)
    addFunction("choosechar", choosechar)
    addFunction("#", comment)
    addFunction("compare", compare)
    addFunction("concat", concat)
    addFunction("define", define)
    addFunction("floor", floor)
    addFunction("global define", global_define)
    addFunction("global var", global_var)
    addFunction("if", if_func)
    addFunction("index", index)
    addFunction("j", j)
    addFunction("math", math)
    addFunction("mod", mod)
    addFunction("randint", randint)
    addFunction("random", random_func)
    addFunction("repeat", repeat)
    addFunction("round", round_func)
    addFunction("time", time)
    addFunction("var", var)


def addFunction(name: str, func):
    print(name.upper(), func)
    functions[name.upper()] = func
