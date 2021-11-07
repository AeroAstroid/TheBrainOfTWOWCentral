import datetime  # uptime
import os
import time

import discord
from discord.ext import commands
from dotenv import load_dotenv

# from src.database.s3 import setupDatabaseConnection, createTag
from src.database.s3 import createTag, getTag, infoTag, updateTag, isOwner, editTag, deleteTag
from src.interpreter.function_deco import setupFunctions
from src.interpreter.parsing import runCode

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="b/", description="B* bot!!", intents=intents)

load_dotenv()
setupFunctions()


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
async def tag(ctx, message):
    """Runs a B* tag"""
    tagObject = getTag(message)
    if tagObject is not None:
        code = tagObject["data"]
        output = runCode(code)
        await ctx.send(output)

        # If all goes well, then increment the use
        updateTag(message)
    else:
        await ctx.send(f"There's no program under the name `{message}`!")


@bot.command()
async def create(ctx, name, *, message):
    """Creates a B* tag with your code"""
    # try:
    createTag(ctx.author, name, message)
    await ctx.send("Tag created!")
    # except:
    #     await ctx.send("Tag creation failed")


@bot.command()
async def info(ctx, message):
    """Gives infomation and source code about a B* tag"""
    await ctx.send(infoTag(ctx, message))


@bot.command()
async def edit(ctx, name, *, message):
    """Edit one of your B* tags"""
    if isOwner(name, ctx.author.id):
        editTag(name, message)
        await ctx.send(f"Tag `{name}` edited!")
    else:
        await ctx.send("You aren't the owner of this tag!")


@bot.command()
async def delete(ctx, name):
    """Delete one of your B* tags"""
    if isOwner(name, ctx.author.id):
        deleteTag(name)
        await ctx.send(f"Tag `{name}` deleted!")
    else:
        await ctx.send("You aren't the owner of this tag!")


@bot.command()
async def ping(ctx):
    """Pings the bot"""
    await ctx.send("pong! " + str(round(bot.latency * 1000, 2)) + "ms")


@bot.command()
async def uptime(ctx):
    """Responds with uptime."""
    uptime = str(datetime.timedelta(seconds=int(round(time.time() - startTime))))
    await ctx.send("Uptime: " + uptime)


bot.run(os.getenv("TOKEN"))
