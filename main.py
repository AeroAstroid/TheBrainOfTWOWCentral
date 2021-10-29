import os
from dotenv import load_dotenv
import discord
from discord.ext import commands

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
async def run(ctx, message: str):
    """Run B* code."""
    await ctx.send(message)

load_dotenv()
bot.run(os.getenv("TOKEN"))
