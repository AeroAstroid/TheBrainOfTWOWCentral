import datetime  # uptime
import os
import time

import discord
from discord.ext import commands
from dotenv import load_dotenv

from src.interpreter.function_deco import setupFunctions
from src.interpreter.parsing import runCode

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="b/", description="B* bot!!", intents=intents)


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    global startTime  # global variable to be used later for uptime
    startTime = time.time()  # snapshot of time when listener sends on_ready


@bot.command()
async def run(ctx, *, message):
    """Run B* code"""
    output = runCode(message)
    await ctx.send(output)


@bot.command()
async def ping(ctx):
    """Pings the bot"""
    await ctx.send("pong! " + str(round(bot.latency * 1000, 2)) + "ms")


@bot.command()
async def uptime(ctx):
    """Responds with uptime."""
    uptime = str(datetime.timedelta(seconds=int(round(time.time() - startTime))))
    await ctx.send("Uptime: " + uptime)


load_dotenv()
setupFunctions()
bot.run(os.getenv("TOKEN"))
