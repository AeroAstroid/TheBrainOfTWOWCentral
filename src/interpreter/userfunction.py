from typing import List, Dict

import src.interpreter.globals as globals
from src.interpreter.expression import Expression


class UserFunction:
    def __init__(self, name: str, args: Dict[int, str], block: List[str], global_func: bool):
        self.args = args
        self.block = block

        globals.codebase.functions[name] = self

        # if global_func is True:

    def run(self, run_args: List[str]):
        # print(f"{run_args} > {self.args} > {self.block} > {self.block[0]} > {self.block[0][0]}")

        # TODO: There is definitely a faster way to do this (3 nested for loops is terrible)
        # TODO: Use numpy for arrays and stuff
        # for example maybe creating a lambda that already knows where to replace the variables
        # instead iterating through the entire code block
        # (interpreting within interpreting)

        # Temporary variables for use in function (lexical scope)
        func_arg_name = self.args.values()
        for i, arg in enumerate(func_arg_name):
            Expression(["DEFINE", arg, run_args[i]], globals.codebase)

        result = Expression(self.block, globals.codebase)

        # for arg in func_arg_name:
        #     Expression(["DEFINE", arg, 0], globals.codebase)

        return result
