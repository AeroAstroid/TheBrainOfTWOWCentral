from src.interpreter.function_deco import setupFunctions
from src.interpreter.globals import debug
from src.interpreter.run import runCodeSandbox
from tests import Colours

empty = ""
debug.print_debug = False
setupFunctions()
print("------------------------")
print(Colours.OKGREEN + Colours.BOLD + "B* CLI" + Colours.ENDC)
print(Colours.OKBLUE + Colours.BOLD + "press enter for a new line, and press enter twice to run the code.\n\n" + Colours.ENDC)

while True:
    print(Colours.BOLD + "enter your b* code:\n" + Colours.ENDC)

    code = "\n".join(iter(input, empty))
    result = runCodeSandbox(code)
    print("Result below:\n\n", result, "\n", sep="")
