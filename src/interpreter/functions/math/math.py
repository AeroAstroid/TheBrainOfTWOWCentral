from src.interpreter.functions.math.add import add
from src.interpreter.functions.math.div import div
from src.interpreter.functions.math.mod import mod
from src.interpreter.functions.math.mul import mul
from src.interpreter.functions.math.pow import pow_func
from src.interpreter.functions.math.sub import sub


def math_func(number, operator, by):
    if operator == "+":
        return add(number, by)
    elif operator == "-":
        return sub(number, by)
    elif operator == "/":
        return div(number, by)
    elif operator == "*":
        return mul(number, by)
    elif operator == "^":
        return pow_func(number, by)
    elif operator == "%":
        return mod(number, by)
