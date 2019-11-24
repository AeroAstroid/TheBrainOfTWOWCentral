from Config._links import LINKS

HELP = "Provides useful links to community-related projects or servers"
PERMS = 0
ALIASES = ["L"]
REQ = []

async def MAIN(message, args, level, perms):
	if level == 1:
		await message.channel.send("Include a link you want to see!")
		return
	
	if args[1].lower() == "list":
		await message.channel.send(f"Here's a list of link commands available:\n\n{grammar_list(LINKS.keys())}")
		return

	if args[1].upper() not in LINKS.keys():
		await message.channel.send("That link cannot be found.")
		return
	
	requested = args[1].upper()
	await message.channel.send(f"{LINKS[requested]['INFO']}\n\n**Link :** {LINKS[requested]['MAIN']}")
	return