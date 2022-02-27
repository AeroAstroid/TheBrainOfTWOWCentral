from typing import Dict, Any, Union, Callable, List

from src.interpreter.expression import Expression
from src.interpreter.tempFunctionsFile import functions
from src.interpreter.run import Codebase


class Function:
    def __init__(self, name: str, args: Dict[str, Union[None, Union[int, float, str]]], runner: Callable):
        self.name = name
        self.args = args
        self.runner = runner

        print([name.upper(), name.lower()], self)
        functions[self.name.upper()] = self
        functions[self.name.lower()] = self

    def run(self, codebase: Codebase, args: List[Any]):
        parsedArgs = list(map(lambda arg: Expression(arg, codebase), args))
        return self.runner(*parsedArgs)
