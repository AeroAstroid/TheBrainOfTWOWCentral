import src.interpreter.globals as globals
from src.interpreter.expression import Expression

def block(*functions):
  ret = None
  for fn in functions:
    ret = Expression(fn, globals.codebase)
  return ret