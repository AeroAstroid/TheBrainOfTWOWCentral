from traceback import format_exc
from random import choice

from src.interpreter.expression import Expression


class Codebase:
    def __init__(self, lines):
        self.lines = lines
        self.variables = {}
        self.output = ""


def parseCode(program: str):
    parseTree = []
    activityStack = [parseTree]

    newString = True
    backslashed = False
    inString = False

    # parse the program!
    for c in program:

        if newString and c not in ["[", " ", "\n"]:
            activityStack[-1].append("")
            newString = False

        if len(activityStack) == 1:
            if c == "[":
                activityStack[-1].append([])
                activityStack.append(activityStack[-1][-1])
                newString = True
            else:
                activityStack[-1][-1] += c

        elif backslashed:
            if c == "n":
                activityStack[-1][-1] += "\n"
            else:
                activityStack[-1][-1] += c
            backslashed = False

        elif inString:
            if c == "\\":
                backslashed = True
            elif c == "\"":
                inString = False
            else:
                activityStack[-1][-1] += c

        elif c == "\\":
            backslashed = True
        elif c == "\"":
            inString = True
        elif c in [" ", "\n"]:
            newString = True
        elif c == "[":
            activityStack[-1].append([])
            activityStack.append(activityStack[-1][-1])
            newString = True
        elif c == "]":
            activityStack.pop()
            if len(activityStack) == 1:
                activityStack[-1].append("")
        else:
            activityStack[-1][-1] += c

    return parseTree


def runCode(code: str):
    # TODO: Trim up to three backticks from beginning and end of code
    parsed_code = parseCode(code)
    codebase = Codebase(parsed_code)

    for statement in parsed_code:
        try:
            if type(statement) == str:
                result = statement
            else:
                result = Expression(statement, codebase)

            print(result)
            if result is not None:
                codebase.output += str(result)

        except Exception as e:
            # dev only, delete these lines in production release (error messages contributed by LegitSi)
            github_devs = ["Inferno", "Digin", "LegitSi", "Zelo101", "weee50", "woooowoooo"] # only counts people that have made a commit
            unfunny_errmsg = [
                "GOD FUCKING DAMMIT! **crashing noises**",
                "Whoops. You broke it.",
                "Perhaps some caffeinated beverages will provide some comic relief, hmm?",
                "..Shit.",
                "A fatal exception has occurred at memory address x0AAAAAAAH!",
                "Uh oh!",
                "Your bot ran into a problem and needs to be fixed. We're just collecting some error info, but we can't fix it for you.",
                "Have you tried turning it off and back on again?",
                "That's some pretty crappy reception if you ask me.",
                "Try smashing it, that will work!",
                "Bad bot!",
                "A fresh mind is exactly what you need to solve a problem!",
                "Are you *sure* it wasn't just a typo?",
                "I'm pretty sure it's just a typo.",
                "THREAD: 4 (BROKEN BOT EXCEPTION)",
                "Why not take a break? You can pause your session by leaving the room.",
                "0000000F\n00000003",
                "Your bot's code appears to be abnormal!",
                "I'm so sorry for all this.",
                ":(",
                "Me sad.",
                "404: Good code not found.",
                "I've had enough of this shit!",
                "An unexpected error occurred and the bot needs to quit. We're sorry!",
                "Bot cannot startup. Error code = 0x1.",
                "I ran out of error messages to show! Suggest me some new ones!",
                "Why aren't you working properly?!",
                "***AAAAAAAAA!!!***",
                "I don't wanna play this game anymore!",
                "Guess it was a bad day to code.",
                "I for one welcome our new robot overlorrrrrrrrrrrrrrr-",
                "May contain trace amounts of salt!",
                "Scream louder, I think it can hear you!",
                "Disconnected?! Will attempt to reconnect...",
                f"Have you considered asking {choice(github_devs)}?",
                f"{choice(github_devs)} is to blame!",
                "Aha! I found a technical issue!",
                "get rekt nerd cope skill issue",
                "You're starting to look like that Angry German Kid, calm down!",
                "Take a few deep breaths.. then SCREAM AT THE COMPUTER LOUDLY!",
                "99% done.. so close!",
                "It used to work five minutes ago!",
                "Uhh.. this is awkward..",
                "Day 527: I still haven't got the bot to work.",
                "This bot's about as unstable as the Stonk Market.",
                "[DEFINE broken \"It's broken..\"] [VAR broken]",
                "You can do it, I believe in you!",
                "I haven't seen an outage last since long since the Great ROBLOX Outage of 2021.",
                "You just started working, why are you not working again?!",
                f"{choice(github_devs)} needs to be fired for this! Or was it {choice(github_devs)} that did this? No, it was obviously {choice(github_devs)}! Wait.. no..",
                f"{choice(github_devs)} sabotaged the code!"
            ]
            # errmsg = f"ERROR at `{statement}`:\n{e}"
            errmsg = f"{choice(unfunny_errmsg)}\n\nERROR at `{statement}`:\n{e}"
            print(f"{errmsg}\n\n{format_exc()}") # print stack trace too
            return errmsg

    # print(codebase.variables)
    # print(codebase.output)
    if len(codebase.output) > 2000:
        return "ERROR: Output too long!"
    return codebase.output
