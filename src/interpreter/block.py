class Block:
    def __init__(self, line: str, depth):

        # Function name
        self.function = line.split(" ", 1)[0][1:]

        # The child blocks / Arguments
        self.children = []

        # The code line itself
        self.line = line

        # Depth of block in tree
        self.depth = 0

        # TODO: Make this less complicated
        # This variable is terrible so i'll show you what it does
        # Lets use this example:
        # "[IF [COMPARE 2 = 2] [VAR a] [VAR b]]"
        #
        # It basically gets rid of the parent block, and returns the child blocks in a list:
        # ["[COMPARE 2 = 2]", "[VAR a]", "[VAR b]"]
        if line != "":
            child_blocks = "".join(self.line.split(" ", 1)[1:]).split(" [")
            for i, child in enumerate(child_blocks):
                if i == len(child_blocks) - 1:
                    # Last child, Remove bracket
                    child = child[:-1]
                    self.children.append(Block(child, self.depth + 1))
                else:
                    self.children.append(Block(child, self.depth + 1))

    def debug_print_children(self):
        return "".join(map(lambda child: child.line + " ", self.children))
