from lark import Tree
from Commands.b_star.interpreter.expression import Expression
import Commands.b_star.interpreter.globals as globals
from Commands.b_star.interpreter.userfunction import UserFunction


def func(name, args: Tree, body):
    parsed_name = Expression(name, globals.codebase)
    parsed_args = list(map(lambda x: Expression(x, globals.codebase), args.children[1:]))

    UserFunction(parsed_name, parsed_args, body, True)
