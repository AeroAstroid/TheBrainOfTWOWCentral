import src.interpreter.globals as globals
from src.interpreter.expression import Expression

def type_func(a): # i unno what to name the var
	return type(Expression(a, globals.codebase)).__name__