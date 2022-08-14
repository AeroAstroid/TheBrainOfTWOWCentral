class BStarProgramDefinedException(Exception):
  pass


def raise_func(msg):
  raise BStarProgramDefinedException(msg)