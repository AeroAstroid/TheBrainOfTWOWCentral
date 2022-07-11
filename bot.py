import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix="b/", description="B* bot!!", intents=intents)

async def postrun(output, ctx):
    await ctx.send(output['main'])
    try:
        await ctx.author.dm_channel.send(output['pm'])
    except:
        await ctx.author.create_dm()
        await ctx.author.dm_channel.send(output['pm'])
