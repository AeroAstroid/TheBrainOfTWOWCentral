from traceback import format_exc
from random import choice

from typing import List, Union, Dict

import discord

from src.interpreter.expression import Expression


# the discord user property is used for global ownership checking
from src.interpreter.function_deco import functions
from src.interpreter.parse import parseCode
from src.interpreter.userfunction import UserFunction


class Codebase:
    def __init__(self, lines, user):
        self.lines: List[str] = lines
        self.variables: Dict[str, str] = {}
        self.functions: Dict[str, UserFunction] = {}
        self.user: Union[discord.User, None] = user
        self.output: str = ""


def runCode(code: str, user: Union[discord.User, None] = None):
    # TODO: Trim up to three backticks from beginning and end of code
    parsed_code = parseCode(code)
    codebase = Codebase(parsed_code, user)
    codebase.functions = codebase.functions | functions

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
            # why though? it's funny -inferno 11/28/21
            github_devs = ["Inferno", "Digin", "LegitSi", "Zelo101", "weee50",
                           "woooowoooo", "BowlingPizzaBall"]  # only counts people that have made a commit
            github_devs_uppercase = ["INFERNO", "DIGIN", "LEGITSI", "ZELO101", "WEEE50",
                           "WOOOOWOOOO", "BOWLINGPIZZABALL"]  # yes this was made for only 1 error message
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
                f"{choice(github_devs)} sabotaged the code!",
                "I have a good feeling your code is about as buggy as Windows ME.",
                "Ok, so if you want to fix this, all you need to do is",
                "take this L",
                "Do you notice your code is not working? If so, good! Please proceed to the keyboard smashing station ahead of you.",
                f"YOU CAUSED THIS, {choice(github_devs_uppercase)}!!",
                "Better not make that code worse...",
                "(insert message here)",
                "that code be looking like the battle pass",
                "If you're wondering why this \"unfunny\" error message is sooooo long, keep wondering. Yep, that's what I want you to do. You will never know why I randomly decided to make this error message this long, so keep wondering, and i'm out. See ya!",
                "I think the code gave the interpreter a heart attack.",
                "The unfunny happened.",
                "The calm before the storm... but the storm already happened.",
                "print(\"Code broke how sad...\")",
                "You're a surgeon now, dissect the code!",
                "Either the code broke or THE code broke.",
                "Print out your code. Then throw it in the fire."
            ]
            # errmsg = f"ERROR at `{statement}`:\n{e}"
            errmsg = f"{choice(unfunny_errmsg)}\n\nERROR at `{statement}`:\n{e}"
            print(f"{errmsg}\n\n{format_exc()}")  # print stack trace too
            return errmsg

    # print(codebase.variables)
    # print(codebase.output)
    if len(codebase.output) == 0:
        return "NOTICE: The code has successfully ran, but returned nothing!"
    if len(codebase.output) > 2000:
        return "ERROR: Output too long!"
    return codebase.output
