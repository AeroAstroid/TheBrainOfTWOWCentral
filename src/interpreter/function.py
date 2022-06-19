import math
from typing import Dict, Any, Union, Callable, List

from src.interpreter.expression import Expression
from src.interpreter.tempFunctionsFile import functions
from src.interpreter.run import Codebase
from src.interpreter.globals import debug


# Returns true if the value is not "None" or "Infinite"
def isUniqueValue(value: Any):
    return False if value is (None or math.inf) else True


class Function:
    def __init__(self, aliases: List[str], args: Dict[str, Union[None, Union[int, float, str]]], runner: Callable, parse_args: bool = True):
        self.aliases = aliases
        self.args = args
        self.infiniteArgs = False
        self.argumentsRequired = self.__getArgumentsRequired()
        self.runner = runner
        self.parse_args = parse_args

        for alias in aliases:
            if debug.print_debug:
                print([alias.upper(), alias.lower()], self)
            functions[alias.upper()] = self
            functions[alias.lower()] = self

    def run(self, codebase: Codebase, args: List[Any], alias_used: str):
        if self.parse_args:
            parsedArgs = list(map(lambda arg: Expression(arg, codebase), args))
        else:
            parsedArgs = args

        parsedArgsLength = len(parsedArgs)

        # TODO: Make it so that it doesnt change the original list (parsedArgs)
        self.__fillArgs(parsedArgs)

        if parsedArgsLength < self.argumentsRequired:
            raise Exception(
                f"Not enough arguments for function **{alias_used.upper()}** (expected {len(self.args)}, got {len(parsedArgs)})")

        if parsedArgsLength > len(self.args) and (self.infiniteArgs is False):
            raise Exception(
                f"Too many arguments for function **{alias_used.upper()}** (expected {len(self.args)}, got {len(parsedArgs)})")

        return self.runner(*parsedArgs)

    def __getArgumentsRequired(self):
        result = 0
        for arg in self.args.values():
            if arg is None:
                result += 1
            elif arg is math.inf:
                self.infiniteArgs = True
                result += 1

        return result

    # Fills in optional default values if they are not provided
    def __fillArgs(self, arr: List[str]):
        for i, value in enumerate(self.args.values()):
            if isUniqueValue(value) and len(arr[i:i + 1]) == 0:
                arr.append(value)
        return arr