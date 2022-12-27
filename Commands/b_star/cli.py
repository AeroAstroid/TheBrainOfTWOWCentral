#!/usr/bin/env python3
# above is for shells that support shebangs
from Commands.b_star.interpreter.function_deco import setupFunctions
from Commands.b_star.interpreter.globals import debug
from Commands.b_star.interpreter.run import runCodeSandbox
from tests import Colours
import argparse, pathlib

argparser = argparse.ArgumentParser(description='Run B* code in the terminal')
exclgroup = argparser.add_mutually_exclusive_group()
exclgroup.add_argument("-n", "--interactive",dest="interactive", action="store_true", help="Enable interactive/shell mode. Use CTRL+C to exit.")
exclgroup.add_argument("-i", "--input", help="Take in an input file at INPUT.", type=pathlib.Path)
argparser.add_argument('args', nargs="*")

parsed = argparser.parse_args()
empty = ""
debug.print_debug = False
setupFunctions()

if parsed.interactive:
    while True:
        print(Colours.BOLD + "enter your b* code:\n" + Colours.ENDC)

        code = "\n".join(iter(input, empty))
        if code.startswith("file "):
            code = code.removeprefix("file ")
            with open(code) as f:
                code = f.read()
        result = runCodeSandbox(code)
        print("Result below:\n\n", result, "\n", sep="")
else:
    if parsed.input:
        with parsed.input.open() as file:
            text = file.read()
            file.close()
        result = runCodeSandbox(text, None, parsed.args)
    else:
        argparser.print_help()
        exit()
    print(result)