from src.interpreter.function_deco import setupFunctions
from src.interpreter.parsing import runCode

empty = ""
setupFunctions()
print("------------------------\n\n")

while True:
    print("enter your b* code:\n")

    code = "\n".join(iter(input, empty))
    result = runCode(code)
    print("Result below:\n\n", result, "\n", sep="")

