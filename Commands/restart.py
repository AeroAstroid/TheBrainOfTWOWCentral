def HELP(PREFIX):
	return {
		"COOLDOWN": 10,
		"MAIN": "Restarts the bot. If it's running locally, updates the code automatically",
		"FORMAT": "",
		"CHANNEL": 2,
		"USAGE": f"""Using `{PREFIX}restart` will trigger a bot restart. 
		It'll report the time it took to restart once it's back up.""".replace("\n", "").replace("\t", "")
	}

PERMS = 3 # Developer
ALIASES = ["R"]
REQ = []

async def MAIN(message, args, level, perms, SERVER):
	await message.channel.send("Restarting the bot.")
	print(f"Restarting bot on command by {message.author.name} // {message.created_at} UTC.\n\n")
	return [0] # Flag to restart the bot