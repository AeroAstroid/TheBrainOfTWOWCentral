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
		snowflake_list = []
		format_list = []
		if level > 1:
			for elem in args[1:]:
				try:
					snowflake_list.append(int(elem))
				except ValueError:
					mode = elem
					break
			if mode not in ["timestamp", "unix"]:
				mode = "timestamp"
		else:
			snowflake_list = [int(args[1])]
			mode = "timestamp"
		output = ""
		snowflake_list = snowflake_list[:2]
		for snowflake in snowflake_list:
			if snowflake > 18446744073709551615 or snowflake < 0:
				snowflake_list.remove(snowflake)
				continue
			snowflaketime = bin(snowflake)[2:].zfill(64)
			snowflaketime = snowflaketime[:42]
			snowflaketime = (int(snowflaketime, 2) + 1420070400000)/1000
			if mode == "timestamp":
				format_list.append(str(datetime.datetime.fromtimestamp(snowflaketime))[:-3] + " UTC")
			elif mode == "unix":
				format_list.append(str(snowflaketime))
		for i in range(len(snowflake_list)):
			output += message.channel.send(str(snowflake_list[i]) + " → **" + format_list[i] + "**")
			output += "\n"
		if len(snowflake_list) == 0:
			await message.channel.send("Invalid ID.")
			return
		await message.channel.send(output)
	return