import time

def HELP(PREFIX):
	return {
		"COOLDOWN": 10,
		"MAIN": "Reimports the commands, updating command code without needing to restart",
		"FORMAT": "",
		"CHANNEL": 2,
		"USAGE": f"""Using `{PREFIX}reimport` will trigger a command reimport. 
		It'll report the time it took to import the commands.""".replace("\n", "").replace("\t", ""),
		"CATEGORY" : "Developer"
	}

PERMS = 3 # Developer
ALIASES = []
REQ = []

async def MAIN(message, args, level, perms, SERVER):
	await message.channel.send("Reimporting commands...")
	print(f"Reimporting command files on command by {message.author.name} // {message.created_at} UTC.\n\n")
	return [3, time.time()] # Flag to reimport commands