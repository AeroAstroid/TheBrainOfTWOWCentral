from traceback import format_exc

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
            github_devs = ["Inferno", "Digin", "LegitSi", "Zelo101", "weee50"] # dev only, delete this line of code in production release, also update as needed (will unhardcode this later hopefully)
            unfunnyerrmsg = ["GOD FUCKING DAMMIT! **crashing noises**", "Whoops. You broke it.",
                "Perhaps some caffeinated beverages will provide some comic relief, hmm?",
                "..Shit.", "A fatal exception has occurred at memory address x0AAAAAAAH!", "Uh oh!",
                "Your bot ran into a problem and needs to be fixed. We're just collecting some error info, but we can't fix it for you.",
                "Have you tried turning it off and back on again?", "That's some pretty crappy reception if you ask me.",
                "Try smashing it, that will work!", "Bad bot!", "A fresh mind is exactly what you need to solve a problem!",
                "Are you *sure* it wasn't just a typo?", "I'm pretty sure it's just a typo.",
                "THREAD: 4 (BROKEN BOT EXCEPTION)", "Why not take a break? You can pause your session by leaving the room.",
                "0000000F\n00000003", "Your bot's code appears to be abnormal!", "I'm so sorry for all this.", ":(", "Me sad.",
                "404: Good code not found.", "I've had enough of this shit!",
                "An unexpected error occurred and the bot needs to quit. We're sorry!", "Bot cannot startup. Error code = 0x1."
                "I ran out of error messages to show! Suggest me some new ones!", "Why aren't you working properly?!",
                "***AAAAAAAAA!!!***", "I don't wanna play this game anymore!",
                "Guess it was a bad day to code.", "I for one welcome our new robot overlorrrrrrrrrrrrrrr-",
                "May contain trace amounts of salt!", "Scream louder, I think it can hear you!",
                "Disconnected?! Will attempt to reconnect...", f"Have you considered asking {random.choice(github_devs)}?",
                f"{random.choice(github_devs)} is to blame!"] # dev only, delete this line of code in production release
            errmsg = f"ERROR at `{statement}`:\n{e}"
            print(f"{errmsg}\n\n{format_exc()}") # print stack trace too
            message = f"{unfunnyerrmsg}\n\n{errmsg}" # dev only, delete this line of code in production release
            return message # dev only, use "return errmsg" in production release

    # print(codebase.variables)
    # print(codebase.output)
    if len(codebase.output) > 2000:
        return "ERROR: Output too long!"
    return codebase.output
