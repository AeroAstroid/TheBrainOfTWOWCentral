# imports
from src.interpreter.block import Block # import block structure
import random # used in random and maybe randint?

# expression defining
def Expression(block: Block, codebase):
    if block.function == "DEFINE":
        print("DEFINE", block.debug_print_children())
        codebase.variables[block.children[0].line] = block.children[1].line
    elif block.function == "VAR":
        print("VAR", block.debug_print_children())
        return codebase.variables[block.children[0].line]
    elif block.function == "MATH":
        return None
    elif block.function == "COMPARE":
        return None
    elif block.function == "IF":
        return None
    elif block.function == "ARRAY":
        return None
    elif block.function == "CHOOSE":
        return None
    elif block.function == "CHOOSECHAR":
        return None
    elif block.function == "REPEAT":
        return None
    elif block.function == "CONCAT":
        # UNFINISHED
        print("CONCAT", block.children[0].line, block.children[1].line)
        buffer = ""
        for i in block.children:
            print("CONCAT_i", i.line)
            buffer += Expression(i, codebase)
        return buffer
    elif block.function == "RANDINT":
        return None
    elif block.function == "RANDOM":
        return random.uniform(block.children[0].line, block.children[1].line) #should probably test this
    elif block.function == "FLOOR":
        return None
    elif block.function == "CEIL":
        return None
    elif block.function == "ROUND":
        return None
    elif block.function == "INDEX":
        return None
    elif block.function == "ABS":
        return None
    elif block.function == "ARGS":
        return None
    elif block.function == "GLOBAL" and block[1] == "DEFINE":
        return None
    elif block.function == "GLOBAL" and block[1] == "VAR":
        return None
    elif block.function == "#":
        return None # this is comments
    elif block.function == "MOD":
        return None
    else:
        return block.function
