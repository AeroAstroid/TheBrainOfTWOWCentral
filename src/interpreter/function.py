from typing import Dict, Any, Union, Callable, List

from src.interpreter.expression import Expression
from src.interpreter.run import Codebase


class Function:
    def __init__(self, name: str, args: Dict[str, Union[None, Union[int, float, str]]], runner: Callable):
        self.name = name
        self.args = args
        self.runner = runner

    def run(self, codebase: Codebase, args: List[Any]):
        parsedArgs = map(lambda arg: Expression(arg, codebase), args)
        self.runner(*parsedArgs)
