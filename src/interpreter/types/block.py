# from typing import List, Union
#
# from src.interpreter.types.literal import Literal
# from src.interpreter.types.numeric import Numeric
#
#
# class Block:
#     def __init__(self, line: str, depth):
#         # Function name
#         self.function = line.split(" ", 1)[0][1:]
#
#         # The child blocks / Arguments
#         self.children: List[Union[Block, Literal, Numeric]] = []
#
#         # The code line itself
#         self.line = line
#
#         # Depth of block in tree
#         self.depth = 0
#
#         # Create tree
#         if self.line != "":
#             # child_blocks = "".join(self.line.split(" ", 1)[1:]).split(" ")
#             child_blocks = self.line.split(" ")
#
#             print("cb|", child_blocks)
#             # for i, child in enumerate(child_blocks):
#             #     if isBlock(child):
#             #         # If opening bracket
#             #         # If closing bracket
#             #     if isLiteral(child):
#             #         # If opening bracket
#             #         # If closing bracket
#             #     if isNumber(child):
#             # self.children.append(Number())
#
#     def debug_print_children(self):
#         return "".join(map(lambda child: child.line + " ", self.children))
