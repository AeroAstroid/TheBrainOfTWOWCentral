from lark import Tree
from Commands.bstar.interpreter.expression import Expression
import Commands.bstar.interpreter.globals as globals
from Commands.bstar.interpreter.userfunction import UserFunction


def func(name, args: Tree, body):
    parsed_name = Expression(name, globals.codebase)
    parsed_args = list(map(lambda x: Expression(x, globals.codebase), args.children[1:]))

    UserFunction(parsed_name, parsed_args, body, True)
