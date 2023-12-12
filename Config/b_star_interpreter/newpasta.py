from __future__ import annotations


class Value:
    value: int | float | str
    length: int

    def __init__(self, value):
        self.value = value
        self.length = len(str(value))


class Token:
    class INTEGER(Value):
        pass

    class FLOAT(Value):
        pass

    class SYMBOL(Value):
        pass

    class QUOTE:
        pass

    class LBRACKET:
        pass

    class RBRACKET:
        pass

    class NEWLINE:
        pass


class Node:
    file_start: int
    file_end: int
    file_line: int
    depth: int
    root: bool
    type: Token | None
    parent: "Node" | None
    children: list["Node"]

    def __init__(self, type, file_start, file_end, file_int, depth, parent):
        self.file_start = file_start
        self.file_end = file_end
        self.file_line = file_int
        self.depth = depth
        self.parent = parent
        self.root = parent is None
        self.type = type
        self.children = []

    def add_child(self, child: "Node"):
        self.children.append(child)


def computeDepth(root: Node):
    end_file_line = 0
    for child in root.children:
        child.parent = root
        child.depth = root.depth + 1
        try:
            end_file_line += child.type.length
        except AttributeError:
            pass

        computeDepth(child)

    root.file_end = end_file_line


def lexer(code: str):
    transformed_code = (
        code
        .replace("[", " [ ")
        .replace("]", " ] ")
        .replace("\"", " \" ")
        .replace("\n", " \n ")
    )

    words = transformed_code.split()
    tokens = []

    # Special quote mode to allow symbols with spaces & brackets
    quote_mode = False

    # Used to check if brackets are missing
    depth = 0

    # Used for error messages & node properties later on
    line = 1

    for word in words:
        if quote_mode:
            match word:
                case "\"":
                    quote_mode = False
                case _:
                    tokens.append(Token.SYMBOL(word))
        else:
            match word:
                case "[":
                    depth += 1
                    tokens.append(Token.LBRACKET())
                case "]":
                    depth -= 1
                    tokens.append(Token.RBRACKET())
                case "\"":
                    quote_mode = True
                case "\n":
                    line += 1
                    tokens.append(Token.NEWLINE())
                case _:
                    try:
                        int(word)
                        tokens.append(Token.INTEGER(int(word)))
                    except ValueError:
                        if word.isnumeric():
                            tokens.append(Token.FLOAT(float(word)))
                        else:
                            tokens.append(Token.SYMBOL(word))

        if depth < 0:
            raise Exception("Your missing a bracket, error occured at line", line)

    if quote_mode:
        raise Exception("Missing quotes!")

    return tokens


def generate(tokens, root) -> Node:
    i = 0
    while len(tokens):
        token = tokens.pop(0)
        node = None
        match token.__class__:
            case Token.FLOAT | Token.INTEGER | Token.SYMBOL:
                # if not quote_mode:
                node = Node(token, root.file_start + i, root.file_start + i + token.length, root.file_line, 0, root)
            case Token.NEWLINE:
                root.file_line += 1
            # case Token.QUOTE:
            #     quote_mode = not quote_mode
            case Token.LBRACKET:
                node = generate(tokens, Node(None, 0, 0, root.file_line, 0, None))
            case Token.RBRACKET:
                break
            case _:
                raise Exception("Unknown token!", token)

        if node is not None:
            root.add_child(node)
        i += 1

    return root


def parser(code: str) -> Node:
    tokens = lexer(code)
    start = Node(None, 0, len(code), 1, 0, None)
    root = generate(tokens, start)
    computeDepth(root)
    return root


if __name__ == '__main__':
    while True:
        file = input("Input code:\n")
        structure = parser(file)
        print(structure)