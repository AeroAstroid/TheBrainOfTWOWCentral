# [DEFINE hello "Hello,_"]
# [DEFINE world "World!"]
# [CONCAT [VAR hello] [VAR world]]

# [DEFINE hello Hello,]
# [DEFINE world World!]
# [CONCAT hello world]
from src.interpreter.block import Block
from src.interpreter.expression import Expression


class Codebase:
    def __init__(self, lines):
        self.lines = lines
        self.variables = {}
        self.output = ""


def parseCode(code: str):
    lines = code.split("\n")
    codebase = Codebase(lines)

    for i in range(len(codebase.lines)):
        line = codebase.lines[i]
        if isBlock(line):
            block = Block(line, 0)
            result = Expression(block, codebase)
            if result is not None:
                codebase.output += result

    print(codebase.variables)
    print(codebase.output)
    return codebase.output


def isBlock(code: str):
    return code[0] == "[" and code[-1] == "]"
