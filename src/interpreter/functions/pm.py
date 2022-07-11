import src.interpreter.globals as globals

class PMSentError(Exception):
    pass

def pm(string):
    if globals.codebase.pmmade == False:
        globals.codebase.pmmade = True
        globals.codebase.pmstring = string
    else:
        globals.codebase.pmstring += string