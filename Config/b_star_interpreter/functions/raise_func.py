from Config.b_star_interpreter.exceptions import BStarProgramRaisedException


def raise_func(msg):
  raise BStarProgramRaisedException(msg)