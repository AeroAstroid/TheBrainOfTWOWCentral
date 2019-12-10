from Config._const import PREFIX, BOT_ROLE

HELP = {
	"MAIN": "Toggles whether or not you have the `Interested in the Bot` role",
	"FORMAT": "",
	"CHANNEL": 0,
	"USAGE": f"""Using `{PREFIX}interested` will add the `Interested in the Bot` to you, or remove it if you already 
	have it.""".replace("\n", "").replace("\t", "")
}

PERMS = 0 # Member
ALIASES = ["I"]
REQ = ["BOT_ROLE", "TWOW_CENTRAL"]

async def MAIN(message, args, level, perms, BOT_ROLE, TWOW_CENTRAL):
	person = TWOW_CENTRAL.get_member(message.author.id)

	if BOT_ROLE in person.roles:
		await person.remove_roles(BOT_ROLE)
		await message.channel.send(f"<@{message.author.id}>, you no longer have `Interested in the Bot`.")
		return
	
	await person.add_roles(BOT_ROLE)
	await message.channel.send(f"**<@{message.author.id}>, you now have `Interested in the Bot`!**")
	return