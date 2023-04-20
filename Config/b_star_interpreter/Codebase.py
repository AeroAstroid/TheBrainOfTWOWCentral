import discord

from Config.b_star_interpreter.userfunction import UserFunction


class OutputClass:
    def __init__(self, text: str, realtime):
        self.text = ""
        self.realtime = realtime

    def __repr__(self):
        return self.text

    def __str__(self):
        return self.text

    def __setattr__(self, __name: str, __value: str):
        self.text = __value

    def __add__(self, other: str):
        self.text += other


class Codebase:
    def __init__(self, lines, user, arguments, author):
        self.lines: list[str] = lines
        self.variables: list[dict[str, str]] = [{}]
        self.functions: dict[str, UserFunction] = {}
        self.user: discord.User | None = user
        self.arguments: list[str] | None = arguments
        self.output: OutputClass(False) = ""
        self.author: int = author if author != "" else -1

        # TODO: This is temporary while s3.py gets revamped in 1.1
        self.global_limit: int = 0
        self.ret = None
