from typing import List


def find(block: List, codebase):
    try:
        if len(block) == 3:
            return Expression(block[1], codebase).index(Expression(block[2], codebase))
        elif len(block) == 4:
            return Expression(block[1], codebase).index(
                Expression(block[2], codebase), Expression(block[3], codebase))
        else:
            return Expression(block[1], codebase).index(
                Expression(block[2], codebase), Expression(block[3], codebase),
                Expression(block[4], codebase))
    except ValueError:
        return -1
