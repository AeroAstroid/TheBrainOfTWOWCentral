from typing import List, Dict, Union

import discord

from Config.b_star_interpreter.userfunction import UserFunction

class OutputClass:
    def __init__(self, text, realtime):
        self.text = ""
        self.realtime = realtime
    def __repr__(self):
        return self.text
    def __str__(self):
        return self.text
    def __setattr__(self, __name: str, __value: str):
        self.text = __value
    def __add__(self, other):
        self.text += other

class Codebase:
    def __init__(self, lines, user, arguments, author):
        self.lines: List[str] = lines
        self.variables: List[Dict[str, str]] = [{}]
        self.functions: Dict[str, UserFunction] = {}
        self.user: Union[discord.User, None] = user
        self.arguments: Union[List[str], None] = arguments
        self.output: OutputClass(False) = ""
        self.author: int = author if author != "" else -1

        # TODO: This is temporary while s3.py gets revamped in 1.1
        self.global_limit: int = 0
        self.ret = None


