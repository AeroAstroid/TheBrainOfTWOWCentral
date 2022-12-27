import Commands.b_star.interpreter.globals as globals
from Commands.b_star.interpreter.expression import Expression

def type_func(a): # i unno what to name the var
	return type(Expression(a, globals.codebase)).__name__