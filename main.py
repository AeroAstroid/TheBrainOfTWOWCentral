import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
import datetime, time #uptime

from src.interpreter.parsing import parseCode

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="b/", description="B* bot!!", intents=intents)

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    global startTime # global variable to be used later for uptime
    startTime = time.time() # snapshot of time when listener sends on_ready

@bot.command()
async def run(ctx, *, message):
    """Run B* code"""
    output = parseCode(message)
    await ctx.send(output)

@bot.command()
async def ping(ctx):
    """Pings the bot"""
    await ctx.send("pong")

@bot.command()
async def uptime(ctx):
    """Responds with uptime."""
    uptime = str(datetime.timedelta(seconds=int(round(time.time()-startTime))))
    await ctx.send("Uptime: " + uptime)


load_dotenv()
bot.run(os.getenv("TOKEN"))
