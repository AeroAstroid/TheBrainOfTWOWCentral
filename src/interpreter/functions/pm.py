import src.interpreter.globals as globals

class PMSentError(Exception):
    pass

def pm(string):
    if globals.codebase.pmsent == False:
        globals.user.send(string)
    else:
        raise PMSentError("You already sent a PM to the user!")