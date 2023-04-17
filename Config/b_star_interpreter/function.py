import inspect
import math
from typing import Dict, Any, Union, Callable, List

import bstarparser

from Config.b_star_interpreter.expression import Expression
from Config.b_star_interpreter.tempFunctionsFile import functions
from Config.b_star_interpreter.run import Codebase
from Config.b_star_interpreter.globals import debug


# Returns true if the value is not "None" or "Infinite"
def isUniqueValue(value: Any):
    return False if value is (None or math.inf) else True


class Function:
    def __init__(self, aliases: List[str], args: Dict[str, Union[None, Union[int, float, str]]], runner: Callable,
                 parse_args: bool = True):
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

    def run(self, codebase: Codebase, block, args: List[Any], alias_used: str):
        #
        # TODO: Make this optional with strict mode
        # This is type coercion, mandatory for now.
        # get all parameters from the function
        parameters = list(inspect.signature(self.runner).parameters.values())
        parsedArgs = []

        # iterate through all arguments given
        for i, arg in enumerate(args):
            # parameters[i] would be something like int() or str()
            # raw = parameters[i].annotation(arg.raw)
            # arg.raw = raw
            match parameters[i].annotation.__name__:
                case int.__name__:
                    arg.val_type = bstarparser.Type.INTEGER
                case float.__name__:
                    arg.val_type = bstarparser.Type.FLOAT
                # case function.__class__:
                #     arg.val_type = bstarparser.Type.FUNCTION
                case str.__name__:
                    arg.val_type = bstarparser.Type.STRING
                case _:
                    arg.val_type = bstarparser.Type.FUNCTION


            parsedArgs.append(arg)

        #
        # This will Expression() all arguments if the function wants it.
        if self.parse_args:

            parsedArgs = list(map(lambda arg: Expression(arg, codebase), parsedArgs))

        else:
            parsedArgs = args

        # TODO: Remove this once arg bug is fixed in Expression
        # parsedArgs = [arg for arg in parsedArgs if arg is not None]

        parsedArgsLength = len(parsedArgs)

        # TODO: Make it so that it doesnt change the original list (parsedArgs)
        self.__fillArgs(parsedArgs)

        if parsedArgsLength < self.argumentsRequired:
            raise Exception(
                f"{alias_used.upper()} requires {len(self.args)} argument(s), but got {len(parsedArgs)}.")

        if parsedArgsLength > len(self.args) and (self.infiniteArgs is False):
            raise Exception(
                f"{alias_used.upper()} requires {len(self.args)} argument(s), but got {len(parsedArgs)}.")

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
