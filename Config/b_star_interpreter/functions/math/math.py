from Config.b_star_interpreter.functions.math.add import add
from Config.b_star_interpreter.functions.math.div import div
from Config.b_star_interpreter.functions.math.mod import mod
from Config.b_star_interpreter.functions.math.mul import mul
from Config.b_star_interpreter.functions.math.pow import pow_func
from Config.b_star_interpreter.functions.math.sub import sub


def math_func(number, operator: str, by):
    operator = operator.strip()
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
    else:
        raise Exception("unknown operator: " + operator)
