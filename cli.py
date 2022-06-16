from src.interpreter.function_deco import setupFunctions
from src.interpreter.run import runCode
from tests import Colours

empty = ""
setupFunctions()
print("------------------------")
print(Colours.OKGREEN + Colours.BOLD + "B* CLI" + Colours.ENDC)
print(Colours.OKBLUE + Colours.BOLD + "press enter for a new line, and press enter twice to run the code.\n\n" + Colours.ENDC)

while True:
    print("enter your b* code:\n")

    code = "\n".join(iter(input, empty))
    result = runCode(code)
    print("Result below:\n\n", result, "\n", sep="")

