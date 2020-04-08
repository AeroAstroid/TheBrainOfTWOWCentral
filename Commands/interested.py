def HELP(PREFIX):
	return {
		"COOLDOWN": 3,
		"MAIN": "Toggles whether or not you have the `Interested in the Bot` role",
		"FORMAT": "",
		"CHANNEL": 0,
		"USAGE": f"""Using `{PREFIX}interested` will add the `Interested in the Bot` to you, or remove it if you already 
		have it.""".replace("\n", "").replace("\t", "")
	}

PERMS = 0 # Member
ALIASES = ["I"]
REQ = ["MAIN_SERVER"]

async def MAIN(message, args, level, perms, SERVER, MAIN_SERVER):
	if SERVER["MAIN"] != MAIN_SERVER["MAIN"]:
		await message.channel.send(f"This command is not available for **{SERVER['MAIN'].name}.**")
		return
	
	person = SERVER["MAIN"].get_member(message.author.id)

	if MAIN_SERVER["INTERESTED"] in person.roles: # If they already have the role...
		await person.remove_roles(MAIN_SERVER["INTERESTED"]) # remove it.
		await message.channel.send(f"<@{message.author.id}>, you no longer have `Interested in the Bot`.")
		return
	
	# If they don't have the role yet...
	await person.add_roles(MAIN_SERVER["INTERESTED"]) # add it.
	await message.channel.send(f"**<@{message.author.id}>, you now have `Interested in the Bot`!**")
	return