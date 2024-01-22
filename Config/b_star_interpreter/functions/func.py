from lark import Tree
from Config.b_star_interpreter.expression import Expression
import Config.b_star_interpreter.globals as globals
from Config.b_star_interpreter.userfunction import UserFunction


def func(name: Tree, args: Tree, body: list[str]):
    parsed_name = Expression(name, globals.codebase)
    parsed_args = list(map(lambda x: Expression(x, globals.codebase), args.children[1:]))

    UserFunction(parsed_name, parsed_args, body, True)
