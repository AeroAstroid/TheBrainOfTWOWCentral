# used for exceptions so it's going here
def safe_cut(s):
	return str(s)[:15] + ("..." if len(str(s)) > 15 else "")

class BStarException(Exception):
  pass

class BStarProgramRaisedException(BStarException):
  pass

class BStarTypeCoercionFailureException(BStarException):
  pass

class BStarUndefinedVariableException(BStarException):
  pass

