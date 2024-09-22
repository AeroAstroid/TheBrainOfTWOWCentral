import random

import cexprtk
import math


def math_func(*equation_strings: str):
    equation = " ".join(map(str, equation_strings))
    st = cexprtk.Symbol_Table(variables={"e": math.e, "phi": (1 + math.sqrt(5)) / 2, "pi": math.pi}, add_constants=True,
                              functions={"rand": random.uniform})
    e = cexprtk.Expression(equation, st)
    output = e.value()
    if output % 1 == 0:
        output = int(output)
    else:
        output = round(output, 15)

    return output
