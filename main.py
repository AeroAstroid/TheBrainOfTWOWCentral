import os
from dotenv import load_dotenv
import discord
from discord.ext import commands

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

@bot.command()
async def run(ctx, *, message):
    """Run B* code"""
    output = parseCode(message)
    await ctx.send(output)

@bot.command()
async def ping(ctx):
    """Pings the bot"""
    await ctx.send("pong")


load_dotenv()
bot.run(os.getenv("TOKEN"))
