from lark import Tree
from src.interpreter.expression import Expression
import src.interpreter.globals as globals
from src.interpreter.userfunction import UserFunction


def func(name, args: Tree, body):
    parsed_name = Expression(name, globals.codebase)
    parsed_args = list(map(lambda x: Expression(x, globals.codebase), args.children[1:]))

    UserFunction(parsed_name, parsed_args, body, True)
