import random

def HELP(PREFIX):
	return {
		"COOLDOWN": 1,
		"MAIN": "Meme command",
		"FORMAT": "",
		"CHANNEL": 0,
		"USAGE": f"""Using `{PREFIX}tonguebattle` will kill God""".replace("\n", "").replace("\t", ""),
		"CATEGORY" : "Fun"
	}

PERMS = 0 # Non-members
ALIASES = []
REQ = []

async def MAIN(message, args, level, perms, SERVER):
	choice = random.choice(["won", "lost"])
	await message.channel.send(f"You {choice} the tongue battle.")
	return