import src.interpreter.globals as globals

class PMSentError(Exception):
    pass

def pm(string):
    if globals.codebase.sendpm == False:
        globals.codebase.sendpm = True
        globals.codebase.pmoutput = string
    else:
        globals.codebase.pmoutput += string