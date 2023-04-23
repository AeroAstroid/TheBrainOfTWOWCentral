# used for exceptions so it's going here
def safe_cut(s):
	return str(s)[:15] + ("..." if len(str(s)) > 15 else "")

class BStarProgramRaisedException(Exception):
  pass

class BStarTypeCoercionFailureException(Exception):
  pass

class BStarUndefinedVariableException(Exception):
  pass

