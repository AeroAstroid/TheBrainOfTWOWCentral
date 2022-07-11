import src.interpreter.globals as globals

class PMSentError(Exception):
    pass

def pm(string):
    if globals.codebase.pmmade == False:
        globals.codebase.pmmade = True
        globals.codebase.pmoutput = string
    else:
        globals.codebase.pmoutput += string