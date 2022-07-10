import src.interpreter.globals as globals

class PMSentError(Exception):
    pass

async def pm(string):
    if globals.codebase.pmsent == False:
        await globals.codebase.user.send(string)
    else:
        raise PMSentError("You already sent a PM to the user!")