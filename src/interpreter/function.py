import math
from typing import Dict, Any, Union, Callable, List

from src.interpreter.expression import Expression
from src.interpreter.tempFunctionsFile import functions
from src.interpreter.run import Codebase


# Returns true if the value is not "None" or "Infinite"
def isUniqueValue(value: Any):
    return False if value is (None or math.inf) else True


class Function:
    def __init__(self, name: str, args: Dict[str, Union[None, Union[int, float, str]]], runner: Callable):
        self.name = name
        self.args = args
        self.argumentsRequired = self.__getArgumentsRequired()
        self.runner = runner

        print([name.upper(), name.lower()], self)
        functions[self.name.upper()] = self
        functions[self.name.lower()] = self

    def run(self, codebase: Codebase, args: List[Any]):
        parsedArgs = list(map(lambda arg: Expression(arg, codebase), args))
        parsedArgsLength = len(parsedArgs)

        # TODO: Make it so that it doesnt change the original list (parsedArgs)
        self.__fillArgs(parsedArgs)

        if parsedArgsLength < self.argumentsRequired:
            raise Exception(
                f"Not enough arguments for function **{self.name.upper()}** (expected {len(self.args)}, got {len(parsedArgs)})")

        if parsedArgsLength > len(self.args) != math.inf:
            raise Exception(
                f"Too many arguments for function **{self.name.upper()}** (expected {len(self.args)}, got {len(parsedArgs)})")

        return self.runner(*parsedArgs)

    def __getArgumentsRequired(self):
        result = 0
        for arg in self.args:
            if arg is None:
                result += 1
            elif arg is math.inf:
                result = math.inf
                return result

        return result

    # Fills in optional default values if they are not provided
    def __fillArgs(self, arr: List[str]):
        for i, value in enumerate(self.args.values()):
            if isUniqueValue(value) and len(arr[i:i + 1]) == 0:
                arr.append(value)
        return arr
