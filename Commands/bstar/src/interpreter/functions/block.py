import Commands.bstar.src.interpreter.globals as globals
from Commands.bstar.src.interpreter.expression import Expression

def block(*functions):
  ret = None
  for fn in functions:
    if ret is not None: # print everything that isnt returned
      globals.codebase.output += str(ret)
      
    ret = Expression(fn, globals.codebase)
    if globals.codebase.ret is not None:
      break
  return ret