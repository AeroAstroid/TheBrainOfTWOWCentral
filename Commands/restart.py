import asyncio, discord

HELP = "Restarts the bot, updating its code"
PERMS = 2
ALIASES = []
REQ = []

async def MAIN(message, args, level, perms):
	await message.channel.send("Restarting the bot.")
	print(f"Restarting bot on command by {message.author.name} // {message.created_at} UTC.\n\n")
	return [0]