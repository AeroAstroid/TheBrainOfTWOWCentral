def HELP(PREFIX):
	return {
		"COOLDOWN": 1,
		"MAIN": "Displays the server's current member count",
		"FORMAT": "",
		"CHANNEL": 0,
		"USAGE": f"""Using `{PREFIX}membercount` will return the current member count of the server 
		it's used in.""".replace("\n", "").replace("\t", "")
	}

PERMS = 0 # Non-members
ALIASES = ["MEMBERS"]
REQ = []

async def MAIN(message, args, level, perms, SERVER):
	member_count = len(SERVER["MAIN"].members)
	await message.channel.send(f"We have **{member_count}** members.")
	return