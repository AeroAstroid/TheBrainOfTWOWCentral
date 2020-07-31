import discord, datetime

def HELP(PREFIX):
	return {
		"COOLDOWN": 1,
		"MAIN": "Finds the time corresponding to a Discord snowflake (ID).",
		"FORMAT": "[id]",
		"CHANNEL": 0,
		"USAGE": f"""Using `{PREFIX}idtime` will return the time 
		corresponding to the provided Discord snowflake.""".replace("\n", "").replace("\t", "")
	}

PERMS = 0 # Non-members
ALIASES = []
REQ = []

async def MAIN(message, args, level, perms, SERVER):
	if level == 1:
		await message.channel.send("Include the ID you would like to find the time of.")
	else:
		try:
			snowflake = int(args[1])
			if snowflake > 18446744073709551615 or snowflake < 0:
				await message.channel.send("Invalid ID.")
				return
			snowflake = bin(snowflake)[2:].zfill(64)
			snowflake = snowflake[:42]
			snowflake = (int(snowflake, 2) + 1420070400000)/1000
			timeformat = str(datetime.datetime.fromtimestamp(snowflake))[:-3]
			await message.channel.send(args[1] + " -> " + timeformat)
		except ValueError:
			await message.channel.send("Invalid ID.")
	return