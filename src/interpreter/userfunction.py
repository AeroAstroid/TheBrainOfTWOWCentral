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

        # for example maybe creating a lambda that already knows where to replace the variables
        # instead iterating through the entire code block
        # (interpreting within interpreting)

        # Temporary variables for use in function (lexical scope)
        func_arg_name = self.args.values()
        globals.codebase.variables.append({})
        for i, arg in enumerate(func_arg_name):
            # TODO: This is outdated
            Expression(["DEFINE", arg, run_args[i]], globals.codebase)

        result = Expression(self.block, globals.codebase)
        globals.codebase.variables.pop()

        # Early return
        if globals.codebase.ret is not None:
            ret = globals.codebase.ret
            globals.codebase.ret = None
            return ret

        return result
