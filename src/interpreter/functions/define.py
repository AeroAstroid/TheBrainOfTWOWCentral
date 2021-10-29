from typing import List


def define(block: List, codebase):
    codebase.variables[block[1]] = block[2]
