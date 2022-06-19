from src.interpreter.expression import Expression
import src.interpreter.globals as globals
from src.interpreter.userfunction import UserFunction


def func(name, args, body):
    parsedName = Expression(name, globals.codebase)
    parsedArgs = list(map(lambda x: Expression(x, globals.codebase), args.children))
    parsed_args = {}

    for i, argument in enumerate(parsedArgs[1:]):
        parsed_args[i] = argument

    UserFunction(parsedName, parsedArgs, body, True)
