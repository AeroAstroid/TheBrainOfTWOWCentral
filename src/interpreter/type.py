def isBlock(line: str):
    return line[0] == '[' or line[-1] == ']'


def isLiteral(line: str):
    return line[0] == '"' or line[-1] == '"'


def isNumber(line: str):
    return line.isnumeric()
