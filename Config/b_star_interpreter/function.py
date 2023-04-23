import inspect
import math

import bstarparser

import bstarparser

from Config.b_star_interpreter.expression import Expression
from Config.b_star_interpreter.tempFunctionsFile import functions
from Config.b_star_interpreter.run import Codebase
from Config.b_star_interpreter.globals import debug


# Returns true if the value is not "None" or "Infinite"
def isUniqueValue(value: any):
    return False if value is (None or math.inf) else True


def coerceArgument(parameter_type: str, argument: any):
    match parameter_type:
        case int.__name__:
            argument.val_type = bstarparser.Type.INTEGER
        case float.__name__:
            argument.val_type = bstarparser.Type.FLOAT
        # case function.__class__:
        #     arg.val_type = bstarparser.Type.FUNCTION
        case str.__name__:
            argument.val_type = bstarparser.Type.STRING
        case _:
            # argument.val_type = bstarparser.Type.FUNCTION
            pass

    return argument


def coerceTupleArgument(parameter: inspect.Parameter, arguments: tuple[any]):
    # tuple[T] -> T
    for argument in arguments:
        # TODO: only works for Tuple[T] so far, not Tuple[T | K]
        parameterType = str(parameter.annotation).split("[")[1][:-1]
        coerceArgument(parameterType, argument)

    return arguments


class Function:
    def __init__(self, aliases: list[str], args: dict[str, int | float | str | None], runner: callable,
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

    def run(self, codebase: Codebase, block, args: list[any], alias_used: str):
        #
        # TODO: Make this optional with strict mode
        # This is type coercion, mandatory for now.
        # get all parameters from the function

        # This will Expression() all arguments if the function wants it.
        if self.parse_args:
            parameters = list(inspect.signature(self.runner).parameters.values())

            # iterate through all arguments given, coerce them to the type the function wants
            parsedArgs = []
            for i, parameter in enumerate(parameters):
                if parameter.kind == inspect.Parameter.VAR_POSITIONAL:
                    parsedArgs.extend(coerceTupleArgument(parameter, args[i:]))
                else:
                    parsedArgs.append(coerceArgument(parameter.annotation.__name__, args[i]))

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
    def __fillArgs(self, arr: list[str]):
        for i, value in enumerate(self.args.values()):
            if isUniqueValue(value) and len(arr[i:i + 1]) == 0:
                arr.append(value)
        return arr