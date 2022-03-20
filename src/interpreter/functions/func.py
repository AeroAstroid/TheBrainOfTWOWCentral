from src.interpreter.userfunction import UserFunction


def func(name, args, code):
    parsed_args = {}

    for i, argument in enumerate(args[1:]):
        parsed_args[i] = argument

    UserFunction(name, parsed_args, code, True)
